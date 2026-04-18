"""
Demo script to test the Predictor module with trained models.
"""

import logging

from sav_copilot.trainer import ModelTrainer
from sav_copilot.predictor import Predictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Demo the predictor with trained models."""
    logger.info("=" * 60)
    logger.info("SAV Copilot - Predictor Demo")
    logger.info("=" * 60)

    # Load trained models
    logger.info("\n1. Loading trained models...")
    trainer = ModelTrainer(models_dir="models")
    success = trainer.load_models()

    if not success:
        logger.error(
            "Failed to load models. Please run demo_trainer.py first.")
        return

    logger.info(
        f"Loaded models for targets: {list(trainer.vectorizers.keys())}")

    # Create predictor
    logger.info("\n2. Creating predictor...")
    predictor = Predictor(trainer)

    # Test cases
    test_cases = [
        {
            "description": "Portail coulissant défectueux avec rouille",
            "label": "Case 1: Defective sliding gate with rust"
        },
        {
            "description": "Usure normale du produit après 10 ans",
            "label": "Case 2: Normal wear after 10 years"
        },
        {
            "description": "Installation non conforme causant des problèmes",
            "label": "Case 3: Non-compliant installation"
        },
        {
            "description": "Pièce cassée nécessitant remplacement urgent",
            "label": "Case 4: Broken part requiring urgent replacement"
        }
    ]

    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Test Case {i}: {test_case['label']}")
        logger.info(f"Description: {test_case['description']}")
        logger.info(f"{'=' * 60}")

        # Predict all targets
        result = predictor.predict_all(test_case['description'])

        # Display results
        logger.info("\nPredictions:")
        logger.info("-" * 60)

        # Litige type
        litige = result['litige_type']
        logger.info(
            f"Litige Type: {litige['prediction']} "
            f"(confidence: {litige['confidence']:.3f}, "
            f"available: {litige['available']})"
        )

        # Responsibility
        resp = result['responsibility']
        logger.info(
            f"Responsibility: {resp['prediction']} "
            f"(confidence: {resp['confidence']:.3f}, "
            f"available: {resp['available']})"
        )

        # Product detail
        product = result['product_detail']
        logger.info(
            f"Product Detail: {product['prediction']} "
            f"(confidence: {product['confidence']:.3f}, "
            f"available: {product['available']})"
        )

        # Solution
        solution = result['solution']
        logger.info(
            f"Solution: {solution['prediction']} "
            f"(confidence: {solution['confidence']:.3f}, "
            f"available: {solution['available']})"
        )

        # Top 3 solutions
        if solution['top_3']:
            logger.info("\nTop 3 Solution Candidates:")
            for j, candidate in enumerate(solution['top_3'], 1):
                logger.info(
                    f"  {j}. {candidate['label']} "
                    f"(confidence: {candidate['confidence']:.3f})"
                )

    # Test individual predictions
    logger.info(f"\n{'=' * 60}")
    logger.info("Testing Individual Predictions")
    logger.info(f"{'=' * 60}")

    test_text = "Portail avec défaut de fabrication"
    logger.info(f"\nTest text: {test_text}")

    # Test predict_single for each target
    targets = ["litige", "responsibility", "product", "solution"]
    for target in targets:
        result = predictor.predict_single(test_text, target)
        logger.info(
            f"{target}: {result['prediction']} "
            f"(confidence: {result['confidence']:.3f})"
        )

    # Test predict_top_k
    logger.info(f"\n{'=' * 60}")
    logger.info("Testing Top-K Predictions")
    logger.info(f"{'=' * 60}")

    logger.info(f"\nTest text: {test_text}")
    logger.info("\nTop 5 solutions:")

    top_5 = predictor.predict_top_k(test_text, "solution", k=5)
    for i, candidate in enumerate(top_5, 1):
        logger.info(
            f"  {i}. {candidate['label']} "
            f"(confidence: {candidate['confidence']:.3f})"
        )

    # Test with unavailable model
    logger.info(f"\n{'=' * 60}")
    logger.info("Testing Fallback Behavior")
    logger.info(f"{'=' * 60}")

    result = predictor.predict_single(test_text, "nonexistent_target")
    logger.info(
        f"\nPrediction for nonexistent target: {result['prediction']} "
        f"(confidence: {result['confidence']:.3f}, "
        f"available: {result['available']})"
    )

    logger.info(f"\n{'=' * 60}")
    logger.info("Demo Complete!")
    logger.info(f"{'=' * 60}")


if __name__ == "__main__":
    main()
