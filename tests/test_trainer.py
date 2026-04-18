"""
Unit tests for the ModelTrainer class.
"""

import os
import tempfile
import shutil
from unittest.mock import patch

import pandas as pd
import pytest

from sav_copilot.trainer import ModelTrainer


class TestModelTrainer:
    """Test suite for ModelTrainer class."""

    @pytest.fixture
    def sample_training_data(self):
        """Create sample training data for testing."""
        data = {
            'description_features': [
                'Portail coulissant défectueux',
                'Problème de rouille sur la clôture',
                'Défaut de fabrication sur le portail',
                'Usure normale du produit',
                'Mauvais entretien causant des dommages',
                'Pièce cassée nécessitant remplacement',
                'Corrosion due à environnement agressif',
                'Installation non conforme',
                'Rayure sur le portail',
                'Décoloration naturelle du produit'
            ],
            'Type de litige': [
                'Défaut de fabrication',
                'Défaut de fabrication',
                'Défaut de fabrication',
                'Usure normale',
                'Mauvais entretien',
                'Défaut de fabrication',
                'Environnement agressif',
                'Installation',
                'Dommage manipulation',
                'Usure normale'
            ],
            'Responsabilité': [
                'Fabricant',
                'Fabricant',
                'Fabricant',
                'Client',
                'Client',
                'Fabricant',
                'Client',
                'Installateur',
                'Client',
                'Client'
            ],
            'Solution': [
                'Remplacement pièce',
                'Réparation sur site',
                'Remplacement pièce',
                'Refus garantie',
                'Refus garantie',
                'Remplacement pièce',
                'Refus garantie',
                'Réparation installateur',
                'Refus garantie',
                'Refus garantie'
            ]
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def temp_models_dir(self):
        """Create a temporary directory for model storage."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup after test
        shutil.rmtree(temp_dir)

    def test_init_creates_models_directory(self, temp_models_dir):
        """Test that __init__ creates the models directory."""
        models_dir = os.path.join(temp_models_dir, "new_models")
        assert not os.path.exists(models_dir)

        trainer = ModelTrainer(models_dir=models_dir)

        assert os.path.exists(models_dir)
        assert trainer.models_dir == models_dir
        assert isinstance(trainer.vectorizers, dict)
        assert isinstance(trainer.classifiers, dict)
        assert isinstance(trainer.metadata, dict)

    def test_train_classifier_success(self, sample_training_data, temp_models_dir):
        """Test successful training of a single classifier."""
        trainer = ModelTrainer(models_dir=temp_models_dir)

        X = sample_training_data['description_features']
        y = sample_training_data['Type de litige']

        vectorizer, classifier = trainer.train_classifier(X, y, 'litige')

        # Verify vectorizer
        assert vectorizer is not None
        assert hasattr(vectorizer, 'transform')

        # Verify classifier
        assert classifier is not None
        assert hasattr(classifier, 'predict')
        assert hasattr(classifier, 'predict_proba')

        # Verify metadata was stored
        assert 'litige' in trainer.metadata
        metadata = trainer.metadata['litige']
        assert 'training_date' in metadata
        assert 'n_samples' in metadata
        assert 'n_features' in metadata
        assert 'n_classes' in metadata
        assert metadata['n_samples'] == 10

    def test_train_classifier_with_missing_values(self, temp_models_dir):
        """Test training with missing values in data."""
        trainer = ModelTrainer(models_dir=temp_models_dir)

        # Create data with missing values
        X = pd.Series([
            'Text 1',
            None,
            'Text 3',
            'Text 4',
            'Text 5'
        ])
        y = pd.Series([
            'Class A',
            'Class B',
            'Class A',
            'Class B',
            'Class A'
        ])

        vectorizer, classifier = trainer.train_classifier(X, y, 'test_target')

        # Should successfully train on non-missing values
        assert vectorizer is not None
        assert classifier is not None
        # One NaN removed
        assert trainer.metadata['test_target']['n_samples'] == 4

    def test_train_classifier_empty_data(self, temp_models_dir):
        """Test that training with empty data raises ValueError."""
        trainer = ModelTrainer(models_dir=temp_models_dir)

        X = pd.Series([])
        y = pd.Series([])

        with pytest.raises(ValueError, match="empty training data"):
            trainer.train_classifier(X, y, 'test_target')

    def test_train_classifier_mismatched_lengths(self, temp_models_dir):
        """Test that mismatched X and y lengths raise ValueError."""
        trainer = ModelTrainer(models_dir=temp_models_dir)

        X = pd.Series(['Text 1', 'Text 2', 'Text 3'])
        y = pd.Series(['Class A', 'Class B'])

        with pytest.raises(ValueError, match="different lengths"):
            trainer.train_classifier(X, y, 'test_target')

    def test_train_all_success(self, sample_training_data, temp_models_dir):
        """Test training all classifiers successfully."""
        trainer = ModelTrainer(models_dir=temp_models_dir)

        target_columns = ['Type de litige', 'Responsabilité', 'Solution']

        trainer.train_all(
            df=sample_training_data,
            text_column='description_features',
            target_columns=target_columns
        )

        # Verify all models were trained
        assert len(trainer.vectorizers) == 3
        assert len(trainer.classifiers) == 3

        # Check that models exist for expected targets
        # Note: train_all maps column names to short names from config
        assert 'litige' in trainer.vectorizers
        assert 'responsibility' in trainer.vectorizers
        assert 'solution' in trainer.vectorizers

    def test_train_all_missing_text_column(self, sample_training_data, temp_models_dir):
        """Test that missing text column raises ValueError."""
        trainer = ModelTrainer(models_dir=temp_models_dir)

        with pytest.raises(ValueError, match="Text column.*not found"):
            trainer.train_all(
                df=sample_training_data,
                text_column='nonexistent_column',
                target_columns=['Type de litige']
            )

    def test_save_models(self, sample_training_data, temp_models_dir):
        """Test saving models to disk."""
        trainer = ModelTrainer(models_dir=temp_models_dir)

        # Train a simple model
        X = sample_training_data['description_features']
        y = sample_training_data['Type de litige']
        vectorizer, classifier = trainer.train_classifier(X, y, 'litige')

        trainer.vectorizers['litige'] = vectorizer
        trainer.classifiers['litige'] = classifier

        # Save models
        trainer.save_models()

        # Verify files were created
        assert os.path.exists(os.path.join(
            temp_models_dir, 'litige_vectorizer.joblib'))
        assert os.path.exists(os.path.join(
            temp_models_dir, 'litige_classifier.joblib'))
        assert os.path.exists(os.path.join(
            temp_models_dir, 'litige_metadata.joblib'))

    def test_load_models(self, sample_training_data, temp_models_dir):
        """Test loading models from disk."""
        # First, train and save models
        trainer1 = ModelTrainer(models_dir=temp_models_dir)
        X = sample_training_data['description_features']
        y = sample_training_data['Type de litige']
        vectorizer, classifier = trainer1.train_classifier(X, y, 'litige')

        trainer1.vectorizers['litige'] = vectorizer
        trainer1.classifiers['litige'] = classifier
        trainer1.save_models()

        # Now load models in a new trainer instance
        trainer2 = ModelTrainer(models_dir=temp_models_dir)
        success = trainer2.load_models()

        assert success is True
        assert 'litige' in trainer2.vectorizers
        assert 'litige' in trainer2.classifiers
        assert 'litige' in trainer2.metadata

    def test_load_models_no_directory(self, temp_models_dir):
        """Test loading models when directory doesn't exist."""
        nonexistent_dir = os.path.join(temp_models_dir, "nonexistent")
        trainer = ModelTrainer(models_dir=nonexistent_dir)

        success = trainer.load_models()

        assert success is False

    def test_load_models_empty_directory(self, temp_models_dir):
        """Test loading models from empty directory."""
        trainer = ModelTrainer(models_dir=temp_models_dir)

        success = trainer.load_models()

        assert success is False

    def test_train_all_with_insufficient_data_warning(self, temp_models_dir, caplog):
        """Test that training with insufficient data logs warnings and fails."""
        trainer = ModelTrainer(models_dir=temp_models_dir)

        # Create data with only one class
        data = pd.DataFrame({
            'text': ['Sample 1', 'Sample 2', 'Sample 3'],
            'target': ['Class A', 'Class A', 'Class A']
        })

        # Should raise ValueError because no classifiers can be trained
        with pytest.raises(ValueError, match="No classifiers were successfully trained"):
            with caplog.at_level('WARNING'):
                trainer.train_all(
                    df=data,
                    text_column='text',
                    target_columns=['target']
                )

        # Should log warning about single class
        assert any(
            'only 1 unique class' in record.message for record in caplog.records)

    def test_save_models_no_models(self, temp_models_dir, caplog):
        """Test saving when no models have been trained."""
        trainer = ModelTrainer(models_dir=temp_models_dir)

        with caplog.at_level('WARNING'):
            trainer.save_models()

        assert any(
            'No models to save' in record.message for record in caplog.records)

    def test_model_persistence_roundtrip(self, sample_training_data, temp_models_dir):
        """Test that models work correctly after save/load cycle."""
        # Train and save
        trainer1 = ModelTrainer(models_dir=temp_models_dir)
        trainer1.train_all(
            df=sample_training_data,
            text_column='description_features',
            target_columns=['Type de litige']
        )
        trainer1.save_models()

        # Load in new instance
        trainer2 = ModelTrainer(models_dir=temp_models_dir)
        trainer2.load_models()

        # Test prediction with loaded model
        test_text = ['Portail défectueux avec rouille']
        vectorizer = trainer2.vectorizers['litige']
        classifier = trainer2.classifiers['litige']

        X_test = vectorizer.transform(test_text)
        prediction = classifier.predict(X_test)

        assert len(prediction) == 1
        assert isinstance(prediction[0], str)
