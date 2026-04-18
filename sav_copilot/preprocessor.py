"""
Preprocessing module for SAV Copilot.

This module handles text normalization, missing value handling, and feature extraction
for machine learning models. It preserves original data for traceability while preparing
clean features for TF-IDF vectorization.
"""

import logging
import re
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class Preprocessor:
    """Handles text preprocessing and feature extraction for ML models."""

    def __init__(self):
        """Initialize the Preprocessor."""
        pass

    def normalize_text(self, text: str) -> str:
        """
        Normalize text by removing extra whitespace and standardizing encoding.

        This function:
        - Ensures UTF-8 encoding for French text
        - Removes leading/trailing whitespace
        - Collapses multiple spaces into single spaces
        - Normalizes line breaks

        Args:
            text: Raw text string to normalize

        Returns:
            Normalized text string

        Examples:
            >>> preprocessor = Preprocessor()
            >>> preprocessor.normalize_text("  Hello   world  \\n\\n  ")
            'Hello world'
        """
        if not isinstance(text, str):
            return ""

        # Ensure UTF-8 encoding (handle French characters)
        try:
            # If text is already a string, encode and decode to ensure UTF-8
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
        except (AttributeError, UnicodeDecodeError):
            logger.warning(
                f"Failed to normalize encoding for text: {text[:50]}...")
            text = str(text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Normalize line breaks to single spaces
        text = re.sub(r'\s*\n\s*', ' ', text)

        # Collapse multiple spaces into single space
        text = re.sub(r'\s+', ' ', text)

        return text

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in non-critical fields.

        This function fills missing values appropriately:
        - Text columns: filled with empty string ""
        - Numeric columns: left as NaN (handled by models)
        - Critical columns: logged but not filled (should be handled upstream)

        Original data is preserved in columns with '_original' suffix.

        Args:
            df: DataFrame with potential missing values

        Returns:
            DataFrame with missing values handled appropriately
        """
        # Define non-critical text columns that can be filled
        text_columns = [
            'description', 'Description', 'desc',
            'souhait', 'Souhait',
            'typeProduit', 'Type produit', 'Précision produit',
            'reperesConcernes', 'Repères concernés'
        ]

        # Find which text columns actually exist in the dataframe
        existing_text_cols = [col for col in text_columns if col in df.columns]

        # Preserve original data before filling
        for col in existing_text_cols:
            if col not in df.columns:
                continue

            # Create backup column if it doesn't exist
            original_col = f"{col}_original"
            if original_col not in df.columns:
                df[original_col] = df[col].copy()

            # Count missing values
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                logger.info(
                    f"Filling {missing_count} missing values in column '{col}' with empty string")

            # Fill missing values with empty string
            df[col] = df[col].fillna('')

        # Log critical columns with missing values (don't fill these)
        critical_columns = ['identifiant', 'reference', 'id']
        for col in critical_columns:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    logger.warning(
                        f"Critical column '{col}' has {missing_count} missing values. "
                        f"These should be handled upstream."
                    )

        return df

    def extract_features(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """
        Extract and prepare text features for TF-IDF vectorization.

        This function:
        - Normalizes text in the specified column
        - Creates a clean feature column for ML models
        - Preserves original text for traceability
        - Handles missing values

        Args:
            df: DataFrame containing text data
            text_column: Name of the column to extract features from

        Returns:
            DataFrame with additional feature column '{text_column}_features'

        Raises:
            ValueError: If text_column doesn't exist in DataFrame
        """
        if text_column not in df.columns:
            error_msg = f"Text column '{text_column}' not found in DataFrame. Available columns: {list(df.columns)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Create feature column name
        feature_column = f"{text_column}_features"

        # Preserve original if not already preserved
        original_column = f"{text_column}_original"
        if original_column not in df.columns:
            df[original_column] = df[text_column].copy()

        # Extract and normalize text features
        logger.info(f"Extracting features from column '{text_column}'")

        # Handle missing values first
        df[text_column] = df[text_column].fillna('')

        # Normalize each text entry
        df[feature_column] = df[text_column].apply(self.normalize_text)

        # Log statistics
        empty_count = (df[feature_column] == '').sum()
        total_count = len(df)
        logger.info(
            f"Feature extraction complete: {total_count - empty_count}/{total_count} "
            f"non-empty features in '{feature_column}'"
        )

        return df

    def flexible_column_match(
        self,
        df: pd.DataFrame,
        expected_cols: List[str]
    ) -> pd.DataFrame:
        """
        Attempt to match actual columns to expected schema using common patterns.

        This function handles schema variations by matching column names using:
        - Case-insensitive matching
        - Common abbreviations and variations
        - Whitespace and punctuation normalization

        Args:
            df: DataFrame with actual columns
            expected_cols: List of expected column names

        Returns:
            DataFrame with renamed columns where matches found
        """
        column_mapping = {}

        # Common variations for each expected column
        variations = {
            'identifiant': ['id', 'reference', 'ref', 'identifiant', 'identifier', 'numero'],
            'description': ['desc', 'description', 'texte', 'text', 'commentaire', 'Description'],
            'Type de litige': ['type_litige', 'litige', 'type', 'dispute_type', 'Type de litige'],
            'Responsabilité': ['responsabilite', 'responsibility', 'resp', 'responsable', 'Responsabilité'],
            'Solution': ['solution', 'resolution', 'action', 'Solution'],
            'Précision produit': ['precision_produit', 'produit', 'product', 'detail_produit',
                                  'Précision produit', 'Détail produit', 'typeProduit'],
            'souhait': ['souhait', 'wish', 'desire', 'demande', 'Souhait'],
            'reperesConcernes': ['reperes', 'reperesConcernes', 'Repères concernés', 'reperes_concernes']
        }

        for expected_col in expected_cols:
            if expected_col not in df.columns:
                # Try to find a match
                possible_variations = variations.get(
                    expected_col, [expected_col.lower()])

                # Also add the expected column itself to variations
                if expected_col not in possible_variations:
                    possible_variations = possible_variations + [expected_col]

                for actual_col in df.columns:
                    # Skip if already mapped
                    if actual_col in column_mapping:
                        continue

                    # Normalize actual column name for comparison
                    actual_lower = actual_col.lower().strip()
                    actual_normalized = re.sub(r'[_\s-]+', '', actual_lower)

                    # Check direct match
                    if actual_lower in [v.lower() for v in possible_variations]:
                        column_mapping[actual_col] = expected_col
                        logger.info(
                            f"Matched column '{actual_col}' to '{expected_col}'")
                        break

                    # Check normalized match (without spaces/underscores)
                    for variation in possible_variations:
                        variation_normalized = re.sub(
                            r'[_\s-]+', '', variation.lower())
                        if actual_normalized == variation_normalized:
                            column_mapping[actual_col] = expected_col
                            logger.info(
                                f"Matched column '{actual_col}' to '{expected_col}' "
                                f"(normalized match)"
                            )
                            break

                    if actual_col in column_mapping:
                        break

        # Apply column mapping
        if column_mapping:
            df = df.rename(columns=column_mapping)
            logger.info(f"Applied {len(column_mapping)} column mappings")
        else:
            logger.info("No column mappings needed")

        return df

    def preprocess_for_training(
        self,
        df: pd.DataFrame,
        text_column: str,
        target_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Complete preprocessing pipeline for training data.

        This is a convenience method that applies all preprocessing steps:
        1. Handle missing values
        2. Extract features from text column
        3. Normalize target columns if provided

        Args:
            df: Raw training DataFrame
            text_column: Name of the text column to use for features
            target_columns: Optional list of target columns to validate

        Returns:
            Preprocessed DataFrame ready for model training
        """
        logger.info("Starting preprocessing pipeline for training data")

        # Step 1: Handle missing values
        df = self.handle_missing_values(df)

        # Step 2: Extract features
        df = self.extract_features(df, text_column)

        # Step 3: Validate target columns if provided
        if target_columns:
            missing_targets = [
                col for col in target_columns if col not in df.columns]
            if missing_targets:
                logger.warning(
                    f"Target columns missing from DataFrame: {missing_targets}. "
                    f"Attempting flexible column matching..."
                )
                df = self.flexible_column_match(df, target_columns)

                # Check again after matching
                still_missing = [
                    col for col in target_columns if col not in df.columns]
                if still_missing:
                    logger.error(
                        f"Target columns still missing after flexible matching: {still_missing}"
                    )

        logger.info("Preprocessing pipeline complete")
        return df

    def preprocess_for_prediction(self, text: str) -> str:
        """
        Preprocess a single text input for prediction.

        This is a convenience method for preprocessing new complaint text
        before passing it to the model.

        Args:
            text: Raw complaint text

        Returns:
            Normalized text ready for prediction
        """
        return self.normalize_text(text)
