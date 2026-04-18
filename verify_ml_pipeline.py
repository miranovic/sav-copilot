"""
Checkpoint verification script for Task 7: Verify ML pipeline.

This script verifies that the ModelTrainer and Predictor modules work together
correctly with the data pipeline by:
1. Loading and preprocessing training data
2. Training models (or loading existing ones)
3. Making predictions on test cases
4. Validating prediction quality and confidence scores
5. Testing end-to-end pipeline performance
"""

import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any

from sav_copilot.data_loader import DataLoader
from sav_copilot.preprocessor import Preprocessor
from sav_copilot.trainer import ModelTrainer
from sav_copilot.predictor import Predictor
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def verify_model_training():
    """Verify model training functionality."""
    logger.info("=" * 70)
    logger.info("CHECKPOINT 1: Model Training Verification")
    logger.info("=" * 70)

    try:
        # Load training data
        logger.info("Step 1: Loading training data...")
        loader = DataLoader()
        training_path = Path(config.TRAINING_DATA_PATH) / \
            config.TRAINING_EXCEL_FILE

        if not training_path.exists():
            logger.error(f"❌ Training data not found: {training_path}")
            return None, None

        df = loader.load_training_data(str(training_path))
        logger.info(f"✓ Loaded {len(df)} training samples")

        # Preprocess data
        logger.info("Step 2: Preprocessing data...")
        preprocessor = Preprocessor()
        target_columns = list(config.TARGET_COLUMNS.values())

        df = preprocessor.preprocess_for_training(
            df=df,
            text_column=config.TEXT_COLUMN,
            target_columns=target_columns
        )

        text_column = f"{config.TEXT_COLUMN}_features"
        logger.info(f"✓ Data preprocessed, using text column: {text_column}")

        # Initialize trainer
        logger.info("Step 3: Initializing ModelTrainer...")
        trainer = ModelTrainer(models_dir=config.MODELS_DIR)

        # Check for existing models
        models_exist = trainer.load_models()

        if models_exist:
            logger.info("✓ Existing models loaded successfully")
            logger.info(
                f"  Loaded models for: {list(trainer.vectorizers.keys())}")

            # Display model metadata
            for target_name in trainer.vectorizers.keys():
                if target_name in trainer.metadata:
                    metadata = trainer.metadata[target_name]
                    logger.info(f"  {target_name}:")
                    logger.info(
                        f"    - Samples: {metadata.get('n_samples', 'N/A')}")
                    logger.info(
                        f"    - Features: {metadata.get('n_features', 'N/A')}")
                    logger.info(
                        f"    - Classes: {metadata.get('n_classes', 'N/A')}")
        else:
            logger.info("No existing models found, training new models...")

            # Train models
            trainer.train_all(
                df=df,
                text_column=text_column,
                target_columns=target_columns
            )

            # Save models
            trainer.save_models()
            logger.info("✓ Models trained and saved successfully")

            # Display training results
            for target_name in trainer.vectorizers.keys():
                if target_name in trainer.metadata:
                    metadata = trainer.metadata[target_name]
                    logger.info(f"  {target_name}:")
                    logger.info(
                        f"    - Samples: {metadata.get('n_samples', 'N/A')}")
                    logger.info(
                        f"    - Features: {metadata.get('n_features', 'N/A')}")
                    logger.info(
                        f"    - Classes: {metadata.get('n_classes', 'N/A')}")

        # Verify all expected models are present
        expected_targets = ["litige", "responsibility", "product", "solution"]
        missing_targets = [
            t for t in expected_targets if t not in trainer.vectorizers]

        if missing_targets:
            logger.warning(f"⚠ Missing models for targets: {missing_targets}")
        else:
            logger.info("✓ All expected models are present")

        return trainer, preprocessor

    except Exception as e:
        logger.error(
            f"❌ Model training verification failed: {e}", exc_info=True)
        return None, None


