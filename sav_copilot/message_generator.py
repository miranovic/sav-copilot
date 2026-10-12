"""
Message Generator Module

This module generates contextual customer messages based on analysis results.
Messages are in French, professional, and avoid making definitive legal warranty decisions.

"""

import logging
from typing import Any, Dict, List, Optional

from config import (
    QUALITY_POOR,
    QUALITY_UNUSABLE,
    WARRANTY_HORS_GARANTIE,
    LEVEL_RAPIDE
)

logger = logging.getLogger(__name__)


class MessageGenerator:
    """
    Generates contextual customer messages based on analysis results.

    The generator selects appropriate message templates based on:
    - Input quality status
    - Warranty evaluation
    - Complexity level
    - Prediction confidence
    """

    def __init__(self):
        """Initialize the MessageGenerator."""
        logger.info("MessageGenerator initialized")

    def generate(self, analysis_result: Dict[str, Any]) -> Optional[str]:
        """
        Generate appropriate customer message based on analysis.


        Message selection logic:
        1. If input quality is poor/unusable -> need_more_info message
        2. If warranty is hors_garantie_probable -> warranty_not_applicable message
        3. If complexity is rapide AND quality is usable AND solution confidence is high
           -> reassurance_fast_case message
        4. Otherwise -> None (no automatic message)

        Args:
            analysis_result: Dictionary containing:
                - quality: Quality assessment
                - warranty: Warranty evaluation
                - complexity: Complexity score
                - predictions: Prediction results

        Returns:
            Generated message string or None if no message is appropriate
        """
        # Extract components
        quality = analysis_result.get("quality", {})
        warranty = analysis_result.get("warranty", {})
        complexity = analysis_result.get("complexity", {})
        predictions = analysis_result.get("predictions", {})

        quality_status = quality.get("status", "usable")
        quality_issues = quality.get("issues", [])
        warranty_status = warranty.get("status", "")
        warranty_reasons = warranty.get("reasons", [])
        complexity_level = complexity.get("level", "")
        solution = predictions.get("solution", {})
        solution_confidence = solution.get("confidence", 0.0)

        # Priority 1: Request more info if quality is poor/unusable
        if quality_status in [QUALITY_POOR, QUALITY_UNUSABLE]:
            logger.info(
                f"Generating need_more_info message (quality: {quality_status})")
            return self._need_more_info_message(quality_issues)

        # Priority 2: Inform about probable warranty exclusion
        if warranty_status == WARRANTY_HORS_GARANTIE:
            logger.info(
                "Generating warranty_not_applicable message (warranty: hors_garantie_probable)")
            return self._warranty_not_applicable_message(warranty_reasons)

        # Priority 3: Reassure for quick-win cases
        if (complexity_level == LEVEL_RAPIDE and
            quality_status == "usable" and
                solution_confidence > 0.7):
            logger.info(
                f"Generating reassurance_fast_case message (complexity: {complexity_level}, "
                f"solution_confidence: {solution_confidence:.3f})"
            )
            return self._reassurance_fast_case_message()

        # No automatic message for standard/complex cases
        logger.info(
            "No automatic message generated (standard/complex case requiring manual review)")
        return None

    def _need_more_info_message(self, quality_issues: List[str]) -> str:
        """
        Generate message requesting additional information.


        This message is used when input quality is poor or unusable.
        It requests specific information based on detected issues.

        Args:
            quality_issues: List of detected quality issues
                (e.g., ["too_short", "missing_attachments"])

        Returns:
            French message requesting additional information
        """
        # Map issues to specific requests
        issue_requests = {
            "too_short": "- Une description plus détaillée du problème rencontré",
            "missing_attachments": "- Des photos ou documents illustrant le problème",
            "too_vague": "- Des précisions sur la nature exacte du défaut constaté"
        }

        # Build specific requests list
        specific_requests = []
        for issue in quality_issues:
            if issue in issue_requests:
                specific_requests.append(issue_requests[issue])

        # If no specific requests, use generic request
        if not specific_requests:
            specific_requests = [
                "- Des informations complémentaires sur votre réclamation"
            ]

        requests_text = "\n".join(specific_requests)

        message = f"""Bonjour,

Nous avons bien reçu votre réclamation. Pour traiter votre dossier efficacement, nous aurions besoin de quelques informations complémentaires :

{requests_text}

Merci de nous fournir ces éléments pour que nous puissions vous aider au mieux.

Cordialement,
Service Après-Vente"""

        logger.debug(
            f"Generated need_more_info message with {len(specific_requests)} requests")
        return message

    def _warranty_not_applicable_message(self, reasons: List[str]) -> str:
        """
        Generate message about probable warranty exclusion.


        This message informs the customer that their situation may not be covered
        by warranty, while being careful to avoid making definitive legal decisions.

        Args:
            reasons: List of reasons for warranty exclusion
                (e.g., ["Mention d'usure normale détectée"])

        Returns:
            French message about probable warranty exclusion
        """
        # Format reasons as bullet points
        if reasons:
            reasons_text = "\n".join(f"- {reason}" for reason in reasons)
        else:
            reasons_text = "- Les informations fournies suggèrent une situation hors garantie"

        message = f"""Bonjour,

Nous avons examiné votre réclamation. D'après les informations fournies, il semble que votre situation pourrait ne pas être couverte par la garantie pour les raisons suivantes :

{reasons_text}

Nous vous invitons à consulter les conditions de garantie ou à nous contacter pour plus de précisions.

Cordialement,
Service Après-Vente"""

        logger.debug(
            f"Generated warranty_not_applicable message with {len(reasons)} reasons")
        return message

    def _reassurance_fast_case_message(self) -> str:
        """
        Generate reassurance message for quick-win cases.


        This message is used for clear, simple cases that can be processed quickly.
        It reassures the customer that their case is being handled efficiently.

        Returns:
            French reassurance message
        """
        message = """Bonjour,

Nous avons bien reçu votre réclamation et nous vous remercions pour les informations fournies. Votre dossier est clair et nous allons le traiter rapidement.

Nous reviendrons vers vous sous peu avec une solution.

Cordialement,
Service Après-Vente"""

        logger.debug("Generated reassurance_fast_case message")
        return message
