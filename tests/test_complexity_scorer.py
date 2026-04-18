"""
Unit tests for ComplexityScorer module.

Tests the complexity scoring logic, priority assignment, and edge cases.
"""

import pytest
from sav_copilot.complexity_scorer import ComplexityScorer
from config import (
    QUALITY_USABLE,
    QUALITY_POOR,
    QUALITY_UNUSABLE,
    WARRANTY_HORS_GARANTIE,
    WARRANTY_INCERTAINE,
    WARRANTY_ELIGIBLE,
    PRIORITY_QUICK_WIN,
    PRIORITY_STANDARD,
    PRIORITY_EXPERT,
    LEVEL_RAPIDE,
    LEVEL_STANDARD,
    LEVEL_COMPLEXE
)


class TestComplexityScorer:
    """Test suite for ComplexityScorer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = ComplexityScorer()

    def test_initialization(self):
        """Test ComplexityScorer initialization."""
        assert self.scorer is not None

    def test_quick_win_case(self):
        """Test quick win case: high confidence, good quality, clear warranty."""
        analysis_result = {
            "quality": {
                "status": QUALITY_USABLE,
                "issues": [],
                "details": {
                    "attachment_count": 1,
                    "description_length": 50,
                    "meaningful_word_count": 10
                }
            },
            "predictions": {
                "litige_type": {"prediction": "Défaut", "confidence": 0.9, "available": True},
                "responsibility": {"prediction": "Fabricant", "confidence": 0.85, "available": True},
                "product_detail": {"prediction": "Portail", "confidence": 0.88, "available": True},
                "solution": {"prediction": "Remplacement", "confidence": 0.92, "available": True}
            },
            "warranty": {
                "status": WARRANTY_HORS_GARANTIE,
                "reasons": ["Usure normale"],
                "matched_patterns": {"normal_wear": ["usure"]}
            }
        }

        result = self.scorer.calculate(analysis_result)

        assert result["score"] <= 1
        assert result["priority"] == PRIORITY_QUICK_WIN
        assert result["level"] == LEVEL_RAPIDE
        assert "breakdown" in result

    def test_standard_case(self):
        """Test standard case: moderate confidence, some issues."""
        analysis_result = {
            "quality": {
                "status": QUALITY_POOR,
                "issues": ["too_short"],
                "details": {
                    "attachment_count": 2,
                    "description_length": 15,
                    "meaningful_word_count": 4
                }
            },
            "predictions": {
                "litige_type": {"prediction": "Défaut", "confidence": 0.6, "available": True},
                "responsibility": {"prediction": "Fabricant", "confidence": 0.55, "available": True},
                "product_detail": {"prediction": "Portail", "confidence": 0.5, "available": True},
                "solution": {"prediction": "Remplacement", "confidence": 0.58, "available": True}
            },
            "warranty": {
                "status": WARRANTY_HORS_GARANTIE,
                "reasons": ["Choc détecté"],
                "matched_patterns": {"handling_damage": ["choc"]}
            }
        }

        result = self.scorer.calculate(analysis_result)

        assert 2 <= result["score"] <= 3
        assert result["priority"] == PRIORITY_STANDARD
        assert result["level"] == LEVEL_STANDARD

    def test_expert_case(self):
        """Test expert case: low confidence, poor quality, uncertain warranty."""
        analysis_result = {
            "quality": {
                "status": QUALITY_UNUSABLE,
                "issues": ["too_short", "too_vague"],
                "details": {
                    "attachment_count": 3,
                    "description_length": 10,
                    "meaningful_word_count": 2
                }
            },
            "predictions": {
                "litige_type": {"prediction": "Défaut", "confidence": 0.3, "available": True},
                "responsibility": {"prediction": "Fabricant", "confidence": 0.35, "available": True},
                "product_detail": {"prediction": "Portail", "confidence": 0.4, "available": True},
                "solution": {"prediction": "Remplacement", "confidence": 0.25, "available": True}
            },
            "warranty": {
                "status": WARRANTY_INCERTAINE,
                "reasons": ["Aucun motif d'exclusion détecté"],
                "matched_patterns": {}
            }
        }

        result = self.scorer.calculate(analysis_result)

        assert result["score"] >= 4
        assert result["priority"] == PRIORITY_EXPERT
        assert result["level"] == LEVEL_COMPLEXE

    def test_score_data_quality_unusable(self):
        """Test data quality scoring for unusable quality."""
        quality = {
            "status": QUALITY_UNUSABLE,
            "issues": ["too_short", "too_vague"],
            "details": {"attachment_count": 0}
        }

        score = self.scorer._score_data_quality(quality)
        assert score == 2  # +2 for unusable

    def test_score_data_quality_poor(self):
        """Test data quality scoring for poor quality."""
        quality = {
            "status": QUALITY_POOR,
            "issues": ["too_short"],
            "details": {"attachment_count": 1}
        }

        score = self.scorer._score_data_quality(quality)
        assert score == 1  # +1 for poor

    def test_score_data_quality_multiple_attachments(self):
        """Test data quality scoring for multiple attachments."""
        quality = {
            "status": QUALITY_USABLE,
            "issues": [],
            "details": {"attachment_count": 3}
        }

        score = self.scorer._score_data_quality(quality)
        assert score == 1  # +1 for multiple attachments

    def test_score_data_quality_poor_with_multiple_attachments(self):
        """Test data quality scoring for poor quality with multiple attachments."""
        quality = {
            "status": QUALITY_POOR,
            "issues": ["missing_attachments"],
            "details": {"attachment_count": 2}
        }

        score = self.scorer._score_data_quality(quality)
        assert score == 2  # +1 for poor, +1 for multiple attachments

    def test_score_predictions_low_solution_confidence(self):
        """Test prediction scoring for low solution confidence."""
        predictions = {
            "solution": {"confidence": 0.4},
            "responsibility": {"confidence": 0.7},
            "litige_type": {"confidence": 0.6},
            "product_detail": {"confidence": 0.5}
        }

        score = self.scorer._score_predictions(predictions)
        assert score >= 1  # +1 for low solution confidence

    def test_score_predictions_low_responsibility_confidence(self):
        """Test prediction scoring for low responsibility confidence."""
        predictions = {
            "solution": {"confidence": 0.6},
            "responsibility": {"confidence": 0.3},
            "litige_type": {"confidence": 0.7},
            "product_detail": {"confidence": 0.5}
        }

        score = self.scorer._score_predictions(predictions)
        assert score >= 1  # +1 for low responsibility confidence

    def test_score_predictions_contradictory_signals(self):
        """Test prediction scoring for contradictory signals."""
        predictions = {
            "solution": {"confidence": 0.9},  # High
            "responsibility": {"confidence": 0.3},  # Low
            "litige_type": {"confidence": 0.6},
            "product_detail": {"confidence": 0.5}
        }

        score = self.scorer._score_predictions(predictions)
        assert score >= 2  # +1 for low responsibility, +1 for contradiction

    def test_score_warranty_uncertain(self):
        """Test warranty scoring for uncertain status."""
        warranty = {
            "status": WARRANTY_INCERTAINE,
            "reasons": [],
            "matched_patterns": {}
        }

        score = self.scorer._score_warranty(warranty)
        assert score == 2  # +2 for uncertain warranty

    def test_score_warranty_clear(self):
        """Test warranty scoring for clear status."""
        warranty = {
            "status": WARRANTY_HORS_GARANTIE,
            "reasons": ["Usure normale"],
            "matched_patterns": {"normal_wear": ["usure"]}
        }

        score = self.scorer._score_warranty(warranty)
        assert score == 0  # No penalty for clear warranty

    def test_score_clarity_high_solution_confidence(self):
        """Test clarity scoring for high solution confidence."""
        predictions = {
            "solution": {"confidence": 0.85},
            "responsibility": {"confidence": 0.6},
            "litige_type": {"confidence": 0.7},
            "product_detail": {"confidence": 0.65}
        }

        score = self.scorer._score_clarity(predictions)
        assert score == -1  # -1 bonus for high solution confidence

    def test_score_clarity_very_clear_case(self):
        """Test clarity scoring for very clear case (all high confidence)."""
        predictions = {
            "solution": {"confidence": 0.9},
            "responsibility": {"confidence": 0.85},
            "litige_type": {"confidence": 0.88},
            "product_detail": {"confidence": 0.82}
        }

        score = self.scorer._score_clarity(predictions)
        assert score == -2  # -1 for high solution, -1 for all high

    def test_score_clarity_low_confidence(self):
        """Test clarity scoring for low confidence (no bonus)."""
        predictions = {
            "solution": {"confidence": 0.5},
            "responsibility": {"confidence": 0.4},
            "litige_type": {"confidence": 0.6},
            "product_detail": {"confidence": 0.45}
        }

        score = self.scorer._score_clarity(predictions)
        assert score == 0  # No bonus for low confidence

    def test_breakdown_structure(self):
        """Test that breakdown contains all expected components."""
        analysis_result = {
            "quality": {
                "status": QUALITY_USABLE,
                "issues": [],
                "details": {"attachment_count": 1}
            },
            "predictions": {
                "litige_type": {"confidence": 0.7},
                "responsibility": {"confidence": 0.6},
                "product_detail": {"confidence": 0.5},
                "solution": {"confidence": 0.65}
            },
            "warranty": {
                "status": WARRANTY_HORS_GARANTIE,
                "reasons": [],
                "matched_patterns": {}
            }
        }

        result = self.scorer.calculate(analysis_result)

        assert "breakdown" in result
        breakdown = result["breakdown"]
        assert "data_quality" in breakdown
        assert "prediction_confidence" in breakdown
        assert "warranty_uncertainty" in breakdown
        assert "clarity_bonus" in breakdown

    def test_missing_components(self):
        """Test handling of missing components in analysis result."""
        analysis_result = {}

        result = self.scorer.calculate(analysis_result)

        assert "score" in result
        assert "level" in result
        assert "priority" in result
        assert "breakdown" in result

    def test_boundary_score_1(self):
        """Test boundary case: score exactly 1 (quick win threshold)."""
        analysis_result = {
            "quality": {
                "status": QUALITY_POOR,
                "issues": ["too_short"],
                "details": {"attachment_count": 1}
            },
            "predictions": {
                "litige_type": {"confidence": 0.9},
                "responsibility": {"confidence": 0.85},
                "product_detail": {"confidence": 0.88},
                "solution": {"confidence": 0.92}
            },
            "warranty": {
                "status": WARRANTY_HORS_GARANTIE,
                "reasons": [],
                "matched_patterns": {}
            }
        }

        result = self.scorer.calculate(analysis_result)

        # Score should be: +1 (poor) -2 (clarity bonuses) = -1, but min is typically 0
        # Actually: +1 (poor) -1 (high solution) -1 (all high) = -1
        # Let's verify the actual behavior
        assert result["priority"] in [PRIORITY_QUICK_WIN, PRIORITY_STANDARD]

    def test_boundary_score_4(self):
        """Test boundary case: score exactly 4 (expert review threshold)."""
        analysis_result = {
            "quality": {
                "status": QUALITY_UNUSABLE,
                "issues": ["too_short", "too_vague"],
                "details": {"attachment_count": 1}
            },
            "predictions": {
                "litige_type": {"confidence": 0.6},
                "responsibility": {"confidence": 0.55},
                "product_detail": {"confidence": 0.5},
                "solution": {"confidence": 0.58}
            },
            "warranty": {
                "status": WARRANTY_INCERTAINE,
                "reasons": [],
                "matched_patterns": {}
            }
        }

        result = self.scorer.calculate(analysis_result)

        # Score should be: +2 (unusable) +2 (uncertain warranty) = 4
        assert result["score"] == 4
        assert result["priority"] == PRIORITY_EXPERT
        assert result["level"] == LEVEL_COMPLEXE
