"""
Demo script to test the Predictor with Preprocessor integration.
"""

import logging

from sav_copilot.trainer import ModelTrainer
from sav_copilot.predictor import Predictor
from sav_copilot.preprocessor import Preprocessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Demo the predictor with preprocessing."""
    logger.info("=" * 60)
    logger.info("SAV Copilot - Predictor with Preprocessing Demo")
    logger.info("=" * 60)

    # Load trained models
    logger.info("\n1. Loading trained models...")
    trainer = ModelTrainer(models_dir="models")
    success = trainer.load_models()

    if not success:
        logger.error(
            "Failed to load models. Please run demo_trainer.py first.")
        return

    # Create predictor and preprocessor
    logger.info("\n2. Creating predictor and preprocessor...")
    predictor = Predictor(trainer)
    preprocessor = Preprocessor()

    # Test cases with messy input
    test_cases = [
        {
            "raw_text": "  Portail   coulissant   défectueux  \n\n  avec   rouille  ",
            "label": "Case 1: Text with extra whitespace"
        },
        {
            "raw_text": "Usure\nnormale\ndu\nproduit\naprès\n10\nans",
            "label": "Case 2: Text with line breaks"
        },
        {
            "raw_text": "   Installation    non    conforme    ",
            "label": "Case 3: Text with multiple spaces"
        }
    ]

    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Test Case {i}: {test_case['label']}")
        logger.info(f"{'=' * 60}")

        raw_text = test_case['raw_text']
        logger.info(f"Raw text: {repr(raw_text)}")

        # Preprocess text
        normalized_text = preprocessor.preprocess_for_prediction(raw_text)
        logger.info(f"Normalized text: {repr(normalized_text)}")

        # Predict with normalized text
        result = predictor.predict_all(normalized_text)

        # Display key predictions
        logger.info("\nPredictions:")
        logger.info(
            f"  Litige: {result['litige_type']['prediction']} "
            f"(confidence: {result['litige_type']['confidence']:.3f})"
        )
        logger.info(
            f"  Solution: {result['solution']['prediction']} "
            f"(confidence: {result['solution']['confidence']:.3f})"
        )

    logger.info(f"\n{'=' * 60}")
    logger.info("Demo Complete!")
    logger.info(f"{'=' * 60}")


if __name__ == "__main__":
    main()
