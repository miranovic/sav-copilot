"""
Unit tests for the pipeline module.

Tests the complete analysis orchestration including:
- Model loading
- Prediction execution
- Quality assessment
- Warranty evaluation
- Complexity scoring
- Message generation
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sav_copilot.pipeline import analyze_reclamation, AnalysisResult
from sav_copilot.trainer import ModelTrainer


class TestAnalysisResult:
    """Test the AnalysisResult class."""

    def test_analysis_result_initialization(self):
        """Test AnalysisResult can be initialized with all components."""
        reclamation = {"description": "Test", "attachments": []}
        predictions = {"litige_type": {
            "prediction": "Test", "confidence": 0.8}}
        quality = {"status": "usable", "issues": []}
        warranty = {"status": "incertaine", "reasons": []}
        complexity = {"score": 2, "level": "standard"}
        message = "Test message"
        processing_time = 1.5

        result = AnalysisResult(
            reclamation=reclamation,
            predictions=predictions,
            quality=quality,
            warranty=warranty,
            complexity=complexity,
            message=message,
            processing_time=processing_time
        )

        assert result.reclamation == reclamation
        assert result.predictions == predictions
        assert result.quality == quality
        assert result.warranty == warranty
        assert result.complexity == complexity
        assert result.message == message
        assert result.processing_time == processing_time

    def test_analysis_result_to_dict(self):
        """Test AnalysisResult can be converted to dictionary."""
        reclamation = {"description": "Test"}
        predictions = {"litige_type": {
            "prediction": "Test", "confidence": 0.8}}
        quality = {"status": "usable"}
        warranty = {"status": "incertaine"}
        complexity = {"score": 2}
        message = "Test message"
        processing_time = 1.5

        result = AnalysisResult(
            reclamation=reclamation,
            predictions=predictions,
            quality=quality,
            warranty=warranty,
            complexity=complexity,
            message=message,
            processing_time=processing_time
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["reclamation"] == reclamation
        assert result_dict["predictions"] == predictions
        assert result_dict["quality"] == quality
        assert result_dict["warranty"] == warranty
        assert result_dict["complexity"] == complexity
        assert result_dict["message"] == message
        assert result_dict["processing_time"] == processing_time


class TestAnalyzeReclamation:
    """Test the analyze_reclamation function."""

    def test_analyze_reclamation_invalid_input_none(self):
        """Test analyze_reclamation raises error for None input."""
        with pytest.raises(ValueError, match="Invalid reclamation"):
            analyze_reclamation(None)

    def test_analyze_reclamation_invalid_input_not_dict(self):
        """Test analyze_reclamation raises error for non-dict input."""
        with pytest.raises(ValueError, match="Invalid reclamation"):
            analyze_reclamation("not a dict")

    def test_analyze_reclamation_missing_description(self):
        """Test analyze_reclamation raises error when description is missing."""
        reclamation = {"attachments": []}
        with pytest.raises(ValueError, match="'description' field is required"):
            analyze_reclamation(reclamation)

    def test_analyze_reclamation_empty_description(self):
        """Test analyze_reclamation raises error when description is empty."""
        reclamation = {"description": ""}
        with pytest.raises(ValueError, match="'description' field is required"):
            analyze_reclamation(reclamation)

    def test_analyze_reclamation_no_models_no_trainer(self):
        """Test analyze_reclamation raises error when no models available."""
        reclamation = {
            "description": "Portail ne ferme pas correctement",
            "attachments": ["photo1.jpg"]
        }

        # Mock ModelTrainer to simulate no models found
        with patch('sav_copilot.pipeline.ModelTrainer') as MockTrainer:
            mock_trainer_instance = Mock()
            mock_trainer_instance.load_models.return_value = False
            mock_trainer_instance.vectorizers = {}
            mock_trainer_instance.classifiers = {}
            MockTrainer.return_value = mock_trainer_instance

            with pytest.raises(ValueError, match="No trained models found"):
                analyze_reclamation(reclamation)

    @patch('sav_copilot.pipeline.Predictor')
    @patch('sav_copilot.pipeline.InputQualityAnalyzer')
    @patch('sav_copilot.pipeline.WarrantyEngine')
    @patch('sav_copilot.pipeline.ComplexityScorer')
    @patch('sav_copilot.pipeline.MessageGenerator')
    def test_analyze_reclamation_complete_pipeline(
        self,
        MockMessageGenerator,
        MockComplexityScorer,
        MockWarrantyEngine,
        MockQualityAnalyzer,
        MockPredictor
    ):
        """Test analyze_reclamation executes complete pipeline successfully."""
        # Setup reclamation
        reclamation = {
            "description": "Le portail coulissant ne ferme pas correctement depuis 2 semaines",
            "attachments": ["photo1.jpg", "photo2.jpg"]
        }

        # Mock trainer with loaded models
        mock_trainer = Mock(spec=ModelTrainer)
        mock_trainer.vectorizers = {"litige": Mock(), "responsibility": Mock()}
        mock_trainer.classifiers = {"litige": Mock(), "responsibility": Mock()}

        # Mock Predictor
        mock_predictor = Mock()
        mock_predictor.predict_all.return_value = {
            "litige_type": {"prediction": "Défaut de fabrication", "confidence": 0.85, "available": True},
            "responsibility": {"prediction": "Fabricant", "confidence": 0.78, "available": True},
            "product_detail": {"prediction": "Portail coulissant", "confidence": 0.92, "available": True},
            "solution": {
                "prediction": "Remplacement pièce",
                "confidence": 0.81,
                "available": True,
                "top_3": [
                    {"label": "Remplacement pièce", "confidence": 0.81},
                    {"label": "Réparation sur site", "confidence": 0.12}
                ]
            }
        }
        MockPredictor.return_value = mock_predictor

        # Mock InputQualityAnalyzer
        mock_quality_analyzer = Mock()
        mock_quality_analyzer.analyze.return_value = {
            "status": "usable",
            "issues": [],
            "details": {
                "description_length": 65,
                "attachment_count": 2,
                "meaningful_word_count": 10
            }
        }
        MockQualityAnalyzer.return_value = mock_quality_analyzer

        # Mock WarrantyEngine
        mock_warranty_engine = Mock()
        mock_warranty_engine.evaluate.return_value = {
            "status": "incertaine",
            "reasons": ["Aucun motif d'exclusion évident détecté"],
            "matched_patterns": {},
            "disclaimer": "Cette évaluation est indicative."
        }
        MockWarrantyEngine.return_value = mock_warranty_engine

        # Mock ComplexityScorer
        mock_complexity_scorer = Mock()
        mock_complexity_scorer.calculate.return_value = {
            "score": 1,
            "level": "rapide",
            "priority": "quick_win",
            "breakdown": {
                "data_quality": 0,
                "prediction_confidence": 0,
                "warranty_uncertainty": 2,
                "clarity_bonus": -1
            }
        }
        MockComplexityScorer.return_value = mock_complexity_scorer

        # Mock MessageGenerator
        mock_message_generator = Mock()
        mock_message_generator.generate.return_value = "Bonjour, nous avons bien reçu votre réclamation..."
        MockMessageGenerator.return_value = mock_message_generator

        # Execute pipeline
        result = analyze_reclamation(reclamation, trainer=mock_trainer)

        # Verify result
        assert isinstance(result, AnalysisResult)
        assert result.reclamation == reclamation
        assert result.predictions["litige_type"]["prediction"] == "Défaut de fabrication"
        assert result.quality["status"] == "usable"
        assert result.warranty["status"] == "incertaine"
        assert result.complexity["score"] == 1
        assert result.message is not None
        assert result.processing_time >= 0

        # Verify all components were called
        mock_predictor.predict_all.assert_called_once()
        mock_quality_analyzer.analyze.assert_called_once()
        mock_warranty_engine.evaluate.assert_called_once()
        mock_complexity_scorer.calculate.assert_called_once()
        mock_message_generator.generate.assert_called_once()

    @patch('sav_copilot.pipeline.Predictor')
    @patch('sav_copilot.pipeline.InputQualityAnalyzer')
    @patch('sav_copilot.pipeline.WarrantyEngine')
    @patch('sav_copilot.pipeline.ComplexityScorer')
    @patch('sav_copilot.pipeline.MessageGenerator')
    def test_analyze_reclamation_prediction_error_fallback(
        self,
        MockMessageGenerator,
        MockComplexityScorer,
        MockWarrantyEngine,
        MockQualityAnalyzer,
        MockPredictor
    ):
        """Test analyze_reclamation handles prediction errors gracefully."""
        reclamation = {
            "description": "Problème avec le portail",
            "attachments": []
        }

        mock_trainer = Mock(spec=ModelTrainer)
        mock_trainer.vectorizers = {"litige": Mock()}
        mock_trainer.classifiers = {"litige": Mock()}

        # Mock Predictor to raise error
        mock_predictor = Mock()
        mock_predictor.predict_all.side_effect = Exception("Prediction failed")
        MockPredictor.return_value = mock_predictor

        # Mock other components to succeed
        MockQualityAnalyzer.return_value.analyze.return_value = {
            "status": "usable", "issues": [], "details": {}
        }
        MockWarrantyEngine.return_value.evaluate.return_value = {
            "status": "incertaine", "reasons": [], "matched_patterns": {}, "disclaimer": ""
        }
        MockComplexityScorer.return_value.calculate.return_value = {
            "score": 2, "level": "standard", "priority": "standard_review", "breakdown": {}
        }
        MockMessageGenerator.return_value.generate.return_value = None

        # Execute pipeline
        result = analyze_reclamation(reclamation, trainer=mock_trainer)

        # Verify fallback predictions were used
        assert result.predictions["litige_type"]["prediction"] == "unknown"
        assert result.predictions["litige_type"]["confidence"] == 0.0
        assert result.predictions["litige_type"]["available"] is False

        # Verify pipeline continued despite error
        assert isinstance(result, AnalysisResult)
        assert result.processing_time > 0

    @patch('sav_copilot.pipeline.Predictor')
    @patch('sav_copilot.pipeline.InputQualityAnalyzer')
    @patch('sav_copilot.pipeline.WarrantyEngine')
    @patch('sav_copilot.pipeline.ComplexityScorer')
    @patch('sav_copilot.pipeline.MessageGenerator')
    def test_analyze_reclamation_quality_error_fallback(
        self,
        MockMessageGenerator,
        MockComplexityScorer,
        MockWarrantyEngine,
        MockQualityAnalyzer,
        MockPredictor
    ):
        """Test analyze_reclamation handles quality assessment errors gracefully."""
        reclamation = {
            "description": "Problème avec le portail",
            "attachments": []
        }

        mock_trainer = Mock(spec=ModelTrainer)
        mock_trainer.vectorizers = {"litige": Mock()}
        mock_trainer.classifiers = {"litige": Mock()}

        # Mock components
        MockPredictor.return_value.predict_all.return_value = {
            "litige_type": {"prediction": "Test", "confidence": 0.8, "available": True},
            "responsibility": {"prediction": "Test", "confidence": 0.7, "available": True},
            "product_detail": {"prediction": "Test", "confidence": 0.6, "available": True},
            "solution": {"prediction": "Test", "confidence": 0.75, "available": True, "top_3": []}
        }

        # Mock InputQualityAnalyzer to raise error
        mock_quality_analyzer = Mock()
        mock_quality_analyzer.analyze.side_effect = Exception(
            "Quality analysis failed")
        MockQualityAnalyzer.return_value = mock_quality_analyzer

        MockWarrantyEngine.return_value.evaluate.return_value = {
            "status": "incertaine", "reasons": [], "matched_patterns": {}, "disclaimer": ""
        }
        MockComplexityScorer.return_value.calculate.return_value = {
            "score": 2, "level": "standard", "priority": "standard_review", "breakdown": {}
        }
        MockMessageGenerator.return_value.generate.return_value = None

        # Execute pipeline
        result = analyze_reclamation(reclamation, trainer=mock_trainer)

        # Verify fallback quality assessment was used
        assert result.quality["status"] == "usable"
        assert result.quality["issues"] == []

        # Verify pipeline continued despite error
        assert isinstance(result, AnalysisResult)

    @patch('sav_copilot.pipeline.Predictor')
    @patch('sav_copilot.pipeline.InputQualityAnalyzer')
    @patch('sav_copilot.pipeline.WarrantyEngine')
    @patch('sav_copilot.pipeline.ComplexityScorer')
    @patch('sav_copilot.pipeline.MessageGenerator')
    def test_analyze_reclamation_warranty_error_fallback(
        self,
        MockMessageGenerator,
        MockComplexityScorer,
        MockWarrantyEngine,
        MockQualityAnalyzer,
        MockPredictor
    ):
        """Test analyze_reclamation handles warranty evaluation errors gracefully."""
        reclamation = {
            "description": "Problème avec le portail",
            "attachments": []
        }

        mock_trainer = Mock(spec=ModelTrainer)
        mock_trainer.vectorizers = {"litige": Mock()}
        mock_trainer.classifiers = {"litige": Mock()}

        # Mock components
        MockPredictor.return_value.predict_all.return_value = {
            "litige_type": {"prediction": "Test", "confidence": 0.8, "available": True},
            "responsibility": {"prediction": "Test", "confidence": 0.7, "available": True},
            "product_detail": {"prediction": "Test", "confidence": 0.6, "available": True},
            "solution": {"prediction": "Test", "confidence": 0.75, "available": True, "top_3": []}
        }
        MockQualityAnalyzer.return_value.analyze.return_value = {
            "status": "usable", "issues": [], "details": {}
        }

        # Mock WarrantyEngine to raise error
        mock_warranty_engine = Mock()
        mock_warranty_engine.evaluate.side_effect = Exception(
            "Warranty evaluation failed")
        MockWarrantyEngine.return_value = mock_warranty_engine

        MockComplexityScorer.return_value.calculate.return_value = {
            "score": 2, "level": "standard", "priority": "standard_review", "breakdown": {}
        }
        MockMessageGenerator.return_value.generate.return_value = None

        # Execute pipeline
        result = analyze_reclamation(reclamation, trainer=mock_trainer)

        # Verify fallback warranty evaluation was used
        assert result.warranty["status"] == "incertaine"
        assert "Erreur lors de l'évaluation de la garantie" in result.warranty["reasons"]

        # Verify pipeline continued despite error
        assert isinstance(result, AnalysisResult)

    @patch('sav_copilot.pipeline.Predictor')
    @patch('sav_copilot.pipeline.InputQualityAnalyzer')
    @patch('sav_copilot.pipeline.WarrantyEngine')
    @patch('sav_copilot.pipeline.ComplexityScorer')
    @patch('sav_copilot.pipeline.MessageGenerator')
    def test_analyze_reclamation_complexity_error_fallback(
        self,
        MockMessageGenerator,
        MockComplexityScorer,
        MockWarrantyEngine,
        MockQualityAnalyzer,
        MockPredictor
    ):
        """Test analyze_reclamation handles complexity scoring errors gracefully."""
        reclamation = {
            "description": "Problème avec le portail",
            "attachments": []
        }

        mock_trainer = Mock(spec=ModelTrainer)
        mock_trainer.vectorizers = {"litige": Mock()}
        mock_trainer.classifiers = {"litige": Mock()}

        # Mock components
        MockPredictor.return_value.predict_all.return_value = {
            "litige_type": {"prediction": "Test", "confidence": 0.8, "available": True},
            "responsibility": {"prediction": "Test", "confidence": 0.7, "available": True},
            "product_detail": {"prediction": "Test", "confidence": 0.6, "available": True},
            "solution": {"prediction": "Test", "confidence": 0.75, "available": True, "top_3": []}
        }
        MockQualityAnalyzer.return_value.analyze.return_value = {
            "status": "usable", "issues": [], "details": {}
        }
        MockWarrantyEngine.return_value.evaluate.return_value = {
            "status": "incertaine", "reasons": [], "matched_patterns": {}, "disclaimer": ""
        }

        # Mock ComplexityScorer to raise error
        mock_complexity_scorer = Mock()
        mock_complexity_scorer.calculate.side_effect = Exception(
            "Complexity calculation failed")
        MockComplexityScorer.return_value = mock_complexity_scorer

        MockMessageGenerator.return_value.generate.return_value = None

        # Execute pipeline
        result = analyze_reclamation(reclamation, trainer=mock_trainer)

        # Verify fallback complexity score was used
        assert result.complexity["score"] == 2
        assert result.complexity["level"] == "standard"

        # Verify pipeline continued despite error
        assert isinstance(result, AnalysisResult)

    @patch('sav_copilot.pipeline.Predictor')
    @patch('sav_copilot.pipeline.InputQualityAnalyzer')
    @patch('sav_copilot.pipeline.WarrantyEngine')
    @patch('sav_copilot.pipeline.ComplexityScorer')
    @patch('sav_copilot.pipeline.MessageGenerator')
    def test_analyze_reclamation_message_error_fallback(
        self,
        MockMessageGenerator,
        MockComplexityScorer,
        MockWarrantyEngine,
        MockQualityAnalyzer,
        MockPredictor
    ):
        """Test analyze_reclamation handles message generation errors gracefully."""
        reclamation = {
            "description": "Problème avec le portail",
            "attachments": []
        }

        mock_trainer = Mock(spec=ModelTrainer)
        mock_trainer.vectorizers = {"litige": Mock()}
        mock_trainer.classifiers = {"litige": Mock()}

        # Mock components
        MockPredictor.return_value.predict_all.return_value = {
            "litige_type": {"prediction": "Test", "confidence": 0.8, "available": True},
            "responsibility": {"prediction": "Test", "confidence": 0.7, "available": True},
            "product_detail": {"prediction": "Test", "confidence": 0.6, "available": True},
            "solution": {"prediction": "Test", "confidence": 0.75, "available": True, "top_3": []}
        }
        MockQualityAnalyzer.return_value.analyze.return_value = {
            "status": "usable", "issues": [], "details": {}
        }
        MockWarrantyEngine.return_value.evaluate.return_value = {
            "status": "incertaine", "reasons": [], "matched_patterns": {}, "disclaimer": ""
        }
        MockComplexityScorer.return_value.calculate.return_value = {
            "score": 2, "level": "standard", "priority": "standard_review", "breakdown": {}
        }

        # Mock MessageGenerator to raise error
        mock_message_generator = Mock()
        mock_message_generator.generate.side_effect = Exception(
            "Message generation failed")
        MockMessageGenerator.return_value = mock_message_generator

        # Execute pipeline
        result = analyze_reclamation(reclamation, trainer=mock_trainer)

        # Verify no message was generated (fallback to None)
        assert result.message is None

        # Verify pipeline continued despite error
        assert isinstance(result, AnalysisResult)

    @patch('sav_copilot.pipeline.Predictor')
    @patch('sav_copilot.pipeline.InputQualityAnalyzer')
    @patch('sav_copilot.pipeline.WarrantyEngine')
    @patch('sav_copilot.pipeline.ComplexityScorer')
    @patch('sav_copilot.pipeline.MessageGenerator')
    def test_analyze_reclamation_processing_time_measured(
        self,
        MockMessageGenerator,
        MockComplexityScorer,
        MockWarrantyEngine,
        MockQualityAnalyzer,
        MockPredictor
    ):
        """Test analyze_reclamation measures processing time."""
        reclamation = {
            "description": "Problème avec le portail",
            "attachments": []
        }

        mock_trainer = Mock(spec=ModelTrainer)
        mock_trainer.vectorizers = {"litige": Mock()}
        mock_trainer.classifiers = {"litige": Mock()}

        # Mock all components
        MockPredictor.return_value.predict_all.return_value = {
            "litige_type": {"prediction": "Test", "confidence": 0.8, "available": True},
            "responsibility": {"prediction": "Test", "confidence": 0.7, "available": True},
            "product_detail": {"prediction": "Test", "confidence": 0.6, "available": True},
            "solution": {"prediction": "Test", "confidence": 0.75, "available": True, "top_3": []}
        }
        MockQualityAnalyzer.return_value.analyze.return_value = {
            "status": "usable", "issues": [], "details": {}
        }
        MockWarrantyEngine.return_value.evaluate.return_value = {
            "status": "incertaine", "reasons": [], "matched_patterns": {}, "disclaimer": ""
        }
        MockComplexityScorer.return_value.calculate.return_value = {
            "score": 2, "level": "standard", "priority": "standard_review", "breakdown": {}
        }
        MockMessageGenerator.return_value.generate.return_value = None

        # Execute pipeline
        result = analyze_reclamation(reclamation, trainer=mock_trainer)

        # Verify processing time was measured
        assert result.processing_time >= 0
        assert isinstance(result.processing_time, float)
