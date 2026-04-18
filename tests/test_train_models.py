"""
Unit tests for train_models.py script.

Tests the training script's core functionality including:
- Argument parsing
- Data loading
- Preprocessing
- Model training
- Error handling
"""

import config
import train_models
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

import pandas as pd

# Add parent directory to path to import train_models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTrainModelsScript(unittest.TestCase):
    """Test cases for train_models.py script."""

    def test_parse_arguments_with_required_data_path(self):
        """Test that argument parser requires data-path."""
        with patch('sys.argv', ['train_models.py', '--data-path', 'test/path']):
            args = train_models.parse_arguments()
            self.assertEqual(args.data_path, 'test/path')
            self.assertEqual(args.models_dir, config.MODELS_DIR)
            self.assertFalse(args.force)

    def test_parse_arguments_with_all_options(self):
        """Test argument parser with all options."""
        with patch('sys.argv', [
            'train_models.py',
            '--data-path', 'custom/path',
            '--models-dir', 'custom_models',
            '--force',
            '--log-file', 'custom.log'
        ]):
            args = train_models.parse_arguments()
            self.assertEqual(args.data_path, 'custom/path')
            self.assertEqual(args.models_dir, 'custom_models')
            self.assertTrue(args.force)
            self.assertEqual(args.log_file, 'custom.log')

    def test_load_training_data_success(self):
        """Test successful data loading."""
        # Create mock logger
        logger = Mock()

        # Create sample DataFrame
        sample_data = pd.DataFrame({
            'identifiant': ['R001', 'R002'],
            'description': ['Test 1', 'Test 2'],
            'Type de litige': ['Type A', 'Type B'],
            'Responsabilité': ['Resp A', 'Resp B'],
            'Précision produit': ['Prod A', 'Prod B'],
            'Solution': ['Sol A', 'Sol B']
        })

        # Mock DataLoader
        with patch('train_models.DataLoader') as MockDataLoader:
            mock_loader = MockDataLoader.return_value
            mock_loader.load_training_data.return_value = sample_data

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
                tmp_path = tmp.name

            try:
                # Mock os.path.exists to return True
                with patch('os.path.exists', return_value=True):
                    result = train_models.load_training_data(tmp_path, logger)

                # Verify result
                self.assertIsInstance(result, pd.DataFrame)
                self.assertEqual(len(result), 2)

            finally:
                # Clean up
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    def test_load_training_data_file_not_found(self):
        """Test data loading with missing file."""
        logger = Mock()

        with self.assertRaises(FileNotFoundError):
            train_models.load_training_data('nonexistent/path', logger)

    def test_preprocess_data_success(self):
        """Test successful data preprocessing."""
        logger = Mock()

        # Create sample DataFrame
        df = pd.DataFrame({
            'description': ['Test description 1', 'Test description 2'],
            'Type de litige': ['Type A', 'Type B'],
            'Responsabilité': ['Resp A', 'Resp B'],
            'Précision produit': ['Prod A', 'Prod B'],
            'Solution': ['Sol A', 'Sol B']
        })

        # Mock Preprocessor
        with patch('train_models.Preprocessor') as MockPreprocessor:
            mock_preprocessor = MockPreprocessor.return_value

            # Create preprocessed DataFrame
            preprocessed_df = df.copy()
            preprocessed_df['description_features'] = df['description']
            mock_preprocessor.preprocess_for_training.return_value = preprocessed_df

            result_df, text_col, target_cols = train_models.preprocess_data(
                df, logger)

            # Verify results
            self.assertIsInstance(result_df, pd.DataFrame)
            self.assertEqual(text_col, 'description_features')
            self.assertIsInstance(target_cols, list)
            self.assertGreater(len(target_cols), 0)

    def test_train_models_with_existing_models(self):
        """Test training when models already exist."""
        logger = Mock()

        df = pd.DataFrame({
            'description_features': ['Test 1', 'Test 2'],
            'Type de litige': ['Type A', 'Type B']
        })

        # Mock ModelTrainer
        with patch('train_models.ModelTrainer') as MockTrainer:
            mock_trainer = MockTrainer.return_value
            mock_trainer.load_models.return_value = True
            mock_trainer.vectorizers = {'litige': Mock()}

            result = train_models.train_models(
                df=df,
                text_column='description_features',
                target_columns=['Type de litige'],
                models_dir='models',
                force_retrain=False,
                logger=logger
            )

            # Verify that training was skipped
            mock_trainer.train_all.assert_not_called()
            self.assertEqual(result, mock_trainer)

    def test_train_models_force_retrain(self):
        """Test training with force retrain flag."""
        logger = Mock()

        df = pd.DataFrame({
            'description_features': ['Test 1', 'Test 2'],
            'Type de litige': ['Type A', 'Type B']
        })

        # Mock ModelTrainer
        with patch('train_models.ModelTrainer') as MockTrainer:
            mock_trainer = MockTrainer.return_value
            mock_trainer.load_models.return_value = True
            mock_trainer.vectorizers = {'litige': Mock()}

            # Mock datetime properly to return actual datetime objects
            from datetime import datetime
            mock_start = datetime(2026, 4, 18, 12, 0, 0)
            mock_end = datetime(2026, 4, 18, 12, 0, 5)

            with patch('train_models.datetime') as mock_datetime:
                mock_datetime.now.side_effect = [mock_start, mock_end]

                result = train_models.train_models(
                    df=df,
                    text_column='description_features',
                    target_columns=['Type de litige'],
                    models_dir='models',
                    force_retrain=True,
                    logger=logger
                )

                # Verify that training was called
                mock_trainer.train_all.assert_called_once()
                mock_trainer.save_models.assert_called_once()

    def test_log_training_statistics(self):
        """Test logging of training statistics."""
        logger = Mock()

        # Create mock trainer with metadata
        mock_trainer = Mock()
        mock_trainer.vectorizers = {'litige': Mock(), 'product': Mock()}
        mock_trainer.metadata = {
            'litige': {
                'training_date': '2026-04-18T12:00:00',
                'n_samples': 100,
                'n_features': 500,
                'n_classes': 5,
                'min_samples_per_class': 10,
                'class_counts': {'Type A': 50, 'Type B': 30, 'Type C': 20}
            }
        }
        mock_trainer.models_dir = 'models'

        # Should not raise any exceptions
        train_models.log_training_statistics(mock_trainer, logger)

        # Verify logger was called
        self.assertGreater(logger.info.call_count, 0)

    def test_log_training_statistics_no_models(self):
        """Test logging when no models are trained."""
        logger = Mock()

        mock_trainer = Mock()
        mock_trainer.vectorizers = {}

        train_models.log_training_statistics(mock_trainer, logger)

        # Should log a warning
        logger.warning.assert_called_once()

    def test_setup_logging(self):
        """Test logging setup."""
        with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            train_models.setup_logging(tmp_path)

            # Verify log file was created
            # (logging setup doesn't create file until first log)
            import logging
            test_logger = logging.getLogger('test_setup')
            test_logger.info('Test message')

        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestTrainModelsIntegration(unittest.TestCase):
    """Integration tests for train_models.py script."""

    @patch('train_models.DataLoader')
    @patch('train_models.Preprocessor')
    @patch('train_models.ModelTrainer')
    def test_main_success_with_existing_models(self, MockTrainer, MockPreprocessor, MockDataLoader):
        """Test main function with existing models."""
        # Setup mocks
        mock_loader = MockDataLoader.return_value
        mock_preprocessor = MockPreprocessor.return_value
        mock_trainer = MockTrainer.return_value

        # Mock data
        sample_df = pd.DataFrame({
            'description': ['Test 1', 'Test 2'],
            'Type de litige': ['Type A', 'Type B'],
            'Responsabilité': ['Resp A', 'Resp B'],
            'Précision produit': ['Prod A', 'Prod B'],
            'Solution': ['Sol A', 'Sol B']
        })

        preprocessed_df = sample_df.copy()
        preprocessed_df['description_features'] = sample_df['description']

        mock_loader.load_training_data.return_value = sample_df
        mock_preprocessor.preprocess_for_training.return_value = preprocessed_df
        mock_trainer.load_models.return_value = True
        mock_trainer.vectorizers = {'litige': Mock()}

        # Mock command-line arguments
        with patch('sys.argv', ['train_models.py', '--data-path', 'test/path']):
            with patch('os.path.exists', return_value=True):
                exit_code = train_models.main()

        # Verify success
        self.assertEqual(exit_code, 0)

    @patch('train_models.DataLoader')
    def test_main_file_not_found(self, MockDataLoader):
        """Test main function with missing data file."""
        mock_loader = MockDataLoader.return_value
        mock_loader.load_training_data.side_effect = FileNotFoundError(
            "File not found")

        with patch('sys.argv', ['train_models.py', '--data-path', 'nonexistent/path']):
            exit_code = train_models.main()

        # Verify failure
        self.assertEqual(exit_code, 1)


if __name__ == '__main__':
    unittest.main()
