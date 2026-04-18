"""
Verification Script for Business Logic Components

This script tests the integration of:
- InputQualityAnalyzer
- WarrantyEngine
- ComplexityScorer
- MessageGenerator

It runs various test scenarios to ensure components work correctly together.
"""

import logging
from typing import Dict, Any

from sav_copilot.quality_analyzer import InputQualityAnalyzer
from sav_copilot.warranty_engine import WarrantyEngine
from sav_copilot.complexity_scorer import ComplexityScorer
from sav_copilot.message_generator import MessageGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_scenarios():
    """Create test scenarios covering various cases."""
    scenarios = [
        {
            "name": "Quick Win - Clear Case",
            "reclamation": {
                "description": "Le portail coulissant ne ferme plus correctement depuis hier. "
                               "Le rail semble déformé et le portail reste bloqué à mi-course. "
                               "Installation récente (3 mois). Aucun choc constaté.",
                "attachments": ["photo1.jpg", "photo2.jpg"]
            },
            "predictions": {
                "litige_type": {"prediction": "Défaut de fabrication", "confidence": 0.92},
                "responsibility": {"prediction": "Fabricant", "confidence": 0.88},
                "product_detail": {"prediction": "Portail coulissant", "confidence": 0.95},
                "solution": {"prediction": "Remplacement pièce", "confidence": 0.85}
            },
            "expected": {
                "quality_status": "usable",
                "warranty_status": "incertaine",
                "complexity_level": "rapide",
                "message_type": "reassurance"
            }
        },
        {
            "name": "Poor Quality - Missing Info",
            "reclamation": {
                "description": "Problème portail",
                "attachments": []
            },
            "predictions": {
                "litige_type": {"prediction": "Défaut de fabrication", "confidence": 0.45},
                "responsibility": {"prediction": "Fabricant", "confidence": 0.38},
                "product_detail": {"prediction": "Portail", "confidence": 0.52},
                "solution": {"prediction": "Remplacement pièce", "confidence": 0.41}
            },
            "expected": {
                "quality_status": "poor",
                "complexity_level": "complexe",
                "message_type": "need_more_info"
            }
        },
        {
            "name": "Warranty Exclusion - Normal Wear",
            "reclamation": {
                "description": "Mon portail installé il y a 8 ans présente une usure normale "
                               "et une décoloration due au vieillissement. La peinture est patinée "
                               "et quelques traces de rouille apparaissent.",
                "attachments": ["photo1.jpg"]
            },
            "predictions": {
                "litige_type": {"prediction": "Défaut d'aspect", "confidence": 0.78},
                "responsibility": {"prediction": "Client", "confidence": 0.72},
                "product_detail": {"prediction": "Portail", "confidence": 0.85},
                "solution": {"prediction": "Hors garantie", "confidence": 0.81}
            },
            "expected": {
                "quality_status": "usable",
                "warranty_status": "hors_garantie_probable",
                "message_type": "warranty_not_applicable"
            }
        },
        {
            "name": "Warranty Exclusion - Poor Maintenance",
            "reclamation": {
                "description": "Le portail ne fonctionne plus. Il n'a jamais été entretenu "
                               "depuis l'installation il y a 5 ans. Mauvais entretien probable.",
                "attachments": ["photo1.jpg"]
            },
            "predictions": {
                "litige_type": {"prediction": "Défaut fonctionnel", "confidence": 0.68},
                "responsibility": {"prediction": "Client", "confidence": 0.75},
                "product_detail": {"prediction": "Portail", "confidence": 0.82},
                "solution": {"prediction": "Hors garantie", "confidence": 0.79}
            },
            "expected": {
                "quality_status": "usable",
                "warranty_status": "hors_garantie_probable",
                "message_type": "warranty_not_applicable"
            }
        },
        {
            "name": "Warranty Exclusion - Handling Damage",
            "reclamation": {
                "description": "Suite à un choc avec la voiture, le portail présente une rayure "
                               "importante et une déformation. Impact visible sur le panneau.",
                "attachments": ["photo1.jpg", "photo2.jpg"]
            },
            "predictions": {
                "litige_type": {"prediction": "Dommage physique", "confidence": 0.91},
                "responsibility": {"prediction": "Client", "confidence": 0.88},
                "product_detail": {"prediction": "Portail", "confidence": 0.93},
                "solution": {"prediction": "Hors garantie", "confidence": 0.87}
            },
            "expected": {
                "quality_status": "usable",
                "warranty_status": "hors_garantie_probable",
                "message_type": "warranty_not_applicable"
            }
        },
        {
            "name": "Warranty Exclusion - Aggressive Environment",
            "reclamation": {
                "description": "Portail installé en bord de mer. Corrosion importante due à "
                               "l'environnement agressif et l'air marin. Oxydation visible.",
                "attachments": ["photo1.jpg"]
            },
            "predictions": {
                "litige_type": {"prediction": "Corrosion", "confidence": 0.89},
                "responsibility": {"prediction": "Environnement", "confidence": 0.82},
                "product_detail": {"prediction": "Portail", "confidence": 0.87},
                "solution": {"prediction": "Hors garantie", "confidence": 0.84}
            },
            "expected": {
                "quality_status": "usable",
                "warranty_status": "hors_garantie_probable",
                "message_type": "warranty_not_applicable"
            }
        },
        {
            "name": "Warranty Exclusion - Hardware/Accessories",
            "reclamation": {
                "description": "La télécommande du moteur ne fonctionne plus. Problème avec "
                               "la carte électronique de la motorisation. Batterie à remplacer.",
                "attachments": ["photo1.jpg"]
            },
            "predictions": {
                "litige_type": {"prediction": "Défaut électronique", "confidence": 0.86},
                "responsibility": {"prediction": "Accessoire", "confidence": 0.79},
                "product_detail": {"prediction": "Motorisation", "confidence": 0.91},
                "solution": {"prediction": "Hors garantie", "confidence": 0.82}
            },
            "expected": {
                "quality_status": "usable",
                "warranty_status": "hors_garantie_probable",
                "message_type": "warranty_not_applicable"
            }
        },
        {
            "name": "Complex Case - Contradictory Signals",
            "reclamation": {
                "description": "Le portail présente un défaut de fermeture. Installation récente "
                               "mais quelques rayures visibles. Pas sûr de l'origine du problème.",
                "attachments": ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
            },
            "predictions": {
                "litige_type": {"prediction": "Défaut fonctionnel", "confidence": 0.85},
                "responsibility": {"prediction": "Fabricant", "confidence": 0.42},
                "product_detail": {"prediction": "Portail", "confidence": 0.78},
                "solution": {"prediction": "Expertise requise", "confidence": 0.38}
            },
            "expected": {
                "quality_status": "usable",
                "warranty_status": "hors_garantie_probable",
                "complexity_level": "complexe"
            }
        },
        {
            "name": "Standard Case - Moderate Confidence",
            "reclamation": {
                "description": "Le portail fait un bruit anormal lors de l'ouverture. "
                               "Cela a commencé il y a une semaine. Le portail fonctionne "
                               "mais le bruit est gênant.",
                "attachments": ["photo1.jpg"]
            },
            "predictions": {
                "litige_type": {"prediction": "Défaut fonctionnel", "confidence": 0.68},
                "responsibility": {"prediction": "Fabricant", "confidence": 0.62},
                "product_detail": {"prediction": "Portail", "confidence": 0.71},
                "solution": {"prediction": "Réparation", "confidence": 0.58}
            },
            "expected": {
                "quality_status": "usable",
                "warranty_status": "incertaine",
                "complexity_level": "standard"
            }
        },
        {
            "name": "Unusable Quality - Too Short and Vague",
            "reclamation": {
                "description": "Problème",
                "attachments": []
            },
            "predictions": {
                "litige_type": {"prediction": "Inconnu", "confidence": 0.25},
                "responsibility": {"prediction": "Inconnu", "confidence": 0.22},
                "product_detail": {"prediction": "Inconnu", "confidence": 0.28},
                "solution": {"prediction": "Information requise", "confidence": 0.31}
            },
            "expected": {
                "quality_status": "unusable",
                "complexity_level": "complexe",
                "message_type": "need_more_info"
            }
        }
    ]

    return scenarios


