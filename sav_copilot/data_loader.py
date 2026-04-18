"""
Data loading module for SAV Copilot.

This module handles loading and integrating all data sources:
- Training data (Excel with reclamations and solutions)
- Linking table (CSV mapping reclamations to attachments)
- General referencing (Excel with metadata and categories)
"""

import logging
import os
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading and integration of all data sources."""

    def __init__(self):
        """Initialize the DataLoader."""
        self.training_data: Optional[pd.DataFrame] = None
        self.linking_table: Optional[pd.DataFrame] = None
        self.general_referencing: Optional[pd.DataFrame] = None

    def load_training_data(self, path: str) -> pd.DataFrame:
        """
        Load reclamations with solutions from Excel file.

        Args:
            path: Path to the Excel file containing training data

        Returns:
            DataFrame with reclamations and their solutions

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        if not os.path.exists(path):
            error_msg = f"Training data file not found: {path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            # Read Excel with header in row 1 (0-indexed)
            df = pd.read_excel(path, header=1)
            logger.info(
                f"Loaded training data: {df.shape[0]} rows, {df.shape[1]} columns")

            # Validate expected columns exist
            expected_cols = ['identifiant', 'description', 'Type de litige',
                             'Responsabilité', 'Solution', 'Précision produit']
            missing_cols = [
                col for col in expected_cols if col not in df.columns]

            if missing_cols:
                logger.warning(f"Missing expected columns: {missing_cols}")
                # Try flexible column matching
                df = self._flexible_column_match(df, expected_cols)

            # Clean up unnamed columns
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

            # Handle missing values in non-critical fields
            text_columns = ['description', 'souhait',
                            'typeProduit', 'reperesConcernes']
            for col in text_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('')

            # Store for later use
            self.training_data = df

            logger.info(f"Successfully loaded {len(df)} training records")
            return df

        except Exception as e:
            error_msg = f"Error loading training data from {path}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def load_linking_table(self, path: str) -> pd.DataFrame:
        """
        Load CSV linking reclamations to attachments.

        Args:
            path: Path to the CSV file containing reclamation-attachment mappings

        Returns:
            DataFrame with Reference and Fichier columns

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not os.path.exists(path):
            error_msg = f"Linking table file not found: {path}"
            logger.warning(error_msg)
            # Return empty DataFrame with expected structure (non-critical)
            return pd.DataFrame(columns=['Reference', 'Fichier'])

        try:
            # CSV uses semicolon as delimiter
            df = pd.read_csv(path, sep=';')
            logger.info(f"Loaded linking table: {df.shape[0]} rows")

            # Validate expected columns
            if 'Reference' not in df.columns or 'Fichier' not in df.columns:
                # Try alternative column names
                if len(df.columns) == 1 and ';' in df.columns[0]:
                    # Delimiter not properly detected
                    df = pd.read_csv(path, sep=';', header=0)
                    # Split the combined column if needed
                    if len(df.columns) == 1:
                        col_name = df.columns[0]
                        df[['Reference', 'Fichier']] = df[col_name].str.split(
                            ';', expand=True)
                        df = df.drop(columns=[col_name])

            # Store for later use
            self.linking_table = df

            logger.info(f"Successfully loaded {len(df)} attachment links")
            return df

        except Exception as e:
            error_msg = f"Error loading linking table from {path}: {str(e)}"
            logger.warning(error_msg)
            # Return empty DataFrame (non-critical)
            return pd.DataFrame(columns=['Reference', 'Fichier'])

    def load_general_referencing(self, path: str) -> pd.DataFrame:
        """
        Load metadata Excel with category definitions.

        Args:
            path: Path to the Excel file containing general referencing data

        Returns:
            DataFrame with category definitions and metadata

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not os.path.exists(path):
            error_msg = f"General referencing file not found: {path}"
            logger.warning(error_msg)
            # Return empty DataFrame (non-critical)
            return pd.DataFrame()

        try:
            df = pd.read_excel(path)
            logger.info(
                f"Loaded general referencing: {df.shape[0]} rows, {df.shape[1]} columns")

            # Clean up unnamed columns
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

            # Remove rows with all NaN values
            df = df.dropna(how='all')

            # Store for later use
            self.general_referencing = df

            logger.info(f"Successfully loaded {len(df)} reference entries")
            return df

        except Exception as e:
            error_msg = f"Error loading general referencing from {path}: {str(e)}"
            logger.warning(error_msg)
            # Return empty DataFrame (non-critical)
            return pd.DataFrame()

    def merge_attachments(
        self,
        reclamations: pd.DataFrame,
        linking: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge attachment references with reclamations.

        Args:
            reclamations: DataFrame with reclamation records
            linking: DataFrame with reclamation-attachment mappings

        Returns:
            DataFrame with reclamations and their attachment lists
        """
        if linking.empty:
            logger.warning("Linking table is empty, no attachments to merge")
            reclamations['attachments'] = [[]
                                           for _ in range(len(reclamations))]
            reclamations['attachment_count'] = 0
            return reclamations

        try:
            # Group attachments by reference
            attachment_groups = linking.groupby(
                'Reference')['Fichier'].apply(list).reset_index()
            attachment_groups.columns = ['identifiant', 'attachments']

            # Merge with reclamations
            merged = reclamations.merge(
                attachment_groups,
                on='identifiant',
                how='left'
            )

            # Fill missing attachments with empty lists
            merged['attachments'] = merged['attachments'].apply(
                lambda x: x if isinstance(x, list) else []
            )

            # Add attachment count
            merged['attachment_count'] = merged['attachments'].apply(len)

            logger.info(
                f"Merged attachments: {merged['attachment_count'].sum()} total attachments "
                f"for {len(merged)} reclamations"
            )

            return merged

        except Exception as e:
            error_msg = f"Error merging attachments: {str(e)}"
            logger.warning(error_msg)
            # Add empty attachment columns
            reclamations['attachments'] = [[]
                                           for _ in range(len(reclamations))]
            reclamations['attachment_count'] = 0
            return reclamations

    def _flexible_column_match(
        self,
        df: pd.DataFrame,
        expected_cols: List[str]
    ) -> pd.DataFrame:
        """
        Attempt to match actual columns to expected schema using common patterns.

        Args:
            df: DataFrame with actual columns
            expected_cols: List of expected column names

        Returns:
            DataFrame with renamed columns where matches found
        """
        column_mapping = {}

        # Common variations for each expected column
        variations = {
            'identifiant': ['id', 'reference', 'ref', 'identifiant', 'identifier'],
            'description': ['desc', 'description', 'texte', 'text', 'commentaire'],
            'Type de litige': ['type_litige', 'litige', 'type', 'dispute_type'],
            'Responsabilité': ['responsabilite', 'responsibility', 'resp', 'responsable'],
            'Solution': ['solution', 'resolution', 'action'],
            'Précision produit': ['precision_produit', 'produit', 'product', 'detail_produit']
        }

        for expected_col in expected_cols:
            if expected_col not in df.columns:
                # Try to find a match
                possible_variations = variations.get(expected_col, [])
                for actual_col in df.columns:
                    actual_lower = actual_col.lower().strip()
                    if actual_lower in [v.lower() for v in possible_variations]:
                        column_mapping[actual_col] = expected_col
                        logger.info(
                            f"Matched column '{actual_col}' to '{expected_col}'")
                        break

        if column_mapping:
            df = df.rename(columns=column_mapping)

        return df

    def load_all(
        self,
        training_path: str,
        linking_path: str,
        referencing_path: str
    ) -> Dict[str, pd.DataFrame]:
        """
        Load all data sources and return them as a dictionary.

        Args:
            training_path: Path to training data Excel file
            linking_path: Path to linking table CSV file
            referencing_path: Path to general referencing Excel file

        Returns:
            Dictionary with keys: 'training', 'linking', 'referencing', 'merged'
        """
        logger.info("Loading all data sources...")

        # Load training data (critical)
        training_data = self.load_training_data(training_path)

        # Load linking table (non-critical)
        linking_table = self.load_linking_table(linking_path)

        # Load general referencing (non-critical)
        general_referencing = self.load_general_referencing(referencing_path)

        # Merge attachments with training data
        merged_data = self.merge_attachments(training_data, linking_table)

        logger.info("All data sources loaded successfully")

        return {
            'training': training_data,
            'linking': linking_table,
            'referencing': general_referencing,
            'merged': merged_data
        }
