"""
Unit tests for the WarrantyEngine module.

Tests warranty eligibility assessment based on text pattern matching.
"""

import pytest
from sav_copilot.warranty_engine import WarrantyEngine
from config import (
    WARRANTY_HORS_GARANTIE,
    WARRANTY_INCERTAINE,
    WARRANTY_ELIGIBLE,
    WARRANTY_DISCLAIMER
)


class TestWarrantyEngine:
    """Test suite for WarrantyEngine class."""

    @pytest.fixture
    def engine(self):
        """Create a WarrantyEngine instance for testing."""
        return WarrantyEngine()

    def test_initialization(self, engine):
        """Test that the engine initializes with all exclusion categories."""
        categories = engine.get_exclusion_categories()

        assert len(categories) == 5
        assert "normal_wear" in categories
        assert "poor_maintenance" in categories
        assert "handling_damage" in categories
        assert "aggressive_environment" in categories
        assert "hardware_accessories" in categories

    def test_normal_wear_detection(self, engine):
        """Test detection of normal wear and aging patterns."""
        test_cases = [
            "Le portail montre des signes d'usure normale",
            "Vieillissement naturel du matériau",
            "La couleur est décolorée après plusieurs années"
        ]

        for text in test_cases:
            result = engine.evaluate(text)
            assert result["status"] == WARRANTY_HORS_GARANTIE
            assert "normal_wear" in result["matched_patterns"]
            assert len(result["reasons"]) > 0
            assert result["disclaimer"] == WARRANTY_DISCLAIMER

    def test_poor_maintenance_detection(self, engine):
        """Test detection of poor maintenance patterns."""
        test_cases = [
            "Le problème vient d'un mauvais entretien",
            "Installation non conforme aux recommandations",
            "Défaut d'entretien régulier"
        ]

        for text in test_cases:
            result = engine.evaluate(text)
            assert result["status"] == WARRANTY_HORS_GARANTIE
            assert "poor_maintenance" in result["matched_patterns"]
            assert any("entretien" in reason.lower() or "installation" in reason.lower()
                       for reason in result["reasons"])

    def test_handling_damage_detection(self, engine):
        """Test detection of handling damage patterns."""
        test_cases = [
            "Le portail a subi un choc lors de la livraison",
            "Plusieurs rayures visibles sur la surface",
            "Dommage de manipulation évident"
        ]

        for text in test_cases:
            result = engine.evaluate(text)
            assert result["status"] == WARRANTY_HORS_GARANTIE
            assert "handling_damage" in result["matched_patterns"]
            assert any("choc" in reason.lower() or "rayure" in reason.lower() or "manipulation" in reason.lower()
                       for reason in result["reasons"])

    def test_aggressive_environment_detection(self, engine):
        """Test detection of aggressive environment patterns."""
        test_cases = [
            "Installation en bord de mer",
            "Corrosion due à l'environnement agressif",
            "Le portail est rouillé à cause de l'air marin"
        ]

        for text in test_cases:
            result = engine.evaluate(text)
            assert result["status"] == WARRANTY_HORS_GARANTIE
            assert "aggressive_environment" in result["matched_patterns"]
            assert any("environnement" in reason.lower() or "corrosion" in reason.lower()
                       for reason in result["reasons"])

    def test_hardware_accessories_detection(self, engine):
        """Test detection of hardware and accessories patterns."""
        test_cases = [
            "Problème avec la quincaillerie",
            "Le moteur ne fonctionne plus",
            "Défaut sur la carte électronique",
            "Les accessoires sont défectueux"
        ]

        for text in test_cases:
            result = engine.evaluate(text)
            assert result["status"] == WARRANTY_HORS_GARANTIE
            assert "hardware_accessories" in result["matched_patterns"]
            assert any("quincaillerie" in reason.lower() or "accessoires" in reason.lower() or "électronique" in reason.lower()
                       for reason in result["reasons"])

    def test_multiple_exclusions(self, engine):
        """Test detection of multiple exclusion categories in one text."""
        text = "Le portail installé en bord de mer montre de l'usure et des rayures"
        result = engine.evaluate(text)

        assert result["status"] == WARRANTY_HORS_GARANTIE
        assert len(result["matched_patterns"]) >= 2
        assert "normal_wear" in result["matched_patterns"]
        assert "handling_damage" in result["matched_patterns"] or "aggressive_environment" in result["matched_patterns"]
        assert len(result["reasons"]) >= 2

    def test_no_exclusion_patterns(self, engine):
        """Test that clean complaints return uncertain status."""
        test_cases = [
            "Le portail ne ferme pas correctement",
            "Problème de fonctionnement du système",
            "Défaut de fabrication apparent"
        ]

        for text in test_cases:
            result = engine.evaluate(text)
            assert result["status"] == WARRANTY_INCERTAINE
            assert len(result["matched_patterns"]) == 0
            assert len(result["reasons"]) > 0
            assert result["disclaimer"] == WARRANTY_DISCLAIMER

    def test_empty_text(self, engine):
        """Test handling of empty or invalid text."""
        test_cases = ["", None, "   "]

        for text in test_cases:
            result = engine.evaluate(text)
            assert result["status"] == WARRANTY_INCERTAINE
            assert "invalide" in result["reasons"][0].lower(
            ) or "manquant" in result["reasons"][0].lower()

    def test_case_insensitive_matching(self, engine):
        """Test that pattern matching is case-insensitive."""
        test_cases = [
            "USURE NORMALE",
            "Usure Normale",
            "usure normale"
        ]

        for text in test_cases:
            result = engine.evaluate(text)
            assert result["status"] == WARRANTY_HORS_GARANTIE
            assert "normal_wear" in result["matched_patterns"]

    def test_disclaimer_always_present(self, engine):
        """Test that disclaimer is always included in results."""
        test_cases = [
            "Usure normale",
            "Défaut de fabrication",
            ""
        ]

        for text in test_cases:
            result = engine.evaluate(text)
            assert "disclaimer" in result
            assert result["disclaimer"] == WARRANTY_DISCLAIMER
            assert "indicative" in result["disclaimer"].lower(
            ) or "indicatif" in result["disclaimer"].lower()

    def test_get_patterns_for_category(self, engine):
        """Test retrieval of patterns for specific categories."""
        patterns = engine.get_patterns_for_category("normal_wear")
        assert len(patterns) > 0
        assert any("usure" in p for p in patterns)

        # Test non-existent category
        patterns = engine.get_patterns_for_category("non_existent")
        assert patterns == []

    def test_matched_patterns_structure(self, engine):
        """Test that matched patterns are properly structured."""
        text = "Le portail montre de l'usure normale"
        result = engine.evaluate(text)

        assert isinstance(result["matched_patterns"], dict)
        for category, matches in result["matched_patterns"].items():
            assert isinstance(matches, list)
            assert len(matches) > 0
            for match in matches:
                assert isinstance(match, str)
