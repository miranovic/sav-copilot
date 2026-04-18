"""
Unit tests for MessageGenerator module.

Tests message generation logic for different scenarios:
- Need more info messages
- Warranty not applicable messages
- Reassurance fast case messages
- Message selection logic
"""

import pytest
from sav_copilot.message_generator import MessageGenerator
from config import (
    QUALITY_POOR,
    QUALITY_UNUSABLE,
    QUALITY_USABLE,
    WARRANTY_HORS_GARANTIE,
    WARRANTY_INCERTAINE,
    WARRANTY_ELIGIBLE,
    LEVEL_RAPIDE,
    LEVEL_STANDARD,
    LEVEL_COMPLEXE
)


class TestMessageGenerator:
    """Test suite for MessageGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a MessageGenerator instance for testing."""
        return MessageGenerator()

    # ========================================================================
    # Test: Need More Info Message Generation
    # ========================================================================

    def test_need_more_info_message_too_short(self, generator):
        """Test need_more_info message for too_short issue."""
        issues = ["too_short"]
        message = generator._need_more_info_message(issues)

        assert message is not None
        assert "Bonjour" in message
        assert "informations complémentaires" in message
        assert "description plus détaillée" in message
        assert "Cordialement" in message
        assert "Service Après-Vente" in message

    def test_need_more_info_message_missing_attachments(self, generator):
        """Test need_more_info message for missing_attachments issue."""
        issues = ["missing_attachments"]
        message = generator._need_more_info_message(issues)

        assert message is not None
        assert "photos ou documents" in message

    def test_need_more_info_message_too_vague(self, generator):
        """Test need_more_info message for too_vague issue."""
        issues = ["too_vague"]
        message = generator._need_more_info_message(issues)

        assert message is not None
        assert "précisions" in message
        assert "nature exacte" in message

    def test_need_more_info_message_multiple_issues(self, generator):
        """Test need_more_info message with multiple issues."""
        issues = ["too_short", "missing_attachments", "too_vague"]
        message = generator._need_more_info_message(issues)

        assert message is not None
        assert "description plus détaillée" in message
        assert "photos ou documents" in message
        assert "précisions" in message

    def test_need_more_info_message_empty_issues(self, generator):
        """Test need_more_info message with no specific issues."""
        issues = []
        message = generator._need_more_info_message(issues)

        assert message is not None
        assert "informations complémentaires" in message

    # ========================================================================
    # Test: Warranty Not Applicable Message Generation
    # ========================================================================

    def test_warranty_not_applicable_message_with_reasons(self, generator):
        """Test warranty_not_applicable message with specific reasons."""
        reasons = [
            "Mention d'usure normale détectée",
            "Mention d'environnement agressif détecté"
        ]
        message = generator._warranty_not_applicable_message(reasons)

        assert message is not None
        assert "Bonjour" in message
        assert "ne pas être couverte par la garantie" in message
        assert "usure normale" in message
        assert "environnement agressif" in message
        assert "conditions de garantie" in message
        assert "Cordialement" in message

    def test_warranty_not_applicable_message_empty_reasons(self, generator):
        """Test warranty_not_applicable message with no specific reasons."""
        reasons = []
        message = generator._warranty_not_applicable_message(reasons)

        assert message is not None
        assert "ne pas être couverte par la garantie" in message
        assert "hors garantie" in message

    def test_warranty_not_applicable_message_single_reason(self, generator):
        """Test warranty_not_applicable message with single reason."""
        reasons = ["Mention de choc détecté"]
        message = generator._warranty_not_applicable_message(reasons)

        assert message is not None
        assert "choc" in message

    # ========================================================================
    # Test: Reassurance Fast Case Message Generation
    # ========================================================================

    def test_reassurance_fast_case_message(self, generator):
        """Test reassurance_fast_case message generation."""
        message = generator._reassurance_fast_case_message()

        assert message is not None
        assert "Bonjour" in message
        assert "bien reçu votre réclamation" in message
        assert "dossier est clair" in message
        assert "traiter rapidement" in message
        assert "sous peu" in message
        assert "Cordialement" in message

    # ========================================================================
    # Test: Message Selection Logic
    # ========================================================================

    def test_generate_selects_need_more_info_for_poor_quality(self, generator):
        """Test that poor quality triggers need_more_info message."""
        analysis_result = {
            "quality": {
                "status": QUALITY_POOR,
                "issues": ["too_short"]
            },
            "warranty": {
                "status": WARRANTY_INCERTAINE,
                "reasons": []
            },
            "complexity": {
                "level": LEVEL_STANDARD
            },
            "predictions": {
                "solution": {"confidence": 0.8}
            }
        }

        message = generator.generate(analysis_result)

        assert message is not None
        assert "informations complémentaires" in message

    def test_generate_selects_need_more_info_for_unusable_quality(self, generator):
        """Test that unusable quality triggers need_more_info message."""
        analysis_result = {
            "quality": {
                "status": QUALITY_UNUSABLE,
                "issues": ["too_short", "too_vague"]
            },
            "warranty": {
                "status": WARRANTY_INCERTAINE,
                "reasons": []
            },
            "complexity": {
                "level": LEVEL_STANDARD
            },
            "predictions": {
                "solution": {"confidence": 0.8}
            }
        }

        message = generator.generate(analysis_result)

        assert message is not None
        assert "informations complémentaires" in message

    def test_generate_selects_warranty_not_applicable(self, generator):
        """Test that hors_garantie_probable triggers warranty message."""
        analysis_result = {
            "quality": {
                "status": QUALITY_USABLE,
                "issues": []
            },
            "warranty": {
                "status": WARRANTY_HORS_GARANTIE,
                "reasons": ["Mention d'usure normale détectée"]
            },
            "complexity": {
                "level": LEVEL_STANDARD
            },
            "predictions": {
                "solution": {"confidence": 0.8}
            }
        }

        message = generator.generate(analysis_result)

        assert message is not None
        assert "ne pas être couverte par la garantie" in message

    def test_generate_selects_reassurance_for_quick_win(self, generator):
        """Test that quick-win cases trigger reassurance message."""
        analysis_result = {
            "quality": {
                "status": QUALITY_USABLE,
                "issues": []
            },
            "warranty": {
                "status": WARRANTY_INCERTAINE,
                "reasons": []
            },
            "complexity": {
                "level": LEVEL_RAPIDE
            },
            "predictions": {
                "solution": {"confidence": 0.85}
            }
        }

        message = generator.generate(analysis_result)

        assert message is not None
        assert "dossier est clair" in message
        assert "traiter rapidement" in message

    def test_generate_returns_none_for_standard_case(self, generator):
        """Test that standard cases return no automatic message."""
        analysis_result = {
            "quality": {
                "status": QUALITY_USABLE,
                "issues": []
            },
            "warranty": {
                "status": WARRANTY_INCERTAINE,
                "reasons": []
            },
            "complexity": {
                "level": LEVEL_STANDARD
            },
            "predictions": {
                "solution": {"confidence": 0.6}
            }
        }

        message = generator.generate(analysis_result)

        assert message is None

    def test_generate_returns_none_for_complex_case(self, generator):
        """Test that complex cases return no automatic message."""
        analysis_result = {
            "quality": {
                "status": QUALITY_USABLE,
                "issues": []
            },
            "warranty": {
                "status": WARRANTY_INCERTAINE,
                "reasons": []
            },
            "complexity": {
                "level": LEVEL_COMPLEXE
            },
            "predictions": {
                "solution": {"confidence": 0.4}
            }
        }

        message = generator.generate(analysis_result)

        assert message is None

    def test_generate_prioritizes_quality_over_warranty(self, generator):
        """Test that quality issues take priority over warranty messages."""
        analysis_result = {
            "quality": {
                "status": QUALITY_POOR,
                "issues": ["too_short"]
            },
            "warranty": {
                "status": WARRANTY_HORS_GARANTIE,
                "reasons": ["Mention d'usure normale détectée"]
            },
            "complexity": {
                "level": LEVEL_STANDARD
            },
            "predictions": {
                "solution": {"confidence": 0.8}
            }
        }

        message = generator.generate(analysis_result)

        # Should get need_more_info, not warranty message
        assert message is not None
        assert "informations complémentaires" in message
        assert "garantie" not in message

    def test_generate_no_reassurance_for_low_confidence_quick_win(self, generator):
        """Test that quick-win with low confidence doesn't get reassurance."""
        analysis_result = {
            "quality": {
                "status": QUALITY_USABLE,
                "issues": []
            },
            "warranty": {
                "status": WARRANTY_INCERTAINE,
                "reasons": []
            },
            "complexity": {
                "level": LEVEL_RAPIDE
            },
            "predictions": {
                "solution": {"confidence": 0.5}  # Too low
            }
        }

        message = generator.generate(analysis_result)

        # Should not get reassurance message
        assert message is None

    def test_generate_handles_missing_fields_gracefully(self, generator):
        """Test that generator handles missing fields without crashing."""
        analysis_result = {
            "quality": {},
            "warranty": {},
            "complexity": {},
            "predictions": {}
        }

        # Should not crash, should return None
        message = generator.generate(analysis_result)
        assert message is None

    # ========================================================================
    # Test: Message Content Quality
    # ========================================================================

    def test_all_messages_are_professional_french(self, generator):
        """Test that all messages are in professional French."""
        # Test need_more_info
        msg1 = generator._need_more_info_message(["too_short"])
        assert "Bonjour" in msg1
        assert "Cordialement" in msg1
        assert "Service Après-Vente" in msg1

        # Test warranty_not_applicable
        msg2 = generator._warranty_not_applicable_message(
            ["Test reason"])
        assert "Bonjour" in msg2
        assert "Cordialement" in msg2
        assert "Service Après-Vente" in msg2

        # Test reassurance_fast_case
        msg3 = generator._reassurance_fast_case_message()
        assert "Bonjour" in msg3
        assert "Cordialement" in msg3
        assert "Service Après-Vente" in msg3

    def test_warranty_message_avoids_definitive_decisions(self, generator):
        """Test that warranty messages avoid definitive legal decisions."""
        reasons = ["Mention d'usure normale détectée"]
        message = generator._warranty_not_applicable_message(reasons)

        # Should use cautious language
        assert "semble" in message or "pourrait" in message
        # Should not make definitive statements
        assert "n'est pas couverte" not in message
        assert "est refusée" not in message
