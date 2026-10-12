"""
Warranty Engine Module

This module implements business rules to assess probable warranty eligibility
based on text pattern matching for common warranty exclusions.

"""

import re
from typing import Dict, List, Any, Optional
import logging

from config import (
    WARRANTY_HORS_GARANTIE,
    WARRANTY_INCERTAINE,
    WARRANTY_ELIGIBLE,
    WARRANTY_DISCLAIMER
)

logger = logging.getLogger(__name__)


class WarrantyEngine:
    """
    Evaluates probable warranty eligibility based on business rules and text patterns.

    This engine uses pattern matching to detect common warranty exclusion scenarios
    and provides an indicative assessment (not a legal decision).
    """

    def __init__(self):
        """
        Initialize the WarrantyEngine with exclusion patterns for 5 categories.

        Categories:
        1. Normal wear/aging
        2. Poor maintenance
        3. Handling damage
        4. Aggressive environment
        5. Hardware/accessories
        """
        self.exclusion_patterns = self._load_exclusion_patterns()
        logger.info("WarrantyEngine initialized with %d exclusion categories",
                    len(self.exclusion_patterns))

    def _load_exclusion_patterns(self) -> Dict[str, List[str]]:
        """
        Load warranty exclusion keyword patterns for each category.

        Returns:
            Dictionary mapping category names to lists of regex patterns
        """
        patterns = {
            # Category 1: Normal wear and aging
            "normal_wear": [
                r"\busure\b",
                r"\busure normale\b",
                r"vieillissement",
                r"vieilli",
                r"décoloration",
                r"décoloré",
                r"décolorée",
                r"patiné",
                r"patine",
                r"usé",
                r"usée",
                r"normal wear",
                r"aging",
                r"aged"
            ],

            # Category 2: Poor maintenance and installation
            "poor_maintenance": [
                r"mauvais entretien",
                r"défaut d'entretien",
                r"manque d'entretien",
                r"pas entretenu",
                r"non entretenu",
                r"installation non conforme",
                r"mal installé",
                r"mauvaise installation",
                r"pose non conforme",
                r"défaut de pose",
                r"installation incorrecte",
                r"poor maintenance",
                r"lack of maintenance",
                r"improper installation"
            ],

            # Category 3: Handling damage (shocks, scratches)
            "handling_damage": [
                r"\bchoc\b",
                r"\bchocs\b",
                r"rayure",
                r"rayé",
                r"rayée",
                r"griffure",
                r"griffé",
                r"griffée",
                r"dommage de manipulation",
                r"dommage de transport",
                r"coup",
                r"impact",
                r"éraflure",
                r"cabossé",
                r"bosselé",
                r"scratch",
                r"scratched",
                r"impact damage",
                r"handling damage"
            ],

            # Category 4: Aggressive environment
            "aggressive_environment": [
                r"environnement agressif",
                r"bord de mer",
                r"en bord de mer",
                r"près de la mer",
                r"zone côtière",
                r"corrosion",
                r"corrodé",
                r"rouille",
                r"rouillé",
                r"oxydation",
                r"oxydé",
                r"salin",
                r"sel",
                r"air marin",
                r"seaside",
                r"coastal",
                r"corrosion",
                r"rust",
                r"aggressive environment"
            ],

            # Category 5: Hardware, accessories, motors, electronics
            "hardware_accessories": [
                r"quincaillerie",
                r"accessoire",
                r"accessoires",
                r"moteur",
                r"motorisation",
                r"électronique",
                r"électrique",
                r"télécommande",
                r"capteur",
                r"carte électronique",
                r"circuit",
                r"batterie",
                r"pile",
                r"serrure",
                r"poignée",
                r"gond",
                r"charnière",
                r"hardware",
                r"accessories",
                r"motor",
                r"electronic",
                r"remote control"
            ]
        }

        return patterns

    def evaluate(self, reclamation_text: str, product_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Evaluate warranty eligibility based on text patterns.

        Args:
            reclamation_text: The complaint description text
            product_type: Optional product type for context (not used in MVP)

        Returns:
            Dictionary containing:
            - status: "hors_garantie_probable", "incertaine", or "eligible_probable"
            - reasons: List of human-readable reasons for the status
            - matched_patterns: Dictionary of matched patterns by category
            - disclaimer: Legal disclaimer text
        """
        if not reclamation_text or not isinstance(reclamation_text, str):
            logger.warning(
                "Invalid reclamation text provided to warranty engine")
            return {
                "status": WARRANTY_INCERTAINE,
                "reasons": ["Texte de réclamation invalide ou manquant"],
                "matched_patterns": {},
                "disclaimer": WARRANTY_DISCLAIMER
            }

        # Normalize text for pattern matching
        normalized_text = reclamation_text.strip().lower()

        # Check if text is empty after stripping whitespace
        if not normalized_text:
            logger.warning(
                "Empty reclamation text provided to warranty engine")
            return {
                "status": WARRANTY_INCERTAINE,
                "reasons": ["Texte de réclamation invalide ou manquant"],
                "matched_patterns": {},
                "disclaimer": WARRANTY_DISCLAIMER
            }

        # Track matched patterns by category
        matched_patterns: Dict[str, List[str]] = {}
        reasons: List[str] = []

        # Check each exclusion category
        for category, patterns in self.exclusion_patterns.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, normalized_text, re.IGNORECASE):
                    # Extract the matched text for reporting
                    match_obj = re.search(
                        pattern, normalized_text, re.IGNORECASE)
                    if match_obj:
                        matches.append(match_obj.group(0))

            if matches:
                matched_patterns[category] = list(
                    set(matches))  # Remove duplicates

        # Determine warranty status based on matches
        if matched_patterns:
            status = WARRANTY_HORS_GARANTIE

            # Generate human-readable reasons
            category_messages = {
                "normal_wear": "Mention d'usure normale ou vieillissement détecté",
                "poor_maintenance": "Mention de mauvais entretien ou installation non conforme détecté",
                "handling_damage": "Mention de choc, rayure ou dommage de manipulation détecté",
                "aggressive_environment": "Mention d'environnement agressif ou corrosion détecté",
                "hardware_accessories": "Mention de quincaillerie, accessoires ou composants électroniques détecté"
            }

            for category in matched_patterns.keys():
                if category in category_messages:
                    reasons.append(category_messages[category])

            logger.info(
                "Warranty exclusion detected: %d categories matched", len(matched_patterns))
        else:
            # No exclusion patterns found - warranty status uncertain
            # We cannot definitively say it's eligible without more context
            status = WARRANTY_INCERTAINE
            reasons = [
                "Aucun motif d'exclusion évident détecté dans la description",
                "Une analyse détaillée est nécessaire pour confirmer l'éligibilité"
            ]
            logger.info(
                "No warranty exclusion patterns detected - status uncertain")

        return {
            "status": status,
            "reasons": reasons,
            "matched_patterns": matched_patterns,
            "disclaimer": WARRANTY_DISCLAIMER
        }

    def get_exclusion_categories(self) -> List[str]:
        """
        Get the list of exclusion categories tracked by the engine.

        Returns:
            List of category names
        """
        return list(self.exclusion_patterns.keys())

    def get_patterns_for_category(self, category: str) -> List[str]:
        """
        Get the patterns for a specific exclusion category.

        Args:
            category: The category name

        Returns:
            List of regex patterns for that category
        """
        return self.exclusion_patterns.get(category, [])
