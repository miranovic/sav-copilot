"""
Complexity Scorer Module

This module calculates a complexity score based on data quality, prediction confidence,
and warranty status. It helps prioritize cases for quick resolution vs. expert review.

**Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12**
"""

import logging
from typing import Any, Dict

from config import (
    QUALITY_POOR,
    QUALITY_UNUSABLE,
    WARRANTY_INCERTAINE,
    QUICK_WIN_THRESHOLD,
    EXPERT_REVIEW_THRESHOLD,
    PRIORITY_QUICK_WIN,
    PRIORITY_STANDARD,
    PRIORITY_EXPERT,
    LEVEL_RAPIDE,
    LEVEL_STANDARD,
    LEVEL_COMPLEXE
)

logger = logging.getLogger(__name__)


class ComplexityScorer:
    """
    Calculates complexity score and assigns priority level based on analysis results.

    The complexity score is calculated by evaluating:
    - Data quality issues
    - Prediction confidence levels
    - Warranty uncertainty
    - Contradictory signals

    Higher scores indicate more complex cases requiring expert review.
    """

    def __init__(self):
        """Initialize the ComplexityScorer."""
        logger.info("ComplexityScorer initialized")

    def calculate(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate complexity score and assign priority.

        **Validates: Requirements 7.10, 7.11, 7.12**

        Args:
            analysis_result: Dictionary containing:
                - quality: Quality assessment from InputQualityAnalyzer
                - predictions: Predictions from Predictor
                - warranty: Warranty evaluation from WarrantyEngine

        Returns:
            Dictionary containing:
            {
                "score": 3,
                "level": "standard",
                "priority": "standard_review",
                "breakdown": {
                    "data_quality": 1,
                    "prediction_confidence": 1,
                    "warranty_uncertainty": 2,
                    "clarity_bonus": -1
                }
            }
        """
        # Extract components from analysis result
        quality = analysis_result.get("quality", {})
        predictions = analysis_result.get("predictions", {})
        warranty = analysis_result.get("warranty", {})

        # Initialize breakdown
        breakdown = {
            "data_quality": 0,
            "prediction_confidence": 0,
            "warranty_uncertainty": 0,
            "clarity_bonus": 0
        }

        # Calculate scores for each component
        breakdown["data_quality"] = self._score_data_quality(quality)
        breakdown["prediction_confidence"] = self._score_predictions(
            predictions)
        breakdown["warranty_uncertainty"] = self._score_warranty(warranty)
        breakdown["clarity_bonus"] = self._score_clarity(predictions)

        # Calculate total score
        total_score = sum(breakdown.values())

        # Assign priority and level based on score
        if total_score <= QUICK_WIN_THRESHOLD:
            priority = PRIORITY_QUICK_WIN
            level = LEVEL_RAPIDE
        elif total_score <= EXPERT_REVIEW_THRESHOLD - 1:  # 2-3 range
            priority = PRIORITY_STANDARD
            level = LEVEL_STANDARD
        else:  # >= 4
            priority = PRIORITY_EXPERT
            level = LEVEL_COMPLEXE

        result = {
            "score": total_score,
            "level": level,
            "priority": priority,
            "breakdown": breakdown
        }

        logger.info(
            f"Complexity score calculated: score={total_score}, "
            f"level={level}, priority={priority}"
        )
        logger.debug(f"Score breakdown: {breakdown}")

        return result

    def _score_data_quality(self, quality: Dict[str, Any]) -> int:
        """
        Score based on input quality.

        **Validates: Requirements 7.1, 7.9**

        Scoring rules:
        - +2: Important data missing (unusable quality)
        - +1: Poor quality detected
        - +1: Multiple attachments present (more complex to review)

        Args:
            quality: Quality assessment dictionary with:
                - status: "usable", "poor", or "unusable"
                - issues: List of detected issues
                - details: Dictionary with attachment_count, etc.

        Returns:
            Score contribution from data quality (0-3)
        """
        score = 0
        status = quality.get("status", "usable")
        issues = quality.get("issues", [])
        details = quality.get("details", {})

        # +2 for unusable quality (important data missing)
        if status == QUALITY_UNUSABLE:
            score += 2
            logger.debug("Data quality: +2 (unusable/important data missing)")

        # +1 for poor quality
        elif status == QUALITY_POOR:
            score += 1
            logger.debug("Data quality: +1 (poor quality)")

        # +1 for multiple attachments (more to review)
        attachment_count = details.get("attachment_count", 0)
        if attachment_count > 1:
            score += 1
            logger.debug(
                f"Data quality: +1 (multiple attachments: {attachment_count})")

        return score

    def _score_predictions(self, predictions: Dict[str, Any]) -> int:
        """
        Score based on prediction confidence.

        **Validates: Requirements 7.4, 7.5, 7.6, 7.8**

        Scoring rules:
        - +1: Solution confidence < 0.5 (low confidence)
        - +1: Responsibility confidence < 0.5 (low confidence)
        - +1: Contradictory signals detected (high confidence in one, low in another)

        Args:
            predictions: Predictions dictionary with:
                - solution: {prediction, confidence, available}
                - responsibility: {prediction, confidence, available}
                - litige_type: {prediction, confidence, available}
                - product_detail: {prediction, confidence, available}

        Returns:
            Score contribution from predictions (0-3)
        """
        score = 0

        # Extract confidence scores
        solution = predictions.get("solution", {})
        responsibility = predictions.get("responsibility", {})
        litige = predictions.get("litige_type", {})
        product = predictions.get("product_detail", {})

        solution_conf = solution.get("confidence", 0.0)
        responsibility_conf = responsibility.get("confidence", 0.0)
        litige_conf = litige.get("confidence", 0.0)
        product_conf = product.get("confidence", 0.0)

        # +1 for low solution confidence
        if solution_conf < 0.5:
            score += 1
            logger.debug(
                f"Predictions: +1 (low solution confidence: {solution_conf:.3f})")

        # +1 for low responsibility confidence
        if responsibility_conf < 0.5:
            score += 1
            logger.debug(
                f"Predictions: +1 (low responsibility confidence: {responsibility_conf:.3f})")

        # +1 for contradictory signals
        # Contradiction: at least one confidence > 0.7 and at least one < 0.4
        confidences = [solution_conf, responsibility_conf,
                       litige_conf, product_conf]
        has_high = any(c > 0.7 for c in confidences)
        has_low = any(c < 0.4 for c in confidences)

        if has_high and has_low:
            score += 1
            logger.debug(
                "Predictions: +1 (contradictory signals detected)")

        return score

    def _score_warranty(self, warranty: Dict[str, Any]) -> int:
        """
        Score based on warranty uncertainty.

        **Validates: Requirements 7.3**

        Scoring rules:
        - +2: Warranty status is "incertaine"

        Args:
            warranty: Warranty evaluation dictionary with:
                - status: "hors_garantie_probable", "incertaine", or "eligible_probable"
                - reasons: List of reasons
                - matched_patterns: Dictionary of matched patterns

        Returns:
            Score contribution from warranty (0 or 2)
        """
        score = 0
        status = warranty.get("status", "")

        # +2 for uncertain warranty status
        if status == WARRANTY_INCERTAINE:
            score += 2
            logger.debug("Warranty: +2 (uncertain warranty status)")

        return score

    def _score_clarity(self, predictions: Dict[str, Any]) -> int:
        """
        Score based on overall case clarity.

        **Validates: Requirements 7.6, 7.7**

        Scoring rules:
        - -1: Solution confidence > 0.8 (high confidence)
        - -1: Case is very clear (all confidences > 0.8)

        Note: This method returns negative scores (bonuses) for clear cases.

        Args:
            predictions: Predictions dictionary with confidence scores

        Returns:
            Score contribution from clarity (-2 to 0)
        """
        score = 0

        # Extract confidence scores
        solution = predictions.get("solution", {})
        responsibility = predictions.get("responsibility", {})
        litige = predictions.get("litige_type", {})
        product = predictions.get("product_detail", {})

        solution_conf = solution.get("confidence", 0.0)
        responsibility_conf = responsibility.get("confidence", 0.0)
        litige_conf = litige.get("confidence", 0.0)
        product_conf = product.get("confidence", 0.0)

        # -1 for high solution confidence
        if solution_conf > 0.8:
            score -= 1
            logger.debug(
                f"Clarity: -1 (high solution confidence: {solution_conf:.3f})")

        # -1 for very clear case (all confidences > 0.8)
        all_confidences = [solution_conf, responsibility_conf,
                           litige_conf, product_conf]
        if all(c > 0.8 for c in all_confidences):
            score -= 1
            logger.debug(
                "Clarity: -1 (very clear case, all confidences > 0.8)")

        return score
