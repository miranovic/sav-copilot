"""
Prediction module for SAV Copilot.

This module generates predictions with confidence scores for new complaints using
the trained TF-IDF + LogisticRegression models. It handles missing models gracefully
and provides structured output with confidence scores.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from sav_copilot.trainer import ModelTrainer

logger = logging.getLogger(__name__)


class Predictor:
    """Generates predictions with confidence scores for new complaints."""

    def __init__(self, trainer: ModelTrainer):
        """
        Initialize the Predictor with a trained ModelTrainer.

        Args:
            trainer: ModelTrainer instance with loaded models
        """
        self.trainer = trainer
        logger.info("Predictor initialized")

    def predict_single(self, text: str, target: str) -> Dict[str, Any]:
        """
        Predict one target with confidence score.

        This method uses the trained model for the specified target to predict
        the most likely class and its confidence score.

        Args:
            text: Complaint text to analyze
            target: Target name (e.g., 'litige', 'responsibility', 'product', 'solution')

        Returns:
            Dictionary with prediction and confidence:
            {
                "prediction": "Défaut de fabrication",
                "confidence": 0.87,
                "available": True
            }

            If model is unavailable:
            {
                "prediction": "unknown",
                "confidence": 0.0,
                "available": False
            }
        """
        # Check if model is available
        if target not in self.trainer.vectorizers or target not in self.trainer.classifiers:
            logger.warning(
                f"Model for target '{target}' not available. Returning fallback.")
            return {
                "prediction": "unknown",
                "confidence": 0.0,
                "available": False
            }

        try:
            # Get vectorizer and classifier
            vectorizer = self.trainer.vectorizers[target]
            classifier = self.trainer.classifiers[target]

            # Transform text to TF-IDF features
            X = vectorizer.transform([text])

            # Get prediction
            prediction = classifier.predict(X)[0]

            # Get confidence score (probability of predicted class)
            probabilities = classifier.predict_proba(X)[0]
            predicted_class_idx = classifier.classes_.tolist().index(prediction)
            confidence = float(probabilities[predicted_class_idx])

            logger.debug(
                f"Predicted {target}: {prediction} (confidence: {confidence:.3f})")

            return {
                "prediction": prediction,
                "confidence": confidence,
                "available": True
            }

        except Exception as e:
            logger.error(
                f"Error predicting target '{target}': {e}", exc_info=True)
            return {
                "prediction": "unknown",
                "confidence": 0.0,
                "available": False,
                "error": str(e)
            }

    def predict_top_k(self, text: str, target: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Get top K predictions with confidence scores.

        This method returns the K most likely classes for the specified target,
        sorted by confidence score in descending order.

        Args:
            text: Complaint text to analyze
            target: Target name (e.g., 'litige', 'responsibility', 'product', 'solution')
            k: Number of top predictions to return (default: 3)

        Returns:
            List of dictionaries with predictions and confidence scores:
            [
                {"label": "Remplacement pièce", "confidence": 0.81},
                {"label": "Réparation sur site", "confidence": 0.12},
                {"label": "Remboursement", "confidence": 0.05}
            ]

            If model is unavailable, returns empty list.
        """
        # Check if model is available
        if target not in self.trainer.vectorizers or target not in self.trainer.classifiers:
            logger.warning(
                f"Model for target '{target}' not available. Returning empty list.")
            return []

        try:
            # Get vectorizer and classifier
            vectorizer = self.trainer.vectorizers[target]
            classifier = self.trainer.classifiers[target]

            # Transform text to TF-IDF features
            X = vectorizer.transform([text])

            # Get probabilities for all classes
            probabilities = classifier.predict_proba(X)[0]
            classes = classifier.classes_

            # Create list of (class, probability) tuples
            class_probs = list(zip(classes, probabilities))

            # Sort by probability in descending order
            class_probs.sort(key=lambda x: x[1], reverse=True)

            # Take top K
            top_k = class_probs[:k]

            # Format results
            results = [
                {
                    "label": str(label),
                    "confidence": float(prob)
                }
                for label, prob in top_k
            ]

            logger.debug(
                f"Top {k} predictions for {target}: {[r['label'] for r in results]}")

            return results

        except Exception as e:
            logger.error(
                f"Error getting top-K predictions for target '{target}': {e}",
                exc_info=True
            )
            return []

    def predict_all(self, text: str) -> Dict[str, Any]:
        """
        Predict all four targets (litige, responsibility, product, solution).

        This method runs predictions for all classification targets and returns
        a structured result with predictions, confidence scores, and top-K
        alternatives for the solution.

        Args:
            text: Complaint text to analyze

        Returns:
            Dictionary with all predictions:
            {
                "litige_type": {
                    "prediction": "Défaut de fabrication",
                    "confidence": 0.87,
                    "available": True
                },
                "responsibility": {
                    "prediction": "Fabricant",
                    "confidence": 0.72,
                    "available": True
                },
                "product_detail": {
                    "prediction": "Portail coulissant",
                    "confidence": 0.65,
                    "available": True
                },
                "solution": {
                    "prediction": "Remplacement pièce",
                    "confidence": 0.81,
                    "available": True,
                    "top_3": [
                        {"label": "Remplacement pièce", "confidence": 0.81},
                        {"label": "Réparation sur site", "confidence": 0.12},
                        {"label": "Remboursement", "confidence": 0.05}
                    ]
                }
            }
        """
        logger.info("Predicting all targets for complaint text")

        # Predict each target
        litige = self.predict_single(text, "litige")
        responsibility = self.predict_single(text, "responsibility")
        product = self.predict_single(text, "product")
        solution = self.predict_single(text, "solution")

        # Get top 3 solutions
        solution_top_3 = self.predict_top_k(text, "solution", k=3)

        # Add top_3 to solution result
        solution["top_3"] = solution_top_3

        # Construct result
        result = {
            "litige_type": litige,
            "responsibility": responsibility,
            "product_detail": product,
            "solution": solution
        }

        # Log summary
        available_count = sum(
            1 for v in result.values() if v.get("available", False))
        logger.info(
            f"Prediction complete: {available_count}/4 models available")

        return result