def run_scenario(scenario: Dict[str, Any],
                 quality_analyzer: InputQualityAnalyzer,
                 warranty_engine: WarrantyEngine,
                 complexity_scorer: ComplexityScorer,
                 message_generator: MessageGenerator) -> Dict[str, Any]:
    """Run a single test scenario through all components."""

    logger.info(f"\n{'='*80}")
    logger.info(f"Running Scenario: {scenario['name']}")
    logger.info(f"{'='*80}")

    reclamation = scenario["reclamation"]
    predictions = scenario["predictions"]

    # Step 1: Quality Analysis
    logger.info("\n--- Quality Analysis ---")
    quality = quality_analyzer.analyze(reclamation)
    logger.info(f"Status: {quality['status']}")
    logger.info(f"Issues: {quality['issues']}")
    logger.info(f"Details: {quality['details']}")

    # Step 2: Warranty Evaluation
    logger.info("\n--- Warranty Evaluation ---")
    warranty = warranty_engine.evaluate(reclamation["description"])
    logger.info(f"Status: {warranty['status']}")
    logger.info(f"Reasons: {warranty['reasons']}")
    logger.info(f"Matched Patterns: {warranty['matched_patterns']}")

    # Step 3: Complexity Scoring
    logger.info("\n--- Complexity Scoring ---")
    analysis_result = {
        "quality": quality,
        "predictions": predictions,
        "warranty": warranty
    }
    complexity = complexity_scorer.calculate(analysis_result)
    logger.info(f"Score: {complexity['score']}")
    logger.info(f"Level: {complexity['level']}")
    logger.info(f"Priority: {complexity['priority']}")
    logger.info(f"Breakdown: {complexity['breakdown']}")

    # Step 4: Message Generation
    logger.info("\n--- Message Generation ---")
    analysis_result["complexity"] = complexity
    message = message_generator.generate(analysis_result)
    if message:
        logger.info(f"Message Generated:\n{message}")
    else:
        logger.info("No automatic message generated (manual review required)")

    # Compile results
    results = {
        "quality": quality,
        "warranty": warranty,
        "complexity": complexity,
        "message": message,
        "scenario_name": scenario["name"]
    }

    return results


