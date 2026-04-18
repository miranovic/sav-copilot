"""
Unit tests for the Preprocessor module.
"""

import pandas as pd
import pytest

from sav_copilot.preprocessor import Preprocessor


class TestPreprocessor:
    """Test suite for Preprocessor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = Preprocessor()

    def test_normalize_text_basic(self):
        """Test basic text normalization."""
        text = "  Hello   world  \n\n  "
        result = self.preprocessor.normalize_text(text)
        assert result == "Hello world"

    def test_normalize_text_french_characters(self):
        """Test normalization with French characters."""
        text = "  Problème de qualité  avec  l'étanchéité  "
        result = self.preprocessor.normalize_text(text)
        assert result == "Problème de qualité avec l'étanchéité"
        assert "é" in result  # Verify French characters preserved

    def test_normalize_text_multiple_spaces(self):
        """Test collapsing multiple spaces."""
        text = "Text    with     many      spaces"
        result = self.preprocessor.normalize_text(text)
        assert result == "Text with many spaces"

    def test_normalize_text_line_breaks(self):
        """Test normalizing line breaks."""
        text = "Line 1\nLine 2\n\nLine 3"
        result = self.preprocessor.normalize_text(text)
        assert result == "Line 1 Line 2 Line 3"

    def test_normalize_text_empty_string(self):
        """Test normalizing empty string."""
        result = self.preprocessor.normalize_text("")
        assert result == ""

    def test_normalize_text_non_string(self):
        """Test normalizing non-string input."""
        result = self.preprocessor.normalize_text(None)
        assert result == ""

        result = self.preprocessor.normalize_text(123)
        assert result == ""

    def test_handle_missing_values_text_columns(self):
        """Test handling missing values in text columns."""
        df = pd.DataFrame({
            'description': ['Text 1', None, 'Text 3'],
            'souhait': ['Wish 1', 'Wish 2', None],
            'identifiant': ['ID1', 'ID2', 'ID3']
        })

        result = self.preprocessor.handle_missing_values(df)

        # Text columns should be filled with empty string
        assert result['description'].iloc[1] == ''
        assert result['souhait'].iloc[2] == ''

        # Original data should be preserved
        assert 'description_original' in result.columns
        assert pd.isna(result['description_original'].iloc[1])

    def test_handle_missing_values_preserves_originals(self):
        """Test that original data is preserved."""
        df = pd.DataFrame({
            'description': ['Original text', None, 'Another text']
        })

        result = self.preprocessor.handle_missing_values(df)

        # Original column should exist
        assert 'description_original' in result.columns

        # Original values should be preserved
        assert result['description_original'].iloc[0] == 'Original text'
        assert pd.isna(result['description_original'].iloc[1])
        assert result['description_original'].iloc[2] == 'Another text'

        # Processed column should have filled values
        assert result['description'].iloc[1] == ''

    def test_extract_features_basic(self):
        """Test basic feature extraction."""
        df = pd.DataFrame({
            'description': ['  Text 1  ', '  Text 2  ', '  Text 3  ']
        })

        result = self.preprocessor.extract_features(df, 'description')

        # Feature column should be created
        assert 'description_features' in result.columns

        # Features should be normalized
        assert result['description_features'].iloc[0] == 'Text 1'
        assert result['description_features'].iloc[1] == 'Text 2'

        # Original should be preserved
        assert 'description_original' in result.columns

    def test_extract_features_missing_column(self):
        """Test feature extraction with missing column."""
        df = pd.DataFrame({
            'other_column': ['Text 1', 'Text 2']
        })

        with pytest.raises(ValueError, match="Text column 'description' not found"):
            self.preprocessor.extract_features(df, 'description')

    def test_extract_features_with_missing_values(self):
        """Test feature extraction handles missing values."""
        df = pd.DataFrame({
            'description': ['Text 1', None, 'Text 3']
        })

        result = self.preprocessor.extract_features(df, 'description')

        # Missing values should be filled with empty string
        assert result['description_features'].iloc[1] == ''

    def test_flexible_column_match_exact(self):
        """Test flexible column matching with exact matches."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'desc': ['Text 1', 'Text 2', 'Text 3']
        })

        expected_cols = ['identifiant', 'description']
        result = self.preprocessor.flexible_column_match(df, expected_cols)

        # Columns should be renamed
        assert 'identifiant' in result.columns
        assert 'description' in result.columns
        assert 'id' not in result.columns
        assert 'desc' not in result.columns

    def test_flexible_column_match_case_insensitive(self):
        """Test flexible column matching is case-insensitive."""
        df = pd.DataFrame({
            'Description': ['Text 1', 'Text 2'],
            'SOLUTION': ['Sol 1', 'Sol 2']
        })

        expected_cols = ['description', 'Solution']
        result = self.preprocessor.flexible_column_match(df, expected_cols)

        # Should match despite case differences
        assert 'description' in result.columns
        assert 'Solution' in result.columns

    def test_flexible_column_match_no_matches(self):
        """Test flexible column matching when no matches found."""
        df = pd.DataFrame({
            'unknown_col1': [1, 2],
            'unknown_col2': [3, 4]
        })

        expected_cols = ['identifiant', 'description']
        result = self.preprocessor.flexible_column_match(df, expected_cols)

        # Original columns should remain unchanged
        assert 'unknown_col1' in result.columns
        assert 'unknown_col2' in result.columns
        assert 'identifiant' not in result.columns

    def test_preprocess_for_training_complete_pipeline(self):
        """Test complete preprocessing pipeline for training."""
        df = pd.DataFrame({
            'description': ['  Text 1  ', None, '  Text 3  '],
            'Solution': ['Sol 1', 'Sol 2', 'Sol 3'],
            'Type de litige': ['Type 1', 'Type 2', 'Type 3']
        })

        target_columns = ['Solution', 'Type de litige']
        result = self.preprocessor.preprocess_for_training(
            df, 'description', target_columns
        )

        # Feature column should exist
        assert 'description_features' in result.columns

        # Missing values should be handled
        assert result['description'].iloc[1] == ''

        # Original should be preserved
        assert 'description_original' in result.columns

        # Target columns should exist
        assert 'Solution' in result.columns
        assert 'Type de litige' in result.columns

    def test_preprocess_for_prediction(self):
        """Test preprocessing for single prediction."""
        text = "  Problème   avec   le   produit  \n\n  "
        result = self.preprocessor.preprocess_for_prediction(text)

        assert result == "Problème avec le produit"

    def test_normalize_text_special_characters(self):
        """Test normalization preserves important special characters."""
        text = "Problème d'étanchéité: 50€ de dégâts!"
        result = self.preprocessor.normalize_text(text)

        # Should preserve French characters and punctuation
        assert "é" in result
        assert "€" in result
        assert ":" in result
        assert "!" in result

    def test_handle_missing_values_multiple_calls(self):
        """Test that multiple calls don't create duplicate original columns."""
        df = pd.DataFrame({
            'description': ['Text 1', None, 'Text 3']
        })

        # First call
        result1 = self.preprocessor.handle_missing_values(df)
        assert 'description_original' in result1.columns

        # Second call on same data
        result2 = self.preprocessor.handle_missing_values(result1)

        # Should not create description_original_original
        assert 'description_original_original' not in result2.columns
        assert 'description_original' in result2.columns
