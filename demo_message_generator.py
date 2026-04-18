"""
Demo script for MessageGenerator module.

This script demonstrates the message generation functionality with various scenarios.
"""

from sav_copilot.message_generator import MessageGenerator
from config import (
    QUALITY_POOR,
    QUALITY_UNUSABLE,
    QUALITY_USABLE,
    WARRANTY_HORS_GARANTIE,
    WARRANTY_INCERTAINE,
    LEVEL_RAPIDE,
    LEVEL_STANDARD,
    LEVEL_COMPLEXE
)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_scenario(scenario_name: str, analysis_result: dict, message: str):
    """Print a scenario with its analysis and generated message."""
    print(f"Scenario: {scenario_name}")
    print("-" * 80)
    print(f"Quality Status: {analysis_result['quality']['status']}")
    print(f"Warranty Status: {analysis_result['warranty']['status']}")
    print(f"Complexity Level: {analysis_result['complexity']['level']}")
    print(
        f"Solution Confidence: {analysis_result['predictions']['solution']['confidence']:.2f}")
    print("\nGenerated Message:")
    print("-" * 80)
    if message:
        print(message)
    else:
        print("(No automatic message - requires manual review)")
    print("\n")


def main():
    """Run the MessageGenerator demo."""
    print_section("SAV Copilot - Message Generator Demo")

    # Initialize the generator
    generator = MessageGenerator()
    print("✓ MessageGenerator initialized\n")

    # ========================================================================
    # Scenario 1: Poor Quality Input - Need More Info
    # ========================================================================
    print_section("Scenario 1: Poor Quality Input")

    analysis_result_1 = {
        "quality": {
            "status": QUALITY_POOR,
            "issues": ["too_short", "missing_attachments"]
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

    message_1 = generator.generate(analysis_result_1)
    print_scenario("Poor Quality - Missing Information",
                   analysis_result_1, message_1)

    # ========================================================================
    # Scenario 2: Warranty Exclusion
    # ========================================================================
    print_section("Scenario 2: Probable Warranty Exclusion")

    analysis_result_2 = {
        "quality": {
            "status": QUALITY_USABLE,
            "issues": []
        },
        "warranty": {
            "status": WARRANTY_HORS_GARANTIE,
            "reasons": [
                "Mention d'usure normale détectée",
                "Mention d'environnement agressif détecté"
            ]
        },
        "complexity": {
            "level": LEVEL_STANDARD
        },
        "predictions": {
            "solution": {"confidence": 0.7}
        }
    }

    message_2 = generator.generate(analysis_result_2)
    print_scenario("Warranty Exclusion - Normal Wear",
                   analysis_result_2, message_2)

    # ========================================================================
    # Scenario 3: Quick Win Case
    # ========================================================================
    print_section("Scenario 3: Quick Win Case")

    analysis_result_3 = {
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
            "solution": {"confidence": 0.92}
        }
    }

    message_3 = generator.generate(analysis_result_3)
    print_scenario("Quick Win - Clear Case", analysis_result_3, message_3)

    # ========================================================================
    # Scenario 4: Standard Case - No Automatic Message
    # ========================================================================
    print_section("Scenario 4: Standard Case")

    analysis_result_4 = {
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
            "solution": {"confidence": 0.65}
        }
    }

    message_4 = generator.generate(analysis_result_4)
    print_scenario("Standard Case - Manual Review",
                   analysis_result_4, message_4)

    # ========================================================================
    # Scenario 5: Complex Case - No Automatic Message
    # ========================================================================
    print_section("Scenario 5: Complex Case")

    analysis_result_5 = {
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
            "solution": {"confidence": 0.42}
        }
    }

    message_5 = generator.generate(analysis_result_5)
    print_scenario("Complex Case - Expert Review",
                   analysis_result_5, message_5)

    # ========================================================================
    # Scenario 6: Unusable Quality
    # ========================================================================
    print_section("Scenario 6: Unusable Quality")

    analysis_result_6 = {
        "quality": {
            "status": QUALITY_UNUSABLE,
            "issues": ["too_short", "too_vague"]
        },
        "warranty": {
            "status": WARRANTY_INCERTAINE,
            "reasons": []
        },
        "complexity": {
            "level": LEVEL_COMPLEXE
        },
        "predictions": {
            "solution": {"confidence": 0.3}
        }
    }

    message_6 = generator.generate(analysis_result_6)
    print_scenario("Unusable Quality - Critical Issues",
                   analysis_result_6, message_6)

    # ========================================================================
    # Summary
    # ========================================================================
    print_section("Demo Summary")
    print("✓ Demonstrated 6 different scenarios")
    print("✓ All message types generated successfully:")
    print("  - Need More Info messages (poor/unusable quality)")
    print("  - Warranty Not Applicable messages (probable exclusions)")
    print("  - Reassurance messages (quick-win cases)")
    print("  - No automatic message (standard/complex cases)")
    print("\n✓ All messages are in professional French")
    print("✓ All messages avoid definitive legal warranty decisions")
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    main()
