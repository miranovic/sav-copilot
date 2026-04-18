"""
SAV Copilot - Machine Learning-powered decision support system for after-sales service.

This package provides automated pre-qualification of customer complaints by analyzing
complaint text and attachments to predict dispute type, responsibility, product details,
and recommended solutions.
"""

__version__ = "1.0.0"
__author__ = "SAV Copilot Team"

# Import main classes for easy access
from sav_copilot.data_loader import DataLoader
from sav_copilot.preprocessor import Preprocessor
from sav_copilot.trainer import ModelTrainer
from sav_copilot.predictor import Predictor
from sav_copilot.quality_analyzer import InputQualityAnalyzer
from sav_copilot.warranty_engine import WarrantyEngine
from sav_copilot.complexity_scorer import ComplexityScorer
from sav_copilot.message_generator import MessageGenerator
from sav_copilot.pipeline import analyze_reclamation, AnalysisResult

__all__ = [
    "DataLoader",
    "Preprocessor",
    "ModelTrainer",
    "Predictor",
    "InputQualityAnalyzer",
    "WarrantyEngine",
    "ComplexityScorer",
    "MessageGenerator",
    "analyze_reclamation",
    "AnalysisResult",
]
