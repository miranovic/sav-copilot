"""
Demo script for ComplexityScorer module.

This script demonstrates the complexity scoring functionality with various scenarios.
"""

from sav_copilot.complexity_scorer import ComplexityScorer
from config import (
    QUALITY_USABLE,
    QUALITY_POOR,
    QUALITY_UNUSABLE,
    WARRANTY_HORS_GARANTIE,
    WARRANTY_INCERTAINE,
    WARRANTY_ELIGIBLE
)


def print_result(scenario_name: str, result: dict):
    """Print complexity scoring result in a readable format."""
    print(f"\n{'=' * 70}")
    print(f"Scenario: {scenario_name}")
    print(f"{'=' * 70}")
    print(f"Overall Score: {result['score']}")
    print(f"Priority Level: {result['priority']}")
    print(f"Complexity Level: {result['level']}")
    print(f"\nScore Breakdown:")
    for component, score in result['breakdown'].items():
        sign = '+' if score >= 0 else ''
        print(f"  {component:25s}: {sign}{score}")
    print(f"{'=' * 70}")


def main():
    """Run complexity scorer demonstrations."""
    print("\n" + "=" * 70)
    print("SAV Copilot - Complexity Scorer Demo")
    print("=" * 70)

    scorer = ComplexityScorer()

    # Scenario 1: Quick Win - Clear case with high confidence
    print("\n\n### SCENARIO 1: Quick Win Case ###")
    print("Description: Clear case with high confidence predictions and good quality")

    scenario1 = {
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
            "litige_type": {"prediction": "Défaut de fabrication", "confidence": 0.92, "available": True},
            "responsibility": {"prediction": "Fabricant", "confidence": 0.88, "available": True},
            "product_detail": {"prediction": "Portail coulissant", "confidence": 0.85, "available": True},
            "solution": {"prediction": "Remplacement pièce", "confidence": 0.91, "available": True}
        },
        "warranty": {
            "status": WARRANTY_HORS_GARANTIE,
            "reasons": ["Mention d'usure normale détectée"],
            "matched_patterns": {"normal_wear": ["usure"]}
        }
    }

    result1 = scorer.calculate(scenario1)
    print_result("Quick Win - Clear Case", result1)

    # Scenario 2: Standard Review - Moderate complexity
    print("\n\n### SCENARIO 2: Standard Review Case ###")
    print("Description: Moderate confidence with some quality issues")

    scenario2 = {
        "quality": {
            "status": QUALITY_POOR,
            "issues": ["too_short"],
            "details": {
                "attachment_count": 2,
                "description_length": 18,
                "meaningful_word_count": 4
            }
        },
        "predictions": {
            "litige_type": {"prediction": "Défaut de fabrication", "confidence": 0.65, "available": True},
            "responsibility": {"prediction": "Fabricant", "confidence": 0.58, "available": True},
            "product_detail": {"prediction": "Portail", "confidence": 0.52, "available": True},
            "solution": {"prediction": "Réparation", "confidence": 0.61, "available": True}
        },
        "warranty": {
            "status": WARRANTY_HORS_GARANTIE,
            "reasons": ["Mention de choc détecté"],
            "matched_patterns": {"handling_damage": ["choc"]}
        }
    }

    result2 = scorer.calculate(scenario2)
    print_result("Standard Review - Moderate Complexity", result2)

    # Scenario 3: Expert Review - High complexity
    print("\n\n### SCENARIO 3: Expert Review Case ###")
    print("Description: Low confidence, poor quality, uncertain warranty")

    scenario3 = {
        "quality": {
            "status": QUALITY_UNUSABLE,
            "issues": ["too_short", "too_vague"],
            "details": {
                "attachment_count": 3,
                "description_length": 12,
                "meaningful_word_count": 2
            }
        },
        "predictions": {
            "litige_type": {"prediction": "Défaut", "confidence": 0.35, "available": True},
            "responsibility": {"prediction": "Fabricant", "confidence": 0.38, "available": True},
            "product_detail": {"prediction": "Portail", "confidence": 0.42, "available": True},
            "solution": {"prediction": "Remplacement", "confidence": 0.28, "available": True}
        },
        "warranty": {
            "status": WARRANTY_INCERTAINE,
            "reasons": ["Aucun motif d'exclusion évident détecté"],
            "matched_patterns": {}
        }
    }

    result3 = scorer.calculate(scenario3)
    print_result("Expert Review - High Complexity", result3)

    # Scenario 4: Contradictory Signals
    print("\n\n### SCENARIO 4: Contradictory Signals ###")
    print("Description: Mixed confidence levels indicating contradictory information")

    scenario4 = {
        "quality": {
            "status": QUALITY_USABLE,
            "issues": [],
            "details": {
                "attachment_count": 2,
                "description_length": 45,
                "meaningful_word_count": 8
            }
        },
        "predictions": {
            "litige_type": {"prediction": "Défaut de fabrication", "confidence": 0.89, "available": True},
            "responsibility": {"prediction": "Fabricant", "confidence": 0.32, "available": True},
            "product_detail": {"prediction": "Portail", "confidence": 0.75, "available": True},
            "solution": {"prediction": "Remplacement", "confidence": 0.85, "available": True}
        },
        "warranty": {
            "status": WARRANTY_HORS_GARANTIE,
            "reasons": ["Environnement agressif mentionné"],
            "matched_patterns": {"aggressive_environment": ["bord de mer"]}
        }
    }

    result4 = scorer.calculate(scenario4)
    print_result("Contradictory Signals", result4)

    # Scenario 5: Uncertain Warranty with Good Data
    print("\n\n### SCENARIO 5: Uncertain Warranty ###")
    print("Description: Good quality data but uncertain warranty status")

    scenario5 = {
        "quality": {
            "status": QUALITY_USABLE,
            "issues": [],
            "details": {
                "attachment_count": 1,
                "description_length": 60,
                "meaningful_word_count": 12
            }
        },
        "predictions": {
            "litige_type": {"prediction": "Défaut de fabrication", "confidence": 0.78, "available": True},
            "responsibility": {"prediction": "Fabricant", "confidence": 0.72, "available": True},
            "product_detail": {"prediction": "Portail", "confidence": 0.68, "available": True},
            "solution": {"prediction": "Remplacement", "confidence": 0.75, "available": True}
        },
        "warranty": {
            "status": WARRANTY_INCERTAINE,
            "reasons": ["Aucun motif d'exclusion évident détecté", "Analyse détaillée nécessaire"],
            "matched_patterns": {}
        }
    }

    result5 = scorer.calculate(scenario5)
    print_result("Uncertain Warranty with Good Data", result5)

    # Summary
    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\nComplexity Scoring Rules Applied:")
    print("  +2: Important data missing (unusable quality)")
    print("  +1: Multiple attachments present")
    print("  +2: Warranty status is uncertain")
    print("  +1: Solution confidence < 0.5")
    print("  +1: Responsibility confidence < 0.5")
    print("  -1: Solution confidence > 0.8")
    print("  -1: Case is very clear (all confidences > 0.8)")
    print("  +1: Contradictory signals detected")
    print("  +1: Input quality is poor")
    print("\nPriority Assignment:")
    print("  Score ≤ 1: quick_win (rapide)")
    print("  Score 2-3: standard_review (standard)")
    print("  Score ≥ 4: expert_review (complexe)")
    print("=" * 70)


if __name__ == "__main__":
    main()
