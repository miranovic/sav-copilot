#!/usr/bin/env python3
"""
Training script for SAV Copilot models.

This script orchestrates the complete training pipeline:
1. Load training data using DataLoader
2. Preprocess data using Preprocessor
3. Train all models using ModelTrainer
4. Save trained models to models directory
5. Log training statistics and performance metrics

Usage:
    python train_models.py --data-path Data/Data_WithSolution_Week13
    python train_models.py --data-path /path/to/data --models-dir custom_models
"""

import argparse
import logging
import os
import sys
from datetime import datetime

import pandas as pd

from sav_copilot.data_loader import DataLoader
from sav_copilot.preprocessor import Preprocessor
from sav_copilot.trainer import ModelTrainer
import config


def setup_logging(log_file: str = None):
    """
    Configure logging for the training script.

    Args:
        log_file: Optional path to log file. If None, uses config.LOG_FILE
    """
    log_file = log_file or config.LOG_FILE

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        Namespace with parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Train SAV Copilot classification models',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train with default paths
  python train_models.py --data-path Data/Data_WithSolution_Week13

  # Train with custom models directory
  python train_models.py --data-path Data/Data_WithSolution_Week13 --models-dir my_models

  # Force retraining even if models exist
  python train_models.py --data-path Data/Data_WithSolution_Week13 --force
        """
    )

    parser.add_argument(
        '--data-path',
        type=str,
        required=True,
        help='Path to the training data directory (e.g., Data/Data_WithSolution_Week13)'
    )

    parser.add_argument(
        '--models-dir',
        type=str,
        default=config.MODELS_DIR,
        help=f'Directory to save trained models (default: {config.MODELS_DIR})'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force retraining even if models already exist'
    )

    parser.add_argument(
        '--log-file',
        type=str,
        default=None,
        help=f'Path to log file (default: {config.LOG_FILE})'
    )

    return parser.parse_args()


def load_training_data(data_path: str, logger: logging.Logger) -> pd.DataFrame:
    """
    Load training data from the specified path.

    Args:
        data_path: Path to the training data directory
        logger: Logger instance

    Returns:
        DataFrame with training data

    Raises:
        FileNotFoundError: If training data file not found
        ValueError: If data format is invalid
    """
    logger.info("=" * 80)
    logger.info("STEP 1: Loading Training Data")
    logger.info("=" * 80)

    try:
        loader = DataLoader()

        # Build full path to training Excel file
        training_file_path = os.path.join(
            data_path,
            config.TRAINING_EXCEL_FILE
        )

        logger.info(f"Loading training data from: {training_file_path}")

        if not os.path.exists(training_file_path):
            # Try alternative path structure
            alt_path = os.path.join(
                data_path,
                os.path.basename(data_path),
                config.TRAINING_EXCEL_FILE
            )
            if os.path.exists(alt_path):
                training_file_path = alt_path
                logger.info(f"Using alternative path: {training_file_path}")
            else:
                raise FileNotFoundError(
                    f"Training data file not found at {training_file_path} or {alt_path}"
                )

        df = loader.load_training_data(training_file_path)

        logger.info(f"✓ Successfully loaded {len(df)} training samples")
        logger.info(f"✓ Columns: {list(df.columns)}")

        # Log basic statistics
        logger.info("\nData Statistics:")
        logger.info(f"  Total records: {len(df)}")
        logger.info(f"  Total columns: {len(df.columns)}")

        # Check for target columns
        target_columns = list(config.TARGET_COLUMNS.values())
        missing_targets = [
            col for col in target_columns if col not in df.columns]
        if missing_targets:
            logger.warning(f"  Missing target columns: {missing_targets}")
        else:
            logger.info(f"  ✓ All target columns present")

        return df

    except FileNotFoundError as e:
        logger.error(f"✗ Training data file not found: {e}")
        raise
    except Exception as e:
        logger.error(f"✗ Failed to load training data: {e}")
        raise ValueError(f"Error loading training data: {e}")


def preprocess_data(df: pd.DataFrame, logger: logging.Logger) -> tuple:
    """
    Preprocess training data for model training.

    Args:
        df: Raw training DataFrame
        logger: Logger instance

    Returns:
        Tuple of (preprocessed_df, text_column_name, target_columns)

    Raises:
        ValueError: If preprocessing fails
    """
    logger.info("\n" + "=" * 80)
    logger.info("STEP 2: Preprocessing Data")
    logger.info("=" * 80)

    try:
        preprocessor = Preprocessor()

        # Get target columns from config
        target_columns = list(config.TARGET_COLUMNS.values())
        logger.info(f"Target columns: {target_columns}")

        # Preprocess for training
        logger.info(f"Preprocessing text column: {config.TEXT_COLUMN}")
        df = preprocessor.preprocess_for_training(
            df=df,
            text_column=config.TEXT_COLUMN,
            target_columns=target_columns
        )

        # Use the features column created by preprocessing
        text_column = f"{config.TEXT_COLUMN}_features"
        logger.info(f"✓ Using feature column: {text_column}")

        # Log preprocessing statistics
        logger.info("\nPreprocessing Statistics:")
        logger.info(f"  Text column: {text_column}")
        logger.info(
            f"  Non-empty texts: {(df[text_column] != '').sum()}/{len(df)}")

        # Check target column statistics
        for target_col in target_columns:
            if target_col in df.columns:
                non_null = df[target_col].notna().sum()
                unique = df[target_col].nunique()
                logger.info(
                    f"  {target_col}: {non_null} non-null, {unique} unique values")

        return df, text_column, target_columns

    except Exception as e:
        logger.error(f"✗ Failed to preprocess data: {e}")
        raise ValueError(f"Error preprocessing data: {e}")


def train_models(
    df: pd.DataFrame,
    text_column: str,
    target_columns: list,
    models_dir: str,
    force_retrain: bool,
    logger: logging.Logger
) -> ModelTrainer:
    """
    Train classification models for all targets.

    Args:
        df: Preprocessed training DataFrame
        text_column: Name of the text feature column
        target_columns: List of target column names
        models_dir: Directory to save models
        force_retrain: Whether to force retraining if models exist
        logger: Logger instance

    Returns:
        Trained ModelTrainer instance

    Raises:
        ValueError: If training fails
    """
    logger.info("\n" + "=" * 80)
    logger.info("STEP 3: Training Models")
    logger.info("=" * 80)

    try:
        trainer = ModelTrainer(models_dir=models_dir)

        # Check if models already exist
        models_exist = trainer.load_models()

        if models_exist and not force_retrain:
            logger.info("✓ Existing models found and loaded successfully")
            logger.info(
                f"✓ Loaded models for targets: {list(trainer.vectorizers.keys())}")
            logger.info("\nℹ Use --force flag to retrain existing models")
            return trainer

        if models_exist and force_retrain:
            logger.info(
                "⚠ Existing models found, but --force flag set. Retraining...")

        if not models_exist:
            logger.info("No existing models found. Training new models...")

        # Train all models
        start_time = datetime.now()
        logger.info(
            f"Training started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        trainer.train_all(
            df=df,
            text_column=text_column,
            target_columns=target_columns
        )

        end_time = datetime.now()
        training_duration = (end_time - start_time).total_seconds()

        logger.info(f"✓ Training completed in {training_duration:.2f} seconds")

        # Save models
        logger.info("\nSaving models to disk...")
        trainer.save_models()
        logger.info(f"✓ Models saved to: {models_dir}")

        return trainer

    except Exception as e:
        logger.error(f"✗ Failed to train models: {e}")
        import traceback
        traceback.print_exc()
        raise ValueError(f"Error training models: {e}")


def log_training_statistics(trainer: ModelTrainer, logger: logging.Logger):
    """
    Log detailed training statistics and performance metrics.

    Args:
        trainer: Trained ModelTrainer instance
        logger: Logger instance
    """
    logger.info("\n" + "=" * 80)
    logger.info("STEP 4: Training Statistics and Performance Metrics")
    logger.info("=" * 80)

    if not trainer.vectorizers:
        logger.warning("No trained models found")
        return

    logger.info(f"\nTrained {len(trainer.vectorizers)} models:")

    for target_name in sorted(trainer.vectorizers.keys()):
        logger.info(f"\n{'─' * 80}")
        logger.info(f"Target: {target_name}")
        logger.info(f"{'─' * 80}")

        # Model metadata
        if target_name in trainer.metadata:
            metadata = trainer.metadata[target_name]

            logger.info(
                f"Training Date: {metadata.get('training_date', 'N/A')}")
            logger.info(
                f"Training Samples: {metadata.get('n_samples', 'N/A')}")
            logger.info(
                f"TF-IDF Features: {metadata.get('n_features', 'N/A')}")
            logger.info(
                f"Number of Classes: {metadata.get('n_classes', 'N/A')}")
            logger.info(
                f"Min Samples per Class: {metadata.get('min_samples_per_class', 'N/A')}")

            # Class distribution
            class_counts = metadata.get('class_counts', {})
            if class_counts:
                logger.info(f"\nClass Distribution (top 10):")
                sorted_classes = sorted(
                    class_counts.items(), key=lambda x: x[1], reverse=True)
                for i, (label, count) in enumerate(sorted_classes[:10], 1):
                    percentage = (count / metadata.get('n_samples', 1)) * 100
                    logger.info(
                        f"  {i:2d}. {label:40s} {count:5d} ({percentage:5.1f}%)")

                if len(class_counts) > 10:
                    remaining = len(class_counts) - 10
                    logger.info(f"  ... and {remaining} more classes")
        else:
            logger.warning(f"No metadata available for {target_name}")

        # Model file paths
        vectorizer_path = os.path.join(
            trainer.models_dir, f"{target_name}_vectorizer.joblib")
        classifier_path = os.path.join(
            trainer.models_dir, f"{target_name}_classifier.joblib")
        metadata_path = os.path.join(
            trainer.models_dir, f"{target_name}_metadata.joblib")

        logger.info(f"\nModel Files:")
        logger.info(f"  Vectorizer: {vectorizer_path}")
        logger.info(f"  Classifier: {classifier_path}")
        logger.info(f"  Metadata: {metadata_path}")


def main():
    """
    Main entry point for the training script.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Setup logging
    setup_logging(args.log_file)
    logger = logging.getLogger(__name__)

    # Print header
    logger.info("\n" + "=" * 80)
    logger.info("SAV COPILOT - MODEL TRAINING SCRIPT")
    logger.info("=" * 80)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Data path: {args.data_path}")
    logger.info(f"Models directory: {args.models_dir}")
    logger.info(f"Force retrain: {args.force}")
    logger.info("=" * 80)

    try:
        # Step 1: Load training data
        df = load_training_data(args.data_path, logger)

        # Step 2: Preprocess data
        df, text_column, target_columns = preprocess_data(df, logger)

        # Step 3: Train models
        trainer = train_models(
            df=df,
            text_column=text_column,
            target_columns=target_columns,
            models_dir=args.models_dir,
            force_retrain=args.force,
            logger=logger
        )

        # Step 4: Log statistics
        log_training_statistics(trainer, logger)

        # Success summary
        logger.info("\n" + "=" * 80)
        logger.info("✓ TRAINING COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(
            f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Models saved to: {args.models_dir}")
        logger.info(
            f"Trained targets: {', '.join(sorted(trainer.vectorizers.keys()))}")
        logger.info("=" * 80)

        return 0

    except FileNotFoundError as e:
        logger.error("\n" + "=" * 80)
        logger.error("✗ TRAINING FAILED - FILE NOT FOUND")
        logger.error("=" * 80)
        logger.error(f"Error: {e}")
        logger.error(
            "\nPlease check that the data path is correct and the file exists.")
        logger.error("=" * 80)
        return 1

    except ValueError as e:
        logger.error("\n" + "=" * 80)
        logger.error("✗ TRAINING FAILED - INVALID DATA")
        logger.error("=" * 80)
        logger.error(f"Error: {e}")
        logger.error("=" * 80)
        return 1

    except Exception as e:
        logger.error("\n" + "=" * 80)
        logger.error("✗ TRAINING FAILED - UNEXPECTED ERROR")
        logger.error("=" * 80)
        logger.error(f"Error: {e}")
        logger.error("\nFull traceback:")
        import traceback
        traceback.print_exc()
        logger.error("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
