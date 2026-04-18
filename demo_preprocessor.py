"""
Demo script to verify preprocessor integration with data loader.
"""

import logging
import os
import pandas as pd

from sav_copilot.data_loader import DataLoader
from sav_copilot.preprocessor import Preprocessor
import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Demonstrate preprocessor functionality."""
    logger.info("=== SAV Copilot Preprocessor Demo ===\n")

    # Initialize components
    data_loader = DataLoader()
    preprocessor = Preprocessor()

    # Build paths
    training_excel_path = os.path.join(
        config.TRAINING_DATA_PATH,
        config.TRAINING_EXCEL_FILE
    )
    linking_csv_path = os.path.join(
        config.TRAINING_DATA_PATH,
        config.LINKING_CSV_FILE
    )
    referencing_path = os.path.join(
        config.WARRANTY_DOCS_PATH,
        config.GENERAL_REFERENCING_FILE
    )

    # Check if files exist
    if not os.path.exists(training_excel_path):
        logger.error(f"Training data not found at: {training_excel_path}")
        logger.info("Please ensure data files are in the correct location.")
        return

    # Load data
    logger.info("Step 1: Loading training data...")
    training_data = data_loader.load_training_data(training_excel_path)
    logger.info(f"Loaded {len(training_data)} records\n")

    # Display sample before preprocessing
    logger.info("Step 2: Sample data BEFORE preprocessing:")
    if 'description' in training_data.columns:
        sample_text = training_data['description'].iloc[0]
        logger.info(f"Sample description: {repr(sample_text[:100])}\n")

    # Preprocess data
    logger.info("Step 3: Preprocessing data...")
    text_column = 'description' if 'description' in training_data.columns else 'Description'

    # Define target columns
    target_columns = [
        'Type de litige',
        'Responsabilité',
        'Solution',
        'Précision produit'
    ]

    # Run preprocessing pipeline
    processed_data = preprocessor.preprocess_for_training(
        training_data,
        text_column,
        target_columns
    )

    logger.info(f"Preprocessing complete!\n")

    # Display results
    logger.info("Step 4: Sample data AFTER preprocessing:")
    feature_column = f"{text_column}_features"
    if feature_column in processed_data.columns:
        sample_features = processed_data[feature_column].iloc[0]
        logger.info(f"Sample features: {repr(sample_features[:100])}")
        logger.info(f"Feature length: {len(sample_features)} characters\n")

    # Show statistics
    logger.info("Step 5: Preprocessing statistics:")
    logger.info(f"Total records: {len(processed_data)}")
    logger.info(f"Columns: {len(processed_data.columns)}")

    if feature_column in processed_data.columns:
        non_empty = (processed_data[feature_column] != '').sum()
        logger.info(f"Non-empty features: {non_empty}/{len(processed_data)}")

        avg_length = processed_data[feature_column].str.len().mean()
        logger.info(f"Average feature length: {avg_length:.1f} characters")

    # Check target columns
    logger.info("\nStep 6: Target columns status:")
    for col in target_columns:
        if col in processed_data.columns:
            non_null = processed_data[col].notna().sum()
            logger.info(
                f"  ✓ {col}: {non_null}/{len(processed_data)} non-null values")
        else:
            logger.info(f"  ✗ {col}: NOT FOUND")

    # Test single text preprocessing
    logger.info("\nStep 7: Testing single text preprocessing:")
    test_text = "  Problème   d'étanchéité   sur   le   portail  \n\n  "
    normalized = preprocessor.preprocess_for_prediction(test_text)
    logger.info(f"Original: {repr(test_text)}")
    logger.info(f"Normalized: {repr(normalized)}")

    logger.info("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