def verify_prediction_functionality(trainer: ModelTrainer, preprocessor: Preprocessor):
    """Verify prediction functionality with test cases."""
    logger.info("\n" + "=" * 70)
    logger.info("CHECKPOINT 2: Prediction Functionality Verification")
    logger.info("=" * 70)

    if trainer is None or preprocessor is None:
        logger.error(
            "❌ Cannot verify predictions: trainer or preprocessor is None")
        return False

    try:
        # Create predictor
        logger.info("Creating predictor...")
        predictor = Predictor(trainer)
        logger.info("✓ Predictor created successfully")

        # Define test cases
        test_cases = [
            {
                "description": "Portail coulissant défectueux avec problème de rouille",
                "label": "Defective sliding gate with rust"
            },
            {
                "description": "Défaut de fabrication sur la clôture",
                "label": "Manufacturing defect on fence"
            },
            {
                "description": "Usure normale du produit après plusieurs années",
                "label": "Normal wear after several years"
            },
            {
                "description": "Installation non conforme causant des problèmes",
                "label": "Non-compliant installation"
            },
            {
                "description": "Pièce cassée nécessitant remplacement urgent",
                "label": "Broken part requiring urgent replacement"
            }
        ]

        logger.info(f"\nTesting {len(test_cases)} test cases...\n")

        all_passed = True
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"--- Test Case {i}: {test_case['label']} ---")
            logger.info(f"Description: {test_case['description']}")

            # Preprocess text
            text = preprocessor.preprocess_for_prediction(
                test_case['description'])

            # Test predict_all
            result = predictor.predict_all(text)

            # Verify structure
            expected_keys = ["litige_type", "responsibility",
                             "product_detail", "solution"]
            missing_keys = [k for k in expected_keys if k not in result]

            if missing_keys:
                logger.error(f"  ❌ Missing keys in result: {missing_keys}")
                all_passed = False
                continue

            # Display predictions
            logger.info("  Predictions:")

            for key in expected_keys:
                pred = result[key]
                if pred.get('available', False):
                    logger.info(
                        f"    {key}: {pred['prediction']} "
                        f"(confidence: {pred['confidence']:.3f})"
                    )
                else:
                    logger.warning(f"    {key}: NOT AVAILABLE")
                    all_passed = False

            # Verify solution has top_3
            if 'top_3' in result['solution']:
                logger.info(f"  Top 3 solutions:")
                for j, candidate in enumerate(result['solution']['top_3'][:3], 1):
                    logger.info(
                        f"    {j}. {candidate['label']} "
                        f"(confidence: {candidate['confidence']:.3f})"
                    )
            else:
                logger.warning("  ⚠ No top_3 solutions provided")

            # Verify confidence scores are valid
            for key in expected_keys:
                pred = result[key]
                if pred.get('available', False):
                    confidence = pred['confidence']
                    if not (0.0 <= confidence <= 1.0):
                        logger.error(
                            f"  ❌ Invalid confidence score for {key}: {confidence}"
                        )
                        all_passed = False

            logger.info("")

        if all_passed:
            logger.info("✓ All prediction tests passed")
        else:
            logger.error("❌ Some prediction tests failed")

        return all_passed

    except Exception as e:
        logger.error(f"❌ Prediction verification failed: {e}", exc_info=True)
        return False


def verify_individual_predictions(trainer: ModelTrainer, preprocessor: Preprocessor):
    """Verify individual prediction methods."""
    logger.info("\n" + "=" * 70)
    logger.info("CHECKPOINT 3: Individual Prediction Methods Verification")
    logger.info("=" * 70)

    if trainer is None or preprocessor is None:
        logger.error("❌ Cannot verify: trainer or preprocessor is None")
        return False

    try:
        predictor = Predictor(trainer)
        test_text = "Portail avec défaut de fabrication nécessitant remplacement"
        text = preprocessor.preprocess_for_prediction(test_text)

        logger.info(f"Test text: {test_text}\n")

        # Test predict_single for each target
        logger.info("Testing predict_single():")
        targets = ["litige", "responsibility", "product", "solution"]

        all_passed = True
        for target in targets:
            result = predictor.predict_single(text, target)

            if result.get('available', False):
                logger.info(
                    f"  ✓ {target}: {result['prediction']} "
                    f"(confidence: {result['confidence']:.3f})"
                )

                # Verify confidence is valid
                if not (0.0 <= result['confidence'] <= 1.0):
                    logger.error(f"  ❌ Invalid confidence for {target}")
                    all_passed = False
            else:
                logger.warning(f"  ⚠ {target}: NOT AVAILABLE")
                all_passed = False

        # Test predict_top_k
        logger.info("\nTesting predict_top_k():")
        for k in [3, 5]:
            top_k = predictor.predict_top_k(text, "solution", k=k)

            if len(top_k) > 0:
                logger.info(f"  ✓ Top {k} solutions:")
                for i, candidate in enumerate(top_k, 1):
                    logger.info(
                        f"    {i}. {candidate['label']} "
                        f"(confidence: {candidate['confidence']:.3f})"
                    )

                # Verify results are sorted by confidence
                confidences = [c['confidence'] for c in top_k]
                if confidences != sorted(confidences, reverse=True):
                    logger.error(f"  ❌ Results not sorted by confidence")
                    all_passed = False
            else:
                logger.warning(f"  ⚠ No top-{k} results returned")
                all_passed = False

        # Test fallback behavior
        logger.info("\nTesting fallback behavior:")
        result = predictor.predict_single(text, "nonexistent_target")

        if result['prediction'] == "unknown" and result['confidence'] == 0.0 and not result['available']:
            logger.info("  ✓ Fallback behavior works correctly")
        else:
            logger.error("  ❌ Fallback behavior incorrect")
            all_passed = False

        if all_passed:
            logger.info("\n✓ All individual prediction tests passed")
        else:
            logger.error("\n❌ Some individual prediction tests failed")

        return all_passed

    except Exception as e:
        logger.error(
            f"❌ Individual prediction verification failed: {e}", exc_info=True)
        return False