def verify_expectations(results: Dict[str, Any], expected: Dict[str, Any]) -> bool:
    """Verify that results match expected outcomes."""

    logger.info("\n--- Verification ---")
    all_passed = True

    # Check quality status
    if "quality_status" in expected:
        actual = results["quality"]["status"]
        expected_val = expected["quality_status"]
        passed = actual == expected_val
        all_passed = all_passed and passed
        status = "✓" if passed else "✗"
        logger.info(
            f"{status} Quality Status: expected={expected_val}, actual={actual}")

    # Check warranty status
    if "warranty_status" in expected:
        actual = results["warranty"]["status"]
        expected_val = expected["warranty_status"]
        passed = actual == expected_val
        all_passed = all_passed and passed
        status = "✓" if passed else "✗"
        logger.info(
            f"{status} Warranty Status: expected={expected_val}, actual={actual}")

    # Check complexity level
    if "complexity_level" in expected:
        actual = results["complexity"]["level"]
        expected_val = expected["complexity_level"]
        passed = actual == expected_val
        all_passed = all_passed and passed
        status = "✓" if passed else "✗"
        logger.info(
            f"{status} Complexity Level: expected={expected_val}, actual={actual}")

    # Check message type
    if "message_type" in expected:
        message = results["message"]
        expected_type = expected["message_type"]

        if expected_type == "need_more_info":
            passed = message is not None and "informations complémentaires" in message
        elif expected_type == "warranty_not_applicable":
            passed = message is not None and "ne pas être couverte par la garantie" in message
        elif expected_type == "reassurance":
            passed = message is not None and "traiter rapidement" in message
        else:
            passed = False

        all_passed = all_passed and passed
        status = "✓" if passed else "✗"
        logger.info(
            f"{status} Message Type: expected={expected_type}, generated={message is not None}")

    return all_passed


def main():
    """Main verification function."""

    logger.info("="*80)
    logger.info("Business Logic Components Verification")
    logger.info("="*80)

    # Initialize components
    logger.info("\nInitializing components...")
    quality_analyzer = InputQualityAnalyzer()
    warranty_engine = WarrantyEngine()
    complexity_scorer = ComplexityScorer()
    message_generator = MessageGenerator()
    logger.info("All components initialized successfully")

    # Load test scenarios
    scenarios = create_test_scenarios()
    logger.info(f"\nLoaded {len(scenarios)} test scenarios")

    # Run all scenarios
    results_summary = []
    for scenario in scenarios:
        results = run_scenario(
            scenario,
            quality_analyzer,
            warranty_engine,
            complexity_scorer,
            message_generator
        )

        # Verify expectations
        passed = verify_expectations(results, scenario["expected"])
        results_summary.append({
            "name": scenario["name"],
            "passed": passed
        })

    # Print summary
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION SUMMARY")
    logger.info("="*80)

    total = len(results_summary)
    passed = sum(1 for r in results_summary if r["passed"])
    failed = total - passed

    for result in results_summary:
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        logger.info(f"{status}: {result['name']}")

    logger.info(f"\nTotal: {total} scenarios")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")

    if failed == 0:
        logger.info("\n✓ All business logic components are working correctly!")
        return 0
    else:
        logger.warning(f"\n✗ {failed} scenario(s) failed verification")
        return 1


if __name__ == "__main__":
    exit(main())
