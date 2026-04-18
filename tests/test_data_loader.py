"""
Unit tests for DataLoader module.
"""

import os
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from sav_copilot.data_loader import DataLoader


class TestDataLoader(unittest.TestCase):
    """Test cases for DataLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = DataLoader()
        self.data_dir = Path("Data")

    def test_load_training_data_success(self):
        """Test loading training data from actual file."""
        training_path = (
            self.data_dir / "Data_WithSolution_Week13" /
            "Data_WithSolution_Week13" / "Reclamations_Digit_20260323-20260327.xlsx"
        )

        if not training_path.exists():
            self.skipTest(f"Training data file not found: {training_path}")

        df = self.loader.load_training_data(str(training_path))

        # Verify DataFrame is not empty
        self.assertGreater(len(df), 0)

        # Verify expected columns exist
        expected_cols = ['identifiant', 'Type de litige',
                         'Responsabilité', 'Solution']
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Missing column: {col}")

    def test_load_training_data_file_not_found(self):
        """Test loading training data with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.loader.load_training_data("nonexistent_file.xlsx")

    def test_load_linking_table_success(self):
        """Test loading linking table from actual file."""
        linking_path = (
            self.data_dir / "Data_WithSolution_Week13" /
            "Data_WithSolution_Week13" / "Lien_Reclamation_PJ_20260323-20260327.CSV"
        )

        if not linking_path.exists():
            self.skipTest(f"Linking table file not found: {linking_path}")

        df = self.loader.load_linking_table(str(linking_path))

        # Verify DataFrame is not empty
        self.assertGreater(len(df), 0)

        # Verify expected columns exist
        self.assertIn('Reference', df.columns)
        self.assertIn('Fichier', df.columns)

    def test_load_linking_table_file_not_found(self):
        """Test loading linking table with non-existent file returns empty DataFrame."""
        df = self.loader.load_linking_table("nonexistent_file.csv")

        # Should return empty DataFrame, not raise exception
        self.assertEqual(len(df), 0)
        self.assertIn('Reference', df.columns)
        self.assertIn('Fichier', df.columns)

    def test_load_general_referencing_success(self):
        """Test loading general referencing from actual file."""
        referencing_path = (
            self.data_dir / "Warranty_Documentation" /
            "Warranty_Documentation" / "GeneralReferencing.xlsx"
        )

        if not referencing_path.exists():
            self.skipTest(
                f"General referencing file not found: {referencing_path}")

        df = self.loader.load_general_referencing(str(referencing_path))

        # Verify DataFrame is not empty
        self.assertGreater(len(df), 0)

        # Verify some expected columns exist
        expected_cols = ['Responsabilité', 'Solution', 'Type de litige']
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Missing column: {col}")

    def test_load_general_referencing_file_not_found(self):
        """Test loading general referencing with non-existent file returns empty DataFrame."""
        df = self.loader.load_general_referencing("nonexistent_file.xlsx")

        # Should return empty DataFrame, not raise exception
        self.assertEqual(len(df), 0)

    def test_merge_attachments_with_data(self):
        """Test merging attachments with reclamations."""
        # Create sample reclamations
        reclamations = pd.DataFrame({
            'identifiant': ['R001', 'R002', 'R003'],
            'description': ['Issue 1', 'Issue 2', 'Issue 3']
        })

        # Create sample linking table
        linking = pd.DataFrame({
            'Reference': ['R001', 'R001', 'R002'],
            'Fichier': ['file1.jpg', 'file2.jpg', 'file3.jpg']
        })

        merged = self.loader.merge_attachments(reclamations, linking)

        # Verify attachments column exists
        self.assertIn('attachments', merged.columns)
        self.assertIn('attachment_count', merged.columns)

        # Verify R001 has 2 attachments
        r001_row = merged[merged['identifiant'] == 'R001'].iloc[0]
        self.assertEqual(len(r001_row['attachments']), 2)
        self.assertEqual(r001_row['attachment_count'], 2)

        # Verify R002 has 1 attachment
        r002_row = merged[merged['identifiant'] == 'R002'].iloc[0]
        self.assertEqual(len(r002_row['attachments']), 1)
        self.assertEqual(r002_row['attachment_count'], 1)

        # Verify R003 has 0 attachments
        r003_row = merged[merged['identifiant'] == 'R003'].iloc[0]
        self.assertEqual(len(r003_row['attachments']), 0)
        self.assertEqual(r003_row['attachment_count'], 0)

    def test_merge_attachments_empty_linking(self):
        """Test merging with empty linking table."""
        reclamations = pd.DataFrame({
            'identifiant': ['R001', 'R002'],
            'description': ['Issue 1', 'Issue 2']
        })

        linking = pd.DataFrame(columns=['Reference', 'Fichier'])

        merged = self.loader.merge_attachments(reclamations, linking)

        # Verify all reclamations have empty attachment lists
        self.assertIn('attachments', merged.columns)
        self.assertIn('attachment_count', merged.columns)
        self.assertTrue(all(merged['attachment_count'] == 0))

    def test_load_all_integration(self):
        """Test loading all data sources together."""
        training_path = (
            self.data_dir / "Data_WithSolution_Week13" /
            "Data_WithSolution_Week13" / "Reclamations_Digit_20260323-20260327.xlsx"
        )
        linking_path = (
            self.data_dir / "Data_WithSolution_Week13" /
            "Data_WithSolution_Week13" / "Lien_Reclamation_PJ_20260323-20260327.CSV"
        )
        referencing_path = (
            self.data_dir / "Warranty_Documentation" /
            "Warranty_Documentation" / "GeneralReferencing.xlsx"
        )

        if not training_path.exists():
            self.skipTest(f"Training data file not found: {training_path}")

        result = self.loader.load_all(
            str(training_path),
            str(linking_path),
            str(referencing_path)
        )

        # Verify all expected keys exist
        self.assertIn('training', result)
        self.assertIn('linking', result)
        self.assertIn('referencing', result)
        self.assertIn('merged', result)

        # Verify merged data has attachments
        self.assertIn('attachments', result['merged'].columns)
        self.assertIn('attachment_count', result['merged'].columns)

        # Verify some reclamations have attachments
        total_attachments = result['merged']['attachment_count'].sum()
        self.assertGreater(total_attachments, 0)


if __name__ == '__main__':
    unittest.main()
