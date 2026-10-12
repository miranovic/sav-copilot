"""
Pipeline Module

This module orchestrates the complete analysis pipeline for SAV Copilot.
It coordinates all components to analyze a reclamation and return a complete result.

"""

import logging
import time
from typing import Any, Dict, Optional

from sav_copilot.trainer import ModelTrainer
from sav_copilot.predictor import Predictor
from sav_copilot.quality_analyzer import InputQualityAnalyzer
from sav_copilot.warranty_engine import WarrantyEngine
from sav_copilot.complexity_scorer import ComplexityScorer
from sav_copilot.message_generator import MessageGenerator

from config import (
    MODELS_DIR,
    MIN_DESCRIPTION_LENGTH,
    MIN_MEANINGFUL_WORDS
)

logger = logging.getLogger(__name__)


class AnalysisResult:
    """
    Complete analysis result containing all components.

    This class encapsulates the results from all analysis components:
    - Predictions with confidence scores
    - Input quality assessment
    - Warranty evaluation
    - Complexity score and priority
    - Generated customer message
    - Processing time
    """

    def __init__(
        self,
        reclamation: Dict[str, Any],
        predictions: Dict[str, Any],
        quality: Dict[str, Any],
        warranty: Dict[str, Any],
        complexity: Dict[str, Any],
        message: Optional[str],
        processing_time: float
    ):
        """
        Initialize AnalysisResult.

        Args:
            reclamation: Original reclamation data
            predictions: Prediction results from Predictor
            quality: Quality assessment from InputQualityAnalyzer
            warranty: Warranty evaluation from WarrantyEngine
            complexity: Complexity score from ComplexityScorer
            message: Generated customer message (if applicable)
            processing_time: Total processing time in seconds
        """
        self.reclamation = reclamation
        self.predictions = predictions
        self.quality = quality
        self.warranty = warranty
        self.complexity = complexity
        self.message = message
        self.processing_time = processing_time

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert AnalysisResult to dictionary format.

        Returns:
            Dictionary representation of the analysis result
        """
        return {
            "reclamation": self.reclamation,
            "predictions": self.predictions,
            "quality": self.quality,
            "warranty": self.warranty,
            "complexity": self.complexity,
            "message": self.message,
            "processing_time": self.processing_time
        }


def analyze_reclamation(
    reclamation: Dict[str, Any],
    trainer: Optional[ModelTrainer] = None,
    models_dir: str = MODELS_DIR
) -> AnalysisResult:
    """
    Orchestrate complete analysis of a reclamation.


    This function:
    1. Loads models if available, otherwise triggers training (if trainer provided)
    2. Runs predictions using Predictor
    3. Assesses input quality using InputQualityAnalyzer
    4. Evaluates warranty using WarrantyEngine
    5. Calculates complexity using ComplexityScorer
    6. Generates message using MessageGenerator
    7. Measures and logs processing time
    8. Returns complete AnalysisResult with all components

    Non-critical component errors are handled gracefully with fallback values.

    Args:
        reclamation: Dictionary containing reclamation data with keys:
            - 'description': Complaint text (required)
            - 'attachments': List of attachment filenames (optional)
            - Other metadata fields (optional)
        trainer: Optional ModelTrainer instance. If None, creates new trainer
            and attempts to load models from disk.
        models_dir: Directory containing saved models (default: from config)

    Returns:
        AnalysisResult containing all analysis components

    Raises:
        ValueError: If reclamation is invalid or models cannot be loaded/trained
    """
    start_time = time.time()
    logger.info("Starting reclamation analysis pipeline")

    # Validate input
    if not reclamation or not isinstance(reclamation, dict):
        raise ValueError("Invalid reclamation: must be a non-empty dictionary")

    description = reclamation.get('description', '')
    if not description or not isinstance(description, str):
        raise ValueError(
            "Invalid reclamation: 'description' field is required and must be a string"
        )

    # Step 1: Load or initialize models
    logger.info("Step 1: Loading models")
    if trainer is None:
        trainer = ModelTrainer(models_dir=models_dir)
        models_loaded = trainer.load_models()

        if not models_loaded:
            error_msg = (
                "No trained models found and no training data provided. "
                "Please train models first using train_models.py"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(
            f"Loaded {len(trainer.vectorizers)} model(s) from {models_dir}")
    else:
        # Check if trainer has models loaded
        if not trainer.vectorizers or not trainer.classifiers:
            models_loaded = trainer.load_models()
            if not models_loaded:
                error_msg = (
                    "Trainer has no models loaded and could not load from disk"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

        logger.info(
            f"Using provided trainer with {len(trainer.vectorizers)} model(s)")

    # Step 2: Run predictions
    logger.info("Step 2: Running predictions")
    try:
        predictor = Predictor(trainer)
        predictions = predictor.predict_all(description)
        logger.info("Predictions completed successfully")
    except Exception as e:
        logger.error(f"Error during prediction: {e}", exc_info=True)
        # Provide fallback predictions
        predictions = {
            "litige_type": {"prediction": "unknown", "confidence": 0.0, "available": False},
            "responsibility": {"prediction": "unknown", "confidence": 0.0, "available": False},
            "product_detail": {"prediction": "unknown", "confidence": 0.0, "available": False},
            "solution": {"prediction": "unknown", "confidence": 0.0, "available": False, "top_3": []}
        }
        logger.warning("Using fallback predictions due to error")

    # Step 3: Assess input quality
    logger.info("Step 3: Assessing input quality")
    try:
        quality_analyzer = InputQualityAnalyzer(
            min_description_length=MIN_DESCRIPTION_LENGTH,
            min_meaningful_words=MIN_MEANINGFUL_WORDS
        )
        quality = quality_analyzer.analyze(reclamation)
        logger.info(
            f"Quality assessment completed: status={quality['status']}")
    except Exception as e:
        logger.error(f"Error during quality assessment: {e}", exc_info=True)
        # Provide fallback quality assessment
        quality = {
            "status": "usable",
            "issues": [],
            "details": {
                "description_length": len(description),
                "attachment_count": len(reclamation.get('attachments', [])),
                "meaningful_word_count": 0
            }
        }
        logger.warning("Using fallback quality assessment due to error")

    # Step 4: Evaluate warranty
    logger.info("Step 4: Evaluating warranty eligibility")
    try:
        warranty_engine = WarrantyEngine()
        product_type = reclamation.get('product_type')
        warranty = warranty_engine.evaluate(description, product_type)
        logger.info(
            f"Warranty evaluation completed: status={warranty['status']}")
    except Exception as e:
        logger.error(f"Error during warranty evaluation: {e}", exc_info=True)
        # Provide fallback warranty evaluation
        warranty = {
            "status": "incertaine",
            "reasons": ["Erreur lors de l'évaluation de la garantie"],
            "matched_patterns": {},
            "disclaimer": "Cette évaluation est indicative et ne constitue pas une décision légale."
        }
        logger.warning("Using fallback warranty evaluation due to error")

    # Step 5: Calculate complexity
    logger.info("Step 5: Calculating complexity score")
    try:
        complexity_scorer = ComplexityScorer()
        analysis_result_for_complexity = {
            "quality": quality,
            "predictions": predictions,
            "warranty": warranty
        }
        complexity = complexity_scorer.calculate(
            analysis_result_for_complexity)
        logger.info(
            f"Complexity calculation completed: score={complexity['score']}, "
            f"level={complexity['level']}"
        )
    except Exception as e:
        logger.error(
            f"Error during complexity calculation: {e}", exc_info=True)
        # Provide fallback complexity score
        complexity = {
            "score": 2,
            "level": "standard",
            "priority": "standard_review",
            "breakdown": {
                "data_quality": 0,
                "prediction_confidence": 0,
                "warranty_uncertainty": 2,
                "clarity_bonus": 0
            }
        }
        logger.warning("Using fallback complexity score due to error")

    # Step 6: Generate customer message
    logger.info("Step 6: Generating customer message")
    try:
        message_generator = MessageGenerator()
        analysis_result_for_message = {
            "quality": quality,
            "warranty": warranty,
            "complexity": complexity,
            "predictions": predictions
        }
        message = message_generator.generate(analysis_result_for_message)
        if message:
            logger.info("Customer message generated successfully")
        else:
            logger.info(
                "No automatic message generated (manual review required)")
    except Exception as e:
        logger.error(f"Error during message generation: {e}", exc_info=True)
        message = None
        logger.warning("No message generated due to error")

    # Calculate processing time
    processing_time = time.time() - start_time
    logger.info(f"Pipeline completed in {processing_time:.3f} seconds")

    # Create and return AnalysisResult
    result = AnalysisResult(
        reclamation=reclamation,
        predictions=predictions,
        quality=quality,
        warranty=warranty,
        complexity=complexity,
        message=message,
        processing_time=processing_time
    )

    logger.info("Analysis pipeline completed successfully")
    return result
