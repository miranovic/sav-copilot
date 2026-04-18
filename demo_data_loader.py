"""
Demo script to showcase DataLoader functionality.
"""

import logging
from pathlib import Path

from sav_copilot.data_loader import DataLoader
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Demonstrate DataLoader functionality."""
    logger.info("=== SAV Copilot Data Loader Demo ===\n")

    # Initialize DataLoader
    loader = DataLoader()

    # Construct file paths using config
    training_path = Path(config.TRAINING_DATA_PATH) / \
        config.TRAINING_EXCEL_FILE
    linking_path = Path(config.TRAINING_DATA_PATH) / config.LINKING_CSV_FILE
    referencing_path = Path(config.WARRANTY_DOCS_PATH) / \
        config.GENERAL_REFERENCING_FILE

    logger.info(f"Training data path: {training_path}")
    logger.info(f"Linking table path: {linking_path}")
    logger.info(f"General referencing path: {referencing_path}\n")

    # Load all data sources
    try:
        data = loader.load_all(
            str(training_path),
            str(linking_path),
            str(referencing_path)
        )

        # Display summary statistics
        logger.info("\n=== Data Loading Summary ===")
        logger.info(f"Training records: {len(data['training'])}")
        logger.info(f"Attachment links: {len(data['linking'])}")
        logger.info(f"Reference entries: {len(data['referencing'])}")
        logger.info(f"Merged records: {len(data['merged'])}")

        # Display attachment statistics
        merged = data['merged']
        total_attachments = merged['attachment_count'].sum()
        records_with_attachments = (merged['attachment_count'] > 0).sum()
        avg_attachments = merged['attachment_count'].mean()

        logger.info(f"\n=== Attachment Statistics ===")
        logger.info(f"Total attachments: {total_attachments}")
        logger.info(f"Records with attachments: {records_with_attachments}")
        logger.info(f"Average attachments per record: {avg_attachments:.2f}")

        # Display sample record
        logger.info(f"\n=== Sample Record ===")
        sample = merged.iloc[1]  # Get second record
        logger.info(f"ID: {sample['identifiant']}")
        logger.info(
            f"Description: {sample.get('description', 'N/A')[:100]}...")
        logger.info(f"Type de litige: {sample.get('Type de litige', 'N/A')}")
        logger.info(f"Responsabilité: {sample.get('Responsabilité', 'N/A')}")
        logger.info(f"Solution: {sample.get('Solution', 'N/A')}")
        logger.info(f"Attachments: {sample['attachment_count']}")
        if sample['attachment_count'] > 0:
            # Show first 3
            logger.info(f"Attachment files: {sample['attachments'][:3]}")

        # Display category statistics from general referencing
        if not data['referencing'].empty:
            logger.info(f"\n=== Category Statistics ===")
            ref = data['referencing']

            if 'Responsabilité' in ref.columns:
                responsibilities = ref['Responsabilité'].dropna().unique()
                logger.info(
                    f"Responsibility categories: {list(responsibilities)}")

            if 'Solution' in ref.columns:
                solutions = ref['Solution'].dropna().unique()
                logger.info(f"Solution categories: {list(solutions)}")

            if 'Type de litige' in ref.columns:
                litiges = ref['Type de litige'].dropna().unique()
                logger.info(f"Litige types: {list(litiges)}")

        logger.info("\n=== Demo Complete ===")

    except Exception as e:
        logger.error(f"Error during data loading: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
