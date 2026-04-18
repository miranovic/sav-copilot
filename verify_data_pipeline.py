"""
Checkpoint verification script for Task 4: Verify data pipeline.

This script verifies that the DataLoader and Preprocessor modules work together
correctly by loading sample data and preprocessing it end-to-end.
"""

import logging
import os
import sys
from pathlib import Path

from sav_copilot.data_loader import DataLoader
from sav_copilot.preprocessor import Preprocessor
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def verify_data_loading():
    """Verify data loading functionality."""
    logger.info("=" * 70)
    logger.info("CHECKPOINT 1: Data Loading Verification")
    logger.info("=" * 70)

    loader = DataLoader()

    # Build paths
    training_path = Path(config.TRAINING_DATA_PATH) / \
        config.TRAINING_EXCEL_FILE
    linking_path = Path(config.TRAINING_DATA_PATH) / config.LINKING_CSV_FILE
    referencing_path = Path(config.WARRANTY_DOCS_PATH) / \
        config.GENERAL_REFERENCING_FILE

    logger.info(f"Training data path: {training_path}")
    logger.info(f"Linking table path: {linking_path}")
    logger.info(f"General referencing path: {referencing_path}")

    # Check if files exist
    if not training_path.exists():
        logger.error(f"❌ Training data file not found: {training_path}")
        return None

    logger.info("✓ Training data file exists")

    # Load all data
    try:
        data = loader.load_all(
            str(training_path),
            str(linking_path),
            str(referencing_path)
        )

        logger.info(f"✓ Successfully loaded all data sources")
        logger.info(f"  - Training records: {len(data['training'])}")
        logger.info(f"  - Attachment links: {len(data['linking'])}")
        logger.info(f"  - Reference entries: {len(data['referencing'])}")
        logger.info(f"  - Merged records: {len(data['merged'])}")

        # Verify merged data has attachments
        total_attachments = data['merged']['attachment_count'].sum()
        records_with_attachments = (
            data['merged']['attachment_count'] > 0).sum()
        logger.info(f"  - Total attachments: {total_attachments}")
        logger.info(
            f"  - Records with attachments: {records_with_attachments}")

        return data

    except Exception as e:
        logger.error(f"❌ Error loading data: {e}", exc_info=True)
        return None


def verify_preprocessing(data):
    """Verify preprocessing functionality."""
    logger.info("\n" + "=" * 70)
    logger.info("CHECKPOINT 2: Preprocessing Verification")
    logger.info("=" * 70)

    if data is None:
        logger.error("❌ Cannot verify preprocessing: data loading failed")
        return None

    preprocessor = Preprocessor()
    merged_data = data['merged']

    # Determine text column
    text_column = None
    for col in ['description', 'Description', 'desc']:
        if col in merged_data.columns:
            text_column = col
            break

    if text_column is None:
        logger.error("❌ No description column found in data")
        return None

    logger.info(f"✓ Using text column: '{text_column}'")

    # Define target columns
    target_columns = [
        'Type de litige',
        'Responsabilité',
        'Solution',
        'Précision produit'
    ]

    # Run preprocessing pipeline
    try:
        processed_data = preprocessor.preprocess_for_training(
            merged_data,
            text_column,
            target_columns
        )

        logger.info(f"✓ Preprocessing completed successfully")
        logger.info(f"  - Total records: {len(processed_data)}")
        logger.info(f"  - Total columns: {len(processed_data.columns)}")

        # Verify feature column was created
        feature_column = f"{text_column}_features"
        if feature_column in processed_data.columns:
            logger.info(f"✓ Feature column created: '{feature_column}'")

            # Statistics
            non_empty = (processed_data[feature_column] != '').sum()
            avg_length = processed_data[feature_column].str.len().mean()
            logger.info(
                f"  - Non-empty features: {non_empty}/{len(processed_data)}")
            logger.info(
                f"  - Average feature length: {avg_length:.1f} characters")
        else:
            logger.error(f"❌ Feature column not created: '{feature_column}'")
            return None

        # Verify original data preserved
        original_column = f"{text_column}_original"
        if original_column in processed_data.columns:
            logger.info(f"✓ Original data preserved: '{original_column}'")
        else:
            logger.warning(
                f"⚠ Original data column not found: '{original_column}'")

        # Verify target columns
        logger.info("\nTarget columns status:")
        all_targets_present = True
        for col in target_columns:
            if col in processed_data.columns:
                non_null = processed_data[col].notna().sum()
                logger.info(
                    f"  ✓ {col}: {non_null}/{len(processed_data)} non-null values")
            else:
                logger.warning(f"  ⚠ {col}: NOT FOUND")
                all_targets_present = False

        if all_targets_present:
            logger.info("✓ All target columns present")
        else:
            logger.warning(
                "⚠ Some target columns missing (may need flexible matching)")

        return processed_data

    except Exception as e:
        logger.error(f"❌ Error during preprocessing: {e}", exc_info=True)
        return None