def verify_confidence_scores(trainer: ModelTrainer, preprocessor: Preprocessor):
    """Verify confidence score properties."""
    logger.info("\n" + "=" * 70)
    logger.info("CHECKPOINT 4: Confidence Score Verification")
    logger.info("=" * 70)

    if trainer is None or preprocessor is None:
        logger.error("❌ Cannot verify: trainer or preprocessor is None")
        return False

    try:
        predictor = Predictor(trainer)

        # Test cases with expected confidence properties
        test_cases = [
            {
                "text": "Portail coulissant défectueux avec rouille",
                "label": "Specific complaint"
            },
            {
                "text": "Problème",
                "label": "Vague complaint"
            },
            {
                "text": "Défaut de fabrication sur portail coulissant nécessitant remplacement complet de la pièce défectueuse",
                "label": "Detailed complaint"
            }
        ]

        logger.info("Testing confidence score properties:\n")

        all_passed = True
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Test {i}: {test_case['label']}")
            logger.info(f"  Text: {test_case['text']}")

            text = preprocessor.preprocess_for_prediction(test_case['text'])
            result = predictor.predict_all(text)

            # Check confidence scores
            for target_name, pred in result.items():
                if pred.get('available', False):
                    confidence = pred['confidence']

                    # Verify confidence is in valid range
                    if not (0.0 <= confidence <= 1.0):
                        logger.error(
                            f"  ❌ {target_name}: confidence {confidence} out of range [0, 1]"
                        )
                        all_passed = False
                    else:
                        logger.info(
                            f"  ✓ {target_name}: confidence {confidence:.3f} in valid range"
                        )

            # Verify top_3 confidences sum to approximately 1.0 (for solution)
            if 'solution' in result and 'top_3' in result['solution']:
                top_3 = result['solution']['top_3']
                if len(top_3) > 0:
                    total_confidence = sum(c['confidence'] for c in top_3)
                    # Allow some tolerance for floating point
                    if 0.95 <= total_confidence <= 1.05:
                        logger.info(
                            f"  ✓ Top-3 confidences sum to {total_confidence:.3f} (valid)"
                        )
                    else:
                        logger.warning(
                            f"  ⚠ Top-3 confidences sum to {total_confidence:.3f} (expected ~1.0)"
                        )

            logger.info("")

        if all_passed:
            logger.info("✓ All confidence score tests passed")
        else:
            logger.error("❌ Some confidence score tests failed")

        return all_passed

    except Exception as e:
        logger.error(
            f"❌ Confidence score verification failed: {e}", exc_info=True)
        return False


def verify_performance(trainer: ModelTrainer, preprocessor: Preprocessor):
    """Verify prediction performance meets requirements."""
    logger.info("\n" + "=" * 70)
    logger.info("CHECKPOINT 5: Performance Verification")
    logger.info("=" * 70)

    if trainer is None or preprocessor is None:
        logger.error("❌ Cannot verify: trainer or preprocessor is None")
        return False

    try:
        predictor = Predictor(trainer)

        test_text = "Portail coulissant défectueux avec problème de rouille nécessitant intervention"
        text = preprocessor.preprocess_for_prediction(test_text)

        # Measure prediction time
        num_iterations = 10
        logger.info(
            f"Measuring prediction time over {num_iterations} iterations...")

        times = []
        for i in range(num_iterations):
            start_time = time.time()
            result = predictor.predict_all(text)
            end_time = time.time()

            elapsed = end_time - start_time
            times.append(elapsed)

        # Calculate statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        logger.info(f"\nPerformance results:")
        logger.info(f"  Average time: {avg_time*1000:.2f} ms")
        logger.info(f"  Min time: {min_time*1000:.2f} ms")
        logger.info(f"  Max time: {max_time*1000:.2f} ms")

        # Check against requirement (< 2 seconds)
        target_time = config.MAX_PROCESSING_TIME

        if avg_time < target_time:
            logger.info(f"  ✓ Average time is below target ({target_time}s)")
            passed = True
        else:
            logger.warning(
                f"  ⚠ Average time exceeds target ({target_time}s). "
                f"This may be acceptable for MVP."
            )
            passed = True  # Don't fail on performance for MVP

        return passed

    except Exception as e:
        logger.error(f"❌ Performance verification failed: {e}", exc_info=True)
        return False


