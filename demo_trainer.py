"""
Demo script to test the ModelTrainer with real data.

This script demonstrates:
1. Loading training data
2. Preprocessing the data
3. Training classifiers for all targets
4. Saving models to disk
5. Loading models and making predictions
"""

import logging
import os
import sys

import pandas as pd

from sav_copilot.data_loader import DataLoader
from sav_copilot.preprocessor import Preprocessor
from sav_copilot.trainer import ModelTrainer
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the trainer demo."""
    logger.info("=" * 80)
    logger.info("SAV Copilot - Model Trainer Demo")
    logger.info("=" * 80)

    # Step 1: Load training data
    logger.info("\n[Step 1] Loading training data...")
    try:
        loader = DataLoader()

        # Build path to training data
        training_path = os.path.join(
            config.TRAINING_DATA_PATH,
            config.TRAINING_EXCEL_FILE
        )
        logger.info(f"Loading from: {training_path}")

        df = loader.load_training_data(training_path)
        logger.info(f"Loaded {len(df)} training samples")
        logger.info(f"Columns: {list(df.columns)}")
    except Exception as e:
        logger.error(f"Failed to load training data: {e}")
        return 1

    # Step 2: Preprocess data
    logger.info("\n[Step 2] Preprocessing data...")
    try:
        preprocessor = Preprocessor()

        # Get target columns from config
        target_columns = list(config.TARGET_COLUMNS.values())
        logger.info(f"Target columns: {target_columns}")

        # Preprocess for training
        df = preprocessor.preprocess_for_training(
            df=df,
            text_column=config.TEXT_COLUMN,
            target_columns=target_columns
        )

        # Use the features column created by preprocessing
        text_column = f"{config.TEXT_COLUMN}_features"
        logger.info(f"Using text column: {text_column}")

    except Exception as e:
        logger.error(f"Failed to preprocess data: {e}")
        return 1

    # Step 3: Train models
    logger.info("\n[Step 3] Training classifiers...")
    try:
        trainer = ModelTrainer(models_dir=config.MODELS_DIR)

        # Check if models already exist
        if trainer.load_models():
            logger.info("Existing models found and loaded successfully")
            logger.info(
                f"Loaded models for targets: {list(trainer.vectorizers.keys())}")

            # Ask user if they want to retrain
            response = input("\nRetrain models? (y/n): ").strip().lower()
            if response != 'y':
                logger.info("Skipping training, using existing models")
            else:
                logger.info("Retraining models...")
                trainer.train_all(
                    df=df,
                    text_column=text_column,
                    target_columns=target_columns
                )
                trainer.save_models()
                logger.info("Models retrained and saved")
        else:
            logger.info("No existing models found, training new models...")
            trainer.train_all(
                df=df,
                text_column=text_column,
                target_columns=target_columns
            )
            trainer.save_models()
            logger.info("Models trained and saved")

    except Exception as e:
        logger.error(f"Failed to train models: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Step 4: Display model information
    logger.info("\n[Step 4] Model Information:")
    for target_name in trainer.vectorizers.keys():
        logger.info(f"\nTarget: {target_name}")
        if target_name in trainer.metadata:
            metadata = trainer.metadata[target_name]
            logger.info(
                f"  Training date: {metadata.get('training_date', 'N/A')}")
            logger.info(f"  Samples: {metadata.get('n_samples', 'N/A')}")
            logger.info(f"  Features: {metadata.get('n_features', 'N/A')}")
            logger.info(f"  Classes: {metadata.get('n_classes', 'N/A')}")
            logger.info(f"  Class distribution:")
            class_counts = metadata.get('class_counts', {})
            for label, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                logger.info(f"    {label}: {count}")
            if len(class_counts) > 5:
                logger.info(
                    f"    ... and {len(class_counts) - 5} more classes")

    # Step 5: Test predictions
    logger.info("\n[Step 5] Testing predictions...")
    test_cases = [
        "Portail coulissant défectueux avec problème de rouille",
        "Défaut de fabrication sur la clôture",
        "Usure normale du produit après plusieurs années"
    ]

    for i, test_text in enumerate(test_cases, 1):
        logger.info(f"\nTest case {i}: {test_text}")

        # Preprocess test text
        test_text_clean = preprocessor.preprocess_for_prediction(test_text)

        # Make predictions for each target
        for target_name in trainer.vectorizers.keys():
            try:
                vectorizer = trainer.vectorizers[target_name]
                classifier = trainer.classifiers[target_name]

                # Transform and predict
                X_test = vectorizer.transform([test_text_clean])
                prediction = classifier.predict(X_test)[0]
                probabilities = classifier.predict_proba(X_test)[0]
                confidence = probabilities.max()

                logger.info(
                    f"  {target_name}: {prediction} (confidence: {confidence:.2f})")

            except Exception as e:
                logger.error(f"  Failed to predict {target_name}: {e}")

    logger.info("\n" + "=" * 80)
    logger.info("Demo complete!")
    logger.info("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
