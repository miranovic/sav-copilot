"""
Unit tests for the Predictor class.
"""

import pandas as pd
import pytest

from sav_copilot.trainer import ModelTrainer
from sav_copilot.predictor import Predictor


class TestPredictor:
    """Test suite for Predictor class."""

    @pytest.fixture
    def sample_training_data(self):
        """Create sample training data for testing."""
        data = {
            'description_features': [
                'Portail coulissant défectueux',
                'Problème de rouille sur la clôture',
                'Défaut de fabrication sur le portail',
                'Usure normale du produit',
                'Mauvais entretien causant des dommages',
                'Pièce cassée nécessitant remplacement',
                'Corrosion due à environnement agressif',
                'Installation non conforme',
                'Rayure sur le portail',
                'Décoloration naturelle du produit'
            ],
            'Type de litige': [
                'Défaut de fabrication',
                'Défaut de fabrication',
                'Défaut de fabrication',
                'Usure normale',
                'Mauvais entretien',
                'Défaut de fabrication',
                'Environnement agressif',
                'Installation',
                'Dommage manipulation',
                'Usure normale'
            ],
            'Responsabilité': [
                'Fabricant',
                'Fabricant',
                'Fabricant',
                'Client',
                'Client',
                'Fabricant',
                'Client',
                'Installateur',
                'Client',
                'Client'
            ],
            'Précision produit': [
                'Portail coulissant',
                'Clôture',
                'Portail',
                'Portail',
                'Clôture',
                'Portail coulissant',
                'Clôture',
                'Portail',
                'Portail',
                'Portail coulissant'
            ],
            'Solution': [
                'Remplacement pièce',
                'Réparation sur site',
                'Remplacement pièce',
                'Refus garantie',
                'Refus garantie',
                'Remplacement pièce',
                'Refus garantie',
                'Réparation installateur',
                'Refus garantie',
                'Refus garantie'
            ]
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def trained_predictor(self, sample_training_data, tmp_path):
        """Create a predictor with trained models."""
        # Train models
        trainer = ModelTrainer(models_dir=str(tmp_path))
        trainer.train_all(
            df=sample_training_data,
            text_column='description_features',
            target_columns=['Type de litige', 'Responsabilité',
                            'Précision produit', 'Solution']
        )

        # Create predictor
        predictor = Predictor(trainer)
        return predictor

    @pytest.fixture
    def empty_predictor(self, tmp_path):
        """Create a predictor with no trained models."""
        trainer = ModelTrainer(models_dir=str(tmp_path))
        predictor = Predictor(trainer)
        return predictor

    def test_init(self, trained_predictor):
        """Test predictor initialization."""
        assert trained_predictor.trainer is not None
        assert isinstance(trained_predictor.trainer, ModelTrainer)

    def test_predict_single_success(self, trained_predictor):
        """Test successful single prediction."""
        text = "Portail coulissant avec défaut de fabrication"

        result = trained_predictor.predict_single(text, "litige")

        assert "prediction" in result
        assert "confidence" in result
        assert "available" in result
        assert result["available"] is True
        assert isinstance(result["prediction"], str)
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_predict_single_all_targets(self, trained_predictor):
        """Test prediction for all targets."""
        text = "Portail coulissant avec défaut de fabrication"

        targets = ["litige", "responsibility", "product", "solution"]

        for target in targets:
            result = trained_predictor.predict_single(text, target)
            assert result["available"] is True
            assert result["prediction"] != "unknown"
            assert result["confidence"] > 0.0

    def test_predict_single_model_unavailable(self, empty_predictor):
        """Test prediction when model is unavailable."""
        text = "Some complaint text"

        result = empty_predictor.predict_single(text, "litige")

        assert result["prediction"] == "unknown"
        assert result["confidence"] == 0.0
        assert result["available"] is False

    def test_predict_single_invalid_target(self, trained_predictor):
        """Test prediction with invalid target name."""
        text = "Some complaint text"

        result = trained_predictor.predict_single(text, "nonexistent_target")

        assert result["prediction"] == "unknown"
        assert result["confidence"] == 0.0
        assert result["available"] is False

    def test_predict_top_k_success(self, trained_predictor):
        """Test successful top-K prediction."""
        text = "Portail coulissant avec défaut de fabrication"

        results = trained_predictor.predict_top_k(text, "solution", k=3)

        assert isinstance(results, list)
        assert len(results) <= 3
        assert len(results) > 0

        # Check structure of each result
        for result in results:
            assert "label" in result
            assert "confidence" in result
            assert isinstance(result["label"], str)
            assert isinstance(result["confidence"], float)
            assert 0.0 <= result["confidence"] <= 1.0

        # Check that results are sorted by confidence (descending)
        confidences = [r["confidence"] for r in results]
        assert confidences == sorted(confidences, reverse=True)

        # Check that confidences sum to approximately 1.0
        total_confidence = sum(confidences)
        assert 0.9 <= total_confidence <= 1.1

    def test_predict_top_k_different_k_values(self, trained_predictor):
        """Test top-K prediction with different K values."""
        text = "Portail coulissant avec défaut de fabrication"

        # Test k=1
        results_1 = trained_predictor.predict_top_k(text, "solution", k=1)
        assert len(results_1) == 1

        # Test k=2
        results_2 = trained_predictor.predict_top_k(text, "solution", k=2)
        assert len(results_2) <= 2

        # Test k=5 (may return fewer if there are fewer classes)
        results_5 = trained_predictor.predict_top_k(text, "solution", k=5)
        assert len(results_5) <= 5

        # First result should be the same across all K values
        assert results_1[0]["label"] == results_2[0]["label"]
        assert results_1[0]["label"] == results_5[0]["label"]

    def test_predict_top_k_model_unavailable(self, empty_predictor):
        """Test top-K prediction when model is unavailable."""
        text = "Some complaint text"

        results = empty_predictor.predict_top_k(text, "solution", k=3)

        assert isinstance(results, list)
        assert len(results) == 0

    def test_predict_all_success(self, trained_predictor):
        """Test prediction of all targets."""
        text = "Portail coulissant avec défaut de fabrication"

        result = trained_predictor.predict_all(text)

        # Check structure
        assert "litige_type" in result
        assert "responsibility" in result
        assert "product_detail" in result
        assert "solution" in result

        # Check each target has required fields
        for target_key in ["litige_type", "responsibility", "product_detail"]:
            assert "prediction" in result[target_key]
            assert "confidence" in result[target_key]
            assert "available" in result[target_key]
            assert result[target_key]["available"] is True

        # Check solution has top_3
        assert "prediction" in result["solution"]
        assert "confidence" in result["solution"]
        assert "available" in result["solution"]
        assert "top_3" in result["solution"]
        assert isinstance(result["solution"]["top_3"], list)
        assert len(result["solution"]["top_3"]) <= 3

    def test_predict_all_with_missing_models(self, empty_predictor):
        """Test predict_all when models are unavailable."""
        text = "Some complaint text"

        result = empty_predictor.predict_all(text)

        # Should still return structure
        assert "litige_type" in result
        assert "responsibility" in result
        assert "product_detail" in result
        assert "solution" in result

        # All should be unavailable
        for target_key in result.keys():
            assert result[target_key]["available"] is False
            assert result[target_key]["prediction"] == "unknown"
            assert result[target_key]["confidence"] == 0.0

        # Solution should have empty top_3
        assert result["solution"]["top_3"] == []

    def test_predict_all_consistency(self, trained_predictor):
        """Test that predict_all is consistent with predict_single."""
        text = "Portail coulissant avec défaut de fabrication"

        # Get predictions using predict_all
        all_result = trained_predictor.predict_all(text)

        # Get predictions using predict_single
        litige_single = trained_predictor.predict_single(text, "litige")
        responsibility_single = trained_predictor.predict_single(
            text, "responsibility")
        product_single = trained_predictor.predict_single(text, "product")
        solution_single = trained_predictor.predict_single(text, "solution")

        # Compare results
        assert all_result["litige_type"]["prediction"] == litige_single["prediction"]
        assert all_result["litige_type"]["confidence"] == litige_single["confidence"]

        assert all_result["responsibility"]["prediction"] == responsibility_single["prediction"]
        assert all_result["responsibility"]["confidence"] == responsibility_single["confidence"]

        assert all_result["product_detail"]["prediction"] == product_single["prediction"]
        assert all_result["product_detail"]["confidence"] == product_single["confidence"]

        assert all_result["solution"]["prediction"] == solution_single["prediction"]
        assert all_result["solution"]["confidence"] == solution_single["confidence"]

    def test_predict_with_empty_text(self, trained_predictor):
        """Test prediction with empty text."""
        text = ""

        result = trained_predictor.predict_single(text, "litige")

        # Should still return a result (model handles empty input)
        assert "prediction" in result
        assert "confidence" in result
        assert "available" in result

    def test_predict_with_special_characters(self, trained_predictor):
        """Test prediction with special characters."""
        text = "Portail @#$% défectueux !!! ???"

        result = trained_predictor.predict_single(text, "litige")

        # Should handle special characters gracefully
        assert result["available"] is True
        assert isinstance(result["prediction"], str)
        assert isinstance(result["confidence"], float)

    def test_confidence_scores_are_valid_probabilities(self, trained_predictor):
        """Test that confidence scores are valid probabilities."""
        text = "Portail coulissant avec défaut de fabrication"

        targets = ["litige", "responsibility", "product", "solution"]

        for target in targets:
            result = trained_predictor.predict_single(text, target)
            if result["available"]:
                assert 0.0 <= result["confidence"] <= 1.0

    def test_top_k_returns_sorted_results(self, trained_predictor):
        """Test that top-K results are sorted by confidence."""
        text = "Portail coulissant avec défaut de fabrication"

        results = trained_predictor.predict_top_k(text, "solution", k=5)

        # Extract confidences
        confidences = [r["confidence"] for r in results]

        # Check that they are in descending order
        for i in range(len(confidences) - 1):
            assert confidences[i] >= confidences[i + 1]

    def test_predict_all_solution_top_3_matches_predict_top_k(self, trained_predictor):
        """Test that solution top_3 in predict_all matches predict_top_k."""
        text = "Portail coulissant avec défaut de fabrication"

        all_result = trained_predictor.predict_all(text)
        top_k_result = trained_predictor.predict_top_k(text, "solution", k=3)

        # Compare top_3 from predict_all with predict_top_k
        assert len(all_result["solution"]["top_3"]) == len(top_k_result)

        for i in range(len(top_k_result)):
            assert all_result["solution"]["top_3"][i]["label"] == top_k_result[i]["label"]
            assert all_result["solution"]["top_3"][i]["confidence"] == top_k_result[i]["confidence"]