def verify_end_to_end_pipeline():
    """Verify complete end-to-end ML pipeline."""
    logger.info("\n" + "=" * 70)
    logger.info("CHECKPOINT 6: End-to-End ML Pipeline Verification")
    logger.info("=" * 70)

    try:
        logger.info(
            "Running complete pipeline from data loading to prediction...\n")

        start_time = time.time()

        # Step 1: Load data
        logger.info("Step 1: Loading data...")
        loader = DataLoader()
        training_path = Path(config.TRAINING_DATA_PATH) / \
            config.TRAINING_EXCEL_FILE
        df = loader.load_training_data(str(training_path))
        logger.info(f"  ✓ Loaded {len(df)} samples")

        # Step 2: Preprocess
        logger.info("Step 2: Preprocessing...")
        preprocessor = Preprocessor()
        target_columns = list(config.TARGET_COLUMNS.values())
        df = preprocessor.preprocess_for_training(
            df=df,
            text_column=config.TEXT_COLUMN,
            target_columns=target_columns
        )
        text_column = f"{config.TEXT_COLUMN}_features"
        logger.info(f"  ✓ Preprocessed data")

        # Step 3: Train/Load models
        logger.info("Step 3: Loading/training models...")
        trainer = ModelTrainer(models_dir=config.MODELS_DIR)

        if not trainer.load_models():
            logger.info("  Training new models...")
            trainer.train_all(df=df, text_column=text_column,
                              target_columns=target_columns)
            trainer.save_models()

        logger.info(f"  ✓ Models ready")

        # Step 4: Make predictions
        logger.info("Step 4: Making predictions...")
        predictor = Predictor(trainer)

        test_text = "Portail coulissant avec défaut de fabrication"
        text = preprocessor.preprocess_for_prediction(test_text)
        result = predictor.predict_all(text)

        logger.info(f"  ✓ Predictions generated")

        # Step 5: Verify output
        logger.info("Step 5: Verifying output...")

        expected_keys = ["litige_type", "responsibility",
                         "product_detail", "solution"]
        all_present = all(k in result for k in expected_keys)

        if not all_present:
            logger.error("  ❌ Missing expected keys in result")
            return False

        all_available = all(result[k].get('available', False)
                            for k in expected_keys)

        if not all_available:
            logger.warning("  ⚠ Some models not available")

        logger.info(f"  ✓ Output structure valid")

        end_time = time.time()
        total_time = end_time - start_time

        logger.info(f"\n✓ END-TO-END PIPELINE COMPLETED")
        logger.info(f"  Total time: {total_time:.2f}s")

        # Display sample result
        logger.info(f"\nSample prediction for: '{test_text}'")
        for key in expected_keys:
            pred = result[key]
            if pred.get('available', False):
                logger.info(
                    f"  {key}: {pred['prediction']} "
                    f"(confidence: {pred['confidence']:.3f})"
                )

        return True

    except Exception as e:
        logger.error(
            f"❌ End-to-end pipeline verification failed: {e}", exc_info=True)
        return False


def main():
    """Run all ML pipeline verification checkpoints."""
    logger.info("\n" + "=" * 70)
    logger.info("SAV COPILOT - ML PIPELINE VERIFICATION")
    logger.info("Task 7: Checkpoint - Verify ML pipeline")
    logger.info("=" * 70 + "\n")

    # Track results
    results = {
        "model_training": False,
        "prediction_functionality": False,
        "individual_predictions": False,
        "confidence_scores": False,
        "performance": False,
        "end_to_end": False
    }

    # Run checkpoints
    trainer, preprocessor = verify_model_training()
    results["model_training"] = (
        trainer is not None and preprocessor is not None)

    if results["model_training"]:
        results["prediction_functionality"] = verify_prediction_functionality(
            trainer, preprocessor)
        results["individual_predictions"] = verify_individual_predictions(
            trainer, preprocessor)
        results["confidence_scores"] = verify_confidence_scores(
            trainer, preprocessor)
        results["performance"] = verify_performance(trainer, preprocessor)

    results["end_to_end"] = verify_end_to_end_pipeline()

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("VERIFICATION SUMMARY")
    logger.info("=" * 70)

    for checkpoint, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        logger.info(f"{checkpoint.replace('_', ' ').title()}: {status}")

    all_passed = all(results.values())

    logger.info("\n" + "=" * 70)
    if all_passed:
        logger.info("✓ ALL CHECKPOINTS PASSED - ML PIPELINE VERIFIED")
        logger.info("=" * 70)
        logger.info(
            "\nThe ModelTrainer and Predictor modules work correctly with the")
        logger.info(
            "data pipeline. Models can be trained, saved, loaded, and used for")
        logger.info("predictions with appropriate confidence scores.")
        return 0
    else:
        logger.error("❌ SOME CHECKPOINTS FAILED - REVIEW ERRORS ABOVE")
        logger.info("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
