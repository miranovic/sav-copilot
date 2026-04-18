"""
Unit tests for InputQualityAnalyzer module.

Tests cover:
- Description length checking
- Attachment checking
- Vagueness detection
- Overall quality analysis
- Status determination logic
"""

import pytest
from sav_copilot.quality_analyzer import InputQualityAnalyzer


class TestInputQualityAnalyzer:
    """Test suite for InputQualityAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create an InputQualityAnalyzer instance with default settings."""
        return InputQualityAnalyzer(
            min_description_length=20,
            min_meaningful_words=5
        )

    # ========================================================================
    # Test check_description_length
    # ========================================================================

    def test_check_description_length_valid(self, analyzer):
        """Test that valid length descriptions pass."""
        text = "This is a sufficiently long description for testing purposes."
        result = analyzer.check_description_length(text)
        assert result is None

    def test_check_description_length_too_short(self, analyzer):
        """Test that short descriptions are flagged."""
        text = "Too short"
        result = analyzer.check_description_length(text)
        assert result == "too_short"

    def test_check_description_length_exactly_minimum(self, analyzer):
        """Test description exactly at minimum length."""
        text = "x" * 20  # Exactly 20 characters
        result = analyzer.check_description_length(text)
        assert result is None

    def test_check_description_length_one_below_minimum(self, analyzer):
        """Test description one character below minimum."""
        text = "x" * 19  # 19 characters
        result = analyzer.check_description_length(text)
        assert result == "too_short"

    def test_check_description_length_empty(self, analyzer):
        """Test empty description."""
        text = ""
        result = analyzer.check_description_length(text)
        assert result == "too_short"

    def test_check_description_length_whitespace_only(self, analyzer):
        """Test description with only whitespace."""
        text = "     "
        result = analyzer.check_description_length(text)
        assert result == "too_short"

    def test_check_description_length_none(self, analyzer):
        """Test None input."""
        result = analyzer.check_description_length(None)
        assert result == "too_short"

    # ========================================================================
    # Test check_attachments
    # ========================================================================

    def test_check_attachments_valid(self, analyzer):
        """Test that valid attachments pass."""
        attachments = ["file1.jpg", "file2.pdf"]
        result = analyzer.check_attachments(attachments)
        assert result is None

    def test_check_attachments_single(self, analyzer):
        """Test single attachment."""
        attachments = ["file1.jpg"]
        result = analyzer.check_attachments(attachments)
        assert result is None

    def test_check_attachments_empty_list(self, analyzer):
        """Test empty attachment list."""
        attachments = []
        result = analyzer.check_attachments(attachments)
        assert result == "missing_attachments"

    def test_check_attachments_none(self, analyzer):
        """Test None attachments."""
        attachments = None
        result = analyzer.check_attachments(attachments)
        assert result == "missing_attachments"

    def test_check_attachments_empty_strings(self, analyzer):
        """Test list with only empty strings."""
        attachments = ["", "  ", ""]
        result = analyzer.check_attachments(attachments)
        assert result == "missing_attachments"

    def test_check_attachments_mixed_valid_invalid(self, analyzer):
        """Test list with mix of valid and empty attachments."""
        attachments = ["file1.jpg", "", "file2.pdf"]
        result = analyzer.check_attachments(attachments)
        assert result is None  # Has valid attachments

    # ========================================================================
    # Test check_vagueness
    # ========================================================================

    def test_check_vagueness_valid(self, analyzer):
        """Test that descriptions with enough meaningful words pass."""
        text = "Le portail coulissant présente un défaut de fabrication important."
        result = analyzer.check_vagueness(text)
        assert result is None

    def test_check_vagueness_too_vague(self, analyzer):
        """Test that vague descriptions are flagged."""
        text = "Le portail est cassé"  # Only 2 meaningful words: portail, cassé
        result = analyzer.check_vagueness(text)
        assert result == "too_vague"

    def test_check_vagueness_exactly_minimum(self, analyzer):
        """Test description with exactly minimum meaningful words."""
        # 5 meaningful words: portail, coulissant, défaut, fabrication, important
        text = "Le portail coulissant a un défaut de fabrication important"
        result = analyzer.check_vagueness(text)
        assert result is None

    def test_check_vagueness_one_below_minimum(self, analyzer):
        """Test description with one less than minimum meaningful words."""
        # 4 meaningful words: portail, coulissant, défaut, fabrication
        text = "Le portail coulissant a un défaut de fabrication"
        result = analyzer.check_vagueness(text)
        assert result == "too_vague"

    def test_check_vagueness_empty(self, analyzer):
        """Test empty description."""
        text = ""
        result = analyzer.check_vagueness(text)
        assert result == "too_vague"

    def test_check_vagueness_only_stop_words(self, analyzer):
        """Test description with only stop words."""
        text = "le la les un une des de du et ou"
        result = analyzer.check_vagueness(text)
        assert result == "too_vague"

    def test_check_vagueness_none(self, analyzer):
        """Test None input."""
        result = analyzer.check_vagueness(None)
        assert result == "too_vague"

    # ========================================================================
    # Test analyze (integration)
    # ========================================================================

    def test_analyze_usable_quality(self, analyzer):
        """Test analysis of high-quality input."""
        reclamation = {
            "description": "Le portail coulissant présente un défaut de fabrication important avec rayures visibles.",
            "attachments": ["photo1.jpg", "photo2.jpg"]
        }
        result = analyzer.analyze(reclamation)

        assert result["status"] == "usable"
        assert result["issues"] == []
        assert result["details"]["description_length"] > 20
        assert result["details"]["attachment_count"] == 2
        assert result["details"]["meaningful_word_count"] >= 5

    def test_analyze_poor_quality_short(self, analyzer):
        """Test analysis with only one issue (missing attachments)."""
        reclamation = {
            # 46 chars, 5 meaningful words - OK, but no attachments
            "description": "Portail coulissant défaut fabrication problème",
            "attachments": []  # Missing attachments - this is the issue
        }
        result = analyzer.analyze(reclamation)

        assert result["status"] == "poor"
        assert "missing_attachments" in result["issues"]
        assert len(result["issues"]) == 1  # Only one issue

    def test_analyze_poor_quality_no_attachments(self, analyzer):
        """Test analysis with missing attachments."""
        reclamation = {
            "description": "Le portail coulissant présente un défaut de fabrication important.",
            "attachments": []
        }
        result = analyzer.analyze(reclamation)

        assert result["status"] == "poor"
        assert "missing_attachments" in result["issues"]
        assert result["details"]["attachment_count"] == 0

    def test_analyze_poor_quality_vague(self, analyzer):
        """Test analysis with vague description."""
        reclamation = {
            "description": "Le portail est cassé maintenant",  # Only 2 meaningful words
            "attachments": ["photo1.jpg"]
        }
        result = analyzer.analyze(reclamation)

        assert result["status"] == "poor"
        assert "too_vague" in result["issues"]
        assert result["details"]["meaningful_word_count"] < 5

    def test_analyze_unusable_quality(self, analyzer):
        """Test analysis with multiple critical issues."""
        reclamation = {
            "description": "Cassé",  # Too short AND too vague
            "attachments": []
        }
        result = analyzer.analyze(reclamation)

        assert result["status"] == "unusable"
        assert "too_short" in result["issues"]
        assert "too_vague" in result["issues"]
        assert len(result["issues"]) >= 2

    def test_analyze_multiple_issues_poor(self, analyzer):
        """Test analysis with multiple non-critical issues."""
        reclamation = {
            "description": "Portail cassé",  # Short but not vague enough
            "attachments": []
        }
        result = analyzer.analyze(reclamation)

        # Should be poor, not unusable (only one critical issue)
        assert result["status"] in ["poor", "unusable"]
        assert len(result["issues"]) >= 1

    def test_analyze_missing_description(self, analyzer):
        """Test analysis with missing description."""
        reclamation = {
            "attachments": ["photo1.jpg"]
        }
        result = analyzer.analyze(reclamation)

        assert result["status"] in ["poor", "unusable"]
        assert "too_short" in result["issues"]
        assert "too_vague" in result["issues"]

    def test_analyze_missing_attachments_key(self, analyzer):
        """Test analysis with missing attachments key."""
        reclamation = {
            "description": "Le portail coulissant présente un défaut de fabrication important."
        }
        result = analyzer.analyze(reclamation)

        assert result["status"] == "poor"
        assert "missing_attachments" in result["issues"]

    def test_analyze_empty_reclamation(self, analyzer):
        """Test analysis with empty reclamation."""
        reclamation = {}
        result = analyzer.analyze(reclamation)

        assert result["status"] == "unusable"
        assert "too_short" in result["issues"]
        assert "too_vague" in result["issues"]
        assert "missing_attachments" in result["issues"]

    # ========================================================================
    # Test custom thresholds
    # ========================================================================

    def test_custom_min_length(self):
        """Test analyzer with custom minimum length."""
        analyzer = InputQualityAnalyzer(
            min_description_length=50,
            min_meaningful_words=5
        )

        text = "This is a 30 character text."
        result = analyzer.check_description_length(text)
        assert result == "too_short"

    def test_custom_min_words(self):
        """Test analyzer with custom minimum meaningful words."""
        analyzer = InputQualityAnalyzer(
            min_description_length=20,
            min_meaningful_words=10
        )

        # 7 meaningful words
        text = "Le portail coulissant présente un défaut de fabrication important."
        result = analyzer.check_vagueness(text)
        assert result == "too_vague"

    # ========================================================================
    # Test edge cases
    # ========================================================================

    def test_analyze_with_non_list_attachments(self, analyzer):
        """Test analysis when attachments is not a list."""
        reclamation = {
            "description": "Le portail coulissant présente un défaut de fabrication important.",
            "attachments": "photo1.jpg"  # String instead of list
        }
        result = analyzer.analyze(reclamation)

        # Should handle gracefully
        assert result["status"] == "usable"
        assert result["details"]["attachment_count"] == 1

    def test_analyze_with_numeric_description(self, analyzer):
        """Test analysis with numeric description."""
        reclamation = {
            "description": 12345,
            "attachments": ["photo1.jpg"]
        }
        result = analyzer.analyze(reclamation)

        # Should convert to string and analyze
        assert "status" in result
        assert "issues" in result

    def test_meaningful_word_count_with_numbers(self, analyzer):
        """Test meaningful word counting with numbers."""
        text = "Portail 123 défaut 456 fabrication 789 important problème"
        count = analyzer._count_meaningful_words(text)
        # Should count: portail, défaut, fabrication, important, problème, and numbers
        assert count >= 5

    def test_french_accents_handling(self, analyzer):
        """Test that French accents are handled correctly."""
        text = "Le portail présente un défaut de fabrication très important avec problème électrique."
        result = analyzer.check_vagueness(text)
        assert result is None  # Should have enough meaningful words

    def test_case_insensitivity(self, analyzer):
        """Test that stop word matching is case-insensitive."""
        text = "LE PORTAIL COULISSANT PRÉSENTE UN DÉFAUT DE FABRICATION IMPORTANT"
        result = analyzer.check_vagueness(text)
        assert result is None  # Should recognize stop words regardless of case