def verify_sample_records(processed_data):
    """Verify sample records to ensure data quality."""
    logger.info("\n" + "=" * 70)
    logger.info("CHECKPOINT 3: Sample Record Verification")
    logger.info("=" * 70)

    if processed_data is None:
        logger.error("❌ Cannot verify samples: preprocessing failed")
        return False

    # Get text column name
    text_column = None
    for col in ['description', 'Description', 'desc']:
        if col in processed_data.columns:
            text_column = col
            break

    if text_column is None:
        logger.error("❌ No text column found")
        return False

    feature_column = f"{text_column}_features"

    # Display 3 sample records
    num_samples = min(3, len(processed_data))
    logger.info(f"Displaying {num_samples} sample records:\n")

    for i in range(num_samples):
        sample = processed_data.iloc[i]
        logger.info(f"--- Sample {i+1} ---")
        logger.info(f"ID: {sample.get('identifiant', 'N/A')}")

        # Show original vs processed text
        if text_column in sample:
            original_text = str(sample[text_column])[:100]
            logger.info(f"Original text: {original_text}...")

        if feature_column in sample:
            processed_text = str(sample[feature_column])[:100]
            logger.info(f"Processed text: {processed_text}...")
            logger.info(
                f"Feature length: {len(str(sample[feature_column]))} chars")

        # Show target values
        logger.info(f"Type de litige: {sample.get('Type de litige', 'N/A')}")
        logger.info(f"Responsabilité: {sample.get('Responsabilité', 'N/A')}")
        logger.info(f"Solution: {sample.get('Solution', 'N/A')}")
        logger.info(f"Attachments: {sample.get('attachment_count', 0)}")
        logger.info("")

    logger.info("✓ Sample records verified")
    return True


def verify_text_normalization():
    """Verify text normalization with specific test cases."""
    logger.info("\n" + "=" * 70)
    logger.info("CHECKPOINT 4: Text Normalization Verification")
    logger.info("=" * 70)

    preprocessor = Preprocessor()

    test_cases = [
        {
            "input": "  Problème   d'étanchéité   sur   le   portail  \n\n  ",
            "expected_contains": ["Problème", "étanchéité", "portail"]
        },
        {
            "input": "Défaut\n\nde\n\nfabrication",
            "expected_contains": ["Défaut", "fabrication"]
        },
        {
            "input": "   Multiple    spaces    everywhere   ",
            "expected_contains": ["Multiple", "spaces", "everywhere"]
        }
    ]

    all_passed = True
    for i, test in enumerate(test_cases, 1):
        input_text = test["input"]
        expected_contains = test["expected_contains"]

        result = preprocessor.preprocess_for_prediction(input_text)

        logger.info(f"\nTest case {i}:")
        logger.info(f"  Input: {repr(input_text[:50])}")
        logger.info(f"  Output: {repr(result[:50])}")

        # Check if expected words are present
        passed = all(word in result for word in expected_contains)

        if passed:
            logger.info(f"  ✓ PASSED")
        else:
            logger.error(f"  ❌ FAILED: Expected words not found")
            all_passed = False

    if all_passed:
        logger.info("\n✓ All text normalization tests passed")
    else:
        logger.error("\n❌ Some text normalization tests failed")

    return all_passed


def verify_end_to_end():
    """Run complete end-to-end verification."""
    logger.info("\n" + "=" * 70)
    logger.info("CHECKPOINT 5: End-to-End Pipeline Verification")
    logger.info("=" * 70)

    try:
        # Initialize components
        loader = DataLoader()
        preprocessor = Preprocessor()

        # Build paths
        training_path = Path(config.TRAINING_DATA_PATH) / \
            config.TRAINING_EXCEL_FILE
        linking_path = Path(config.TRAINING_DATA_PATH) / \
            config.LINKING_CSV_FILE
        referencing_path = Path(config.WARRANTY_DOCS_PATH) / \
            config.GENERAL_REFERENCING_FILE

        # Load data
        logger.info("Step 1: Loading data...")
        data = loader.load_all(
            str(training_path),
            str(linking_path),
            str(referencing_path)
        )
        logger.info("✓ Data loaded")

        # Preprocess data
        logger.info("Step 2: Preprocessing data...")
        text_column = 'description' if 'description' in data['merged'].columns else 'Description'
        target_columns = ['Type de litige', 'Responsabilité',
                          'Solution', 'Précision produit']

        processed_data = preprocessor.preprocess_for_training(
            data['merged'],
            text_column,
            target_columns
        )
        logger.info("✓ Data preprocessed")

        # Verify output
        logger.info("Step 3: Verifying output...")
        feature_column = f"{text_column}_features"

        assert feature_column in processed_data.columns, "Feature column missing"
        assert len(processed_data) > 0, "No records in processed data"
        assert (processed_data[feature_column] !=
                '').sum() > 0, "No non-empty features"

        logger.info("✓ Output verified")
        logger.info("\n✓ END-TO-END PIPELINE VERIFICATION PASSED")

        return True

    except Exception as e:
        logger.error(
            f"\n❌ END-TO-END PIPELINE VERIFICATION FAILED: {e}", exc_info=True)
        return False


def main():
    """Run all verification checkpoints."""
    logger.info("\n" + "=" * 70)
    logger.info("SAV COPILOT - DATA PIPELINE VERIFICATION")
    logger.info("Task 4: Checkpoint - Verify data pipeline")
    logger.info("=" * 70 + "\n")

    # Track results
    results = {
        "data_loading": False,
        "preprocessing": False,
        "sample_records": False,
        "text_normalization": False,
        "end_to_end": False
    }

    # Run checkpoints
    data = verify_data_loading()
    results["data_loading"] = data is not None

    processed_data = verify_preprocessing(data)
    results["preprocessing"] = processed_data is not None

    results["sample_records"] = verify_sample_records(processed_data)
    results["text_normalization"] = verify_text_normalization()
    results["end_to_end"] = verify_end_to_end()

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("VERIFICATION SUMMARY")
    logger.info("=" * 70)

    for checkpoint, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        logger.info(f"{checkpoint.replace('_', ' ').title()}: {status}")

    all_passed = all(results.values())

    logger.info("\n" + "=" * 70)
    if all_passed:
        logger.info("✓ ALL CHECKPOINTS PASSED - DATA PIPELINE VERIFIED")
        logger.info("=" * 70)
        return 0
    else:
        logger.error("❌ SOME CHECKPOINTS FAILED - REVIEW ERRORS ABOVE")
        logger.info("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
