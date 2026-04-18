"""
Model training module for SAV Copilot.

This module trains separate TF-IDF + LogisticRegression classifiers for each
prediction target (litige, responsibility, product, solution). Models are persisted
using joblib for reuse.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

import config

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Trains and manages TF-IDF + LogisticRegression classifiers for SAV predictions."""

    def __init__(self, models_dir: str = "models"):
        """
        Initialize the ModelTrainer.

        Args:
            models_dir: Directory path where models will be saved/loaded
        """
        self.models_dir = models_dir
        self.vectorizers: Dict[str, TfidfVectorizer] = {}
        self.classifiers: Dict[str, LogisticRegression] = {}
        self.metadata: Dict[str, Dict] = {}

        # Create models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
        logger.info(
            f"ModelTrainer initialized with models directory: {self.models_dir}")

    def train_classifier(
        self,
        X: pd.Series,
        y: pd.Series,
        target_name: str
    ) -> Tuple[TfidfVectorizer, LogisticRegression]:
        """
        Train TF-IDF + LogisticRegression for one target.

        This method:
        1. Creates and fits a TfidfVectorizer on the text data
        2. Transforms text to TF-IDF features
        3. Trains a LogisticRegression classifier
        4. Stores metadata about the training

        Args:
            X: Text data (Series of strings)
            y: Target labels (Series)
            target_name: Name of the target being trained (e.g., 'litige', 'responsibility')

        Returns:
            Tuple of (fitted_vectorizer, fitted_classifier)

        Raises:
            ValueError: If insufficient data for training
        """
        logger.info(f"Training classifier for target: {target_name}")

        # Validate input data
        if len(X) == 0 or len(y) == 0:
            raise ValueError(
                f"Cannot train {target_name}: empty training data")

        if len(X) != len(y):
            raise ValueError(
                f"Cannot train {target_name}: X and y have different lengths "
                f"({len(X)} vs {len(y)})"
            )

        # Remove missing values
        valid_mask = X.notna() & y.notna()
        X_clean = X[valid_mask]
        y_clean = y[valid_mask]

        if len(X_clean) == 0:
            raise ValueError(
                f"Cannot train {target_name}: no valid training samples after removing NaN")

        # Check for minimum samples
        unique_classes = y_clean.nunique()
        if unique_classes < 2:
            logger.warning(
                f"Target {target_name} has only {unique_classes} unique class(es). "
                f"Training may not be meaningful."
            )

        # Log class distribution
        class_counts = y_clean.value_counts()
        logger.info(f"Class distribution for {target_name}:")
        for label, count in class_counts.items():
            logger.info(f"  {label}: {count} samples")

        # Check for insufficient data per class
        min_samples_per_class = class_counts.min()
        if min_samples_per_class < 2:
            logger.warning(
                f"Target {target_name} has classes with fewer than 2 samples. "
                f"Model performance may be poor."
            )

        # Create and fit TF-IDF vectorizer
        logger.info(f"Creating TF-IDF vectorizer for {target_name}")
        vectorizer = TfidfVectorizer(
            max_features=config.TFIDF_MAX_FEATURES,
            ngram_range=config.TFIDF_NGRAM_RANGE,
            min_df=config.TFIDF_MIN_DF,
            sublinear_tf=config.TFIDF_SUBLINEAR_TF
        )

        try:
            X_tfidf = vectorizer.fit_transform(X_clean)
            logger.info(
                f"TF-IDF vectorization complete: {X_tfidf.shape[0]} samples, "
                f"{X_tfidf.shape[1]} features"
            )
        except Exception as e:
            logger.error(
                f"Failed to fit TF-IDF vectorizer for {target_name}: {e}")
            raise

        # Create and fit LogisticRegression classifier
        logger.info(
            f"Training LogisticRegression classifier for {target_name}")
        classifier = LogisticRegression(
            max_iter=config.LOGREG_MAX_ITER,
            multi_class=config.LOGREG_MULTI_CLASS,
            solver=config.LOGREG_SOLVER,
            random_state=config.LOGREG_RANDOM_STATE
        )

        try:
            classifier.fit(X_tfidf, y_clean)
            logger.info(f"Classifier training complete for {target_name}")
        except Exception as e:
            logger.error(f"Failed to train classifier for {target_name}: {e}")
            raise

        # Store metadata
        self.metadata[target_name] = {
            "training_date": datetime.now().isoformat(),
            "n_samples": len(X_clean),
            "n_features": X_tfidf.shape[1],
            "n_classes": unique_classes,
            "class_counts": class_counts.to_dict(),
            "min_samples_per_class": min_samples_per_class
        }

        logger.info(f"Successfully trained classifier for {target_name}")
        return vectorizer, classifier

    def train_all(
        self,
        df: pd.DataFrame,
        text_column: str,
        target_columns: List[str]
    ) -> None:
        """
        Train classifiers for all targets (litige, responsibility, product, solution).

        This method trains separate models for each target and stores them
        in the vectorizers and classifiers dictionaries.

        Args:
            df: Training DataFrame with text and target columns
            text_column: Name of the column containing text features
            target_columns: List of target column names to train models for

        Raises:
            ValueError: If text_column or any target_column is missing from df
        """
        logger.info("Starting training for all targets")
        logger.info(f"Text column: {text_column}")
        logger.info(f"Target columns: {target_columns}")

        # Validate text column exists
        if text_column not in df.columns:
            raise ValueError(
                f"Text column '{text_column}' not found in DataFrame. "
                f"Available columns: {list(df.columns)}"
            )

        # Get text data
        X = df[text_column]
        logger.info(f"Training data: {len(X)} samples")

        # Train a classifier for each target
        successful_targets = []
        failed_targets = []

        for target_col in target_columns:
            try:
                # Validate target column exists
                if target_col not in df.columns:
                    logger.error(
                        f"Target column '{target_col}' not found in DataFrame. "
                        f"Available columns: {list(df.columns)}"
                    )
                    failed_targets.append(target_col)
                    continue

                # Get target data
                y = df[target_col]

                # Determine target name (short name for storage)
                # Map from full column name to short name
                target_name = None
                for short_name, full_name in config.TARGET_COLUMNS.items():
                    if target_col == full_name or target_col == short_name:
                        target_name = short_name
                        break

                if target_name is None:
                    # Use the column name as-is if not in config
                    target_name = target_col
                    logger.warning(
                        f"Target column '{target_col}' not found in config.TARGET_COLUMNS. "
                        f"Using column name as target name."
                    )

                # Train the classifier
                vectorizer, classifier = self.train_classifier(
                    X, y, target_name)

                # Store the trained models
                self.vectorizers[target_name] = vectorizer
                self.classifiers[target_name] = classifier

                successful_targets.append(target_name)
                logger.info(
                    f"Successfully trained and stored models for {target_name}")

            except Exception as e:
                logger.error(
                    f"Failed to train classifier for {target_col}: {e}")
                failed_targets.append(target_col)
                continue

        # Summary
        logger.info(
            f"Training complete: {len(successful_targets)} successful, {len(failed_targets)} failed")
        if successful_targets:
            logger.info(f"Successfully trained targets: {successful_targets}")
        if failed_targets:
            logger.warning(f"Failed targets: {failed_targets}")

        if len(successful_targets) == 0:
            raise ValueError("No classifiers were successfully trained")

    def save_models(self) -> None:
        """
        Persist all models to disk using joblib.

        This method saves:
        - Each vectorizer as {target}_vectorizer.joblib
        - Each classifier as {target}_classifier.joblib
        - Metadata as {target}_metadata.joblib

        Raises:
            IOError: If models cannot be saved
        """
        if not self.vectorizers or not self.classifiers:
            logger.warning("No models to save")
            return

        logger.info(f"Saving models to {self.models_dir}")

        saved_count = 0
        for target_name in self.vectorizers.keys():
            try:
                # Save vectorizer
                vectorizer_path = os.path.join(
                    self.models_dir,
                    f"{target_name}_vectorizer.joblib"
                )
                joblib.dump(self.vectorizers[target_name], vectorizer_path)
                logger.info(f"Saved vectorizer: {vectorizer_path}")

                # Save classifier
                classifier_path = os.path.join(
                    self.models_dir,
                    f"{target_name}_classifier.joblib"
                )
                joblib.dump(self.classifiers[target_name], classifier_path)
                logger.info(f"Saved classifier: {classifier_path}")

                # Save metadata
                if target_name in self.metadata:
                    metadata_path = os.path.join(
                        self.models_dir,
                        f"{target_name}_metadata.joblib"
                    )
                    joblib.dump(self.metadata[target_name], metadata_path)
                    logger.info(f"Saved metadata: {metadata_path}")

                saved_count += 1

            except Exception as e:
                logger.error(f"Failed to save models for {target_name}: {e}")
                continue

        logger.info(f"Successfully saved models for {saved_count} targets")

    def load_models(self) -> bool:
        """
        Load existing models from disk.

        This method attempts to load all saved models from the models directory.
        If any model fails to load, it logs a warning but continues.

        Returns:
            True if at least one complete model set was loaded successfully,
            False otherwise

        Note:
            A complete model set consists of both vectorizer and classifier.
            Metadata is optional.
        """
        logger.info(f"Loading models from {self.models_dir}")

        if not os.path.exists(self.models_dir):
            logger.warning(
                f"Models directory does not exist: {self.models_dir}")
            return False

        # Find all vectorizer files
        vectorizer_files = [
            f for f in os.listdir(self.models_dir)
            if f.endswith("_vectorizer.joblib")
        ]

        if not vectorizer_files:
            logger.warning(f"No vectorizer files found in {self.models_dir}")
            return False

        loaded_count = 0
        for vectorizer_file in vectorizer_files:
            # Extract target name
            target_name = vectorizer_file.replace("_vectorizer.joblib", "")

            try:
                # Load vectorizer
                vectorizer_path = os.path.join(
                    self.models_dir, vectorizer_file)
                vectorizer = joblib.load(vectorizer_path)
                logger.info(f"Loaded vectorizer for {target_name}")

                # Load classifier
                classifier_file = f"{target_name}_classifier.joblib"
                classifier_path = os.path.join(
                    self.models_dir, classifier_file)

                if not os.path.exists(classifier_path):
                    logger.warning(
                        f"Classifier file not found for {target_name}: {classifier_path}"
                    )
                    continue

                classifier = joblib.load(classifier_path)
                logger.info(f"Loaded classifier for {target_name}")

                # Load metadata (optional)
                metadata_file = f"{target_name}_metadata.joblib"
                metadata_path = os.path.join(self.models_dir, metadata_file)

                if os.path.exists(metadata_path):
                    metadata = joblib.load(metadata_path)
                    self.metadata[target_name] = metadata
                    logger.info(f"Loaded metadata for {target_name}")
                else:
                    logger.info(
                        f"No metadata file found for {target_name} (optional)")

                # Store loaded models
                self.vectorizers[target_name] = vectorizer
                self.classifiers[target_name] = classifier
                loaded_count += 1

                logger.info(
                    f"Successfully loaded complete model set for {target_name}")

            except Exception as e:
                logger.error(f"Failed to load models for {target_name}: {e}")
                continue

        if loaded_count > 0:
            logger.info(f"Successfully loaded {loaded_count} model sets")
            return True
        else:
            logger.warning("No models were successfully loaded")
            return False
