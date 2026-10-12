"""
Input Quality Analyzer module for SAV Copilot.

This module assesses the quality and completeness of input data to detect poor quality
or incomplete inputs. It flags issues like short descriptions, missing attachments,
and vague text, and returns an overall quality status.
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class InputQualityAnalyzer:
    """Assesses the quality and completeness of input data."""

    def __init__(
        self,
        min_description_length: int = 20,
        min_meaningful_words: int = 5
    ):
        """
        Initialize the InputQualityAnalyzer.

        Args:
            min_description_length: Minimum character length for descriptions (default: 20)
            min_meaningful_words: Minimum number of meaningful words (default: 5)
        """
        self.min_description_length = min_description_length
        self.min_meaningful_words = min_meaningful_words

        # Common French stop words to exclude from meaningful word count
        self.stop_words = {
            'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du',
            'et', 'ou', 'mais', 'donc', 'or', 'ni', 'car',
            'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
            'ce', 'cet', 'cette', 'ces',
            'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses',
            'à', 'au', 'aux', 'en', 'dans', 'sur', 'sous', 'pour', 'par',
            'avec', 'sans', 'chez',
            'est', 'sont', 'a', 'ont', 'ai', 'as', 'avons', 'avez',
            'être', 'avoir', 'faire',
            'qui', 'que', 'quoi', 'dont', 'où',
            'si', 'ne', 'pas', 'plus', 'très', 'bien', 'mal',
            'y', 'en'
        }

        logger.info(
            f"InputQualityAnalyzer initialized with min_length={min_description_length}, "
            f"min_words={min_meaningful_words}"
        )

    def check_description_length(self, text: str) -> Optional[str]:
        """
        Flag if description is too short.


        Args:
            text: Description text to check

        Returns:
            Issue string if description is too short, None otherwise
        """
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        text = text.strip()
        length = len(text)

        if length < self.min_description_length:
            logger.debug(
                f"Description too short: {length} characters "
                f"(minimum: {self.min_description_length})"
            )
            return "too_short"

        return None

    def check_attachments(self, attachments: List[str]) -> Optional[str]:
        """
        Flag if attachments are missing.


        Args:
            attachments: List of attachment filenames

        Returns:
            Issue string if attachments are missing, None otherwise
        """
        if not attachments or len(attachments) == 0:
            logger.debug("No attachments found")
            return "missing_attachments"

        # Filter out empty strings or None values
        valid_attachments = [a for a in attachments if a and str(a).strip()]

        if len(valid_attachments) == 0:
            logger.debug("No valid attachments found")
            return "missing_attachments"

        return None

    def check_vagueness(self, text: str) -> Optional[str]:
        """
        Flag if description is too vague (fewer than minimum meaningful words).


        Meaningful words are defined as words that are:
        - At least 2 characters long
        - Not in the stop words list
        - Alphanumeric (not just punctuation)

        Args:
            text: Description text to check

        Returns:
            Issue string if description is too vague, None otherwise
        """
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        text = text.strip().lower()

        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b\w+\b', text)

        # Count meaningful words (not stop words, at least 2 chars)
        meaningful_words = [
            word for word in words
            if len(word) >= 2 and word not in self.stop_words
        ]

        meaningful_count = len(meaningful_words)

        if meaningful_count < self.min_meaningful_words:
            logger.debug(
                f"Description too vague: {meaningful_count} meaningful words "
                f"(minimum: {self.min_meaningful_words})"
            )
            return "too_vague"

        return None

    def _count_meaningful_words(self, text: str) -> int:
        """
        Count the number of meaningful words in text.

        Helper method for detailed statistics.

        Args:
            text: Text to analyze

        Returns:
            Count of meaningful words
        """
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        text = text.strip().lower()
        words = re.findall(r'\b\w+\b', text)

        meaningful_words = [
            word for word in words
            if len(word) >= 2 and word not in self.stop_words
        ]

        return len(meaningful_words)

    def analyze(self, reclamation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze input quality and return status + issues.


        This method performs all quality checks and determines an overall
        usability status:
        - "usable": No critical issues, can be processed
        - "poor": Some issues detected, may need additional info
        - "unusable": Critical issues, cannot be processed reliably

        Args:
            reclamation: Dictionary containing reclamation data with keys:
                - 'description': Complaint text
                - 'attachments': List of attachment filenames (optional)

        Returns:
            Dictionary with quality assessment:
            {
                "status": "usable" | "poor" | "unusable",
                "issues": ["too_short", "missing_attachments"],
                "details": {
                    "description_length": 15,
                    "attachment_count": 0,
                    "meaningful_word_count": 3
                }
            }
        """
        # Extract description and attachments
        description = reclamation.get('description', '')
        attachments = reclamation.get('attachments', [])

        # Ensure attachments is a list
        if not isinstance(attachments, list):
            if attachments:
                attachments = [attachments]
            else:
                attachments = []

        # Run all quality checks
        issues = []

        length_issue = self.check_description_length(description)
        if length_issue:
            issues.append(length_issue)

        attachment_issue = self.check_attachments(attachments)
        if attachment_issue:
            issues.append(attachment_issue)

        vagueness_issue = self.check_vagueness(description)
        if vagueness_issue:
            issues.append(vagueness_issue)

        # Calculate detailed statistics
        description_length = len(description.strip()) if isinstance(
            description, str) else 0
        attachment_count = len(
            [a for a in attachments if a and str(a).strip()])
        meaningful_word_count = self._count_meaningful_words(description)

        # Determine overall status
        status = self._determine_status(issues)

        result = {
            "status": status,
            "issues": issues,
            "details": {
                "description_length": description_length,
                "attachment_count": attachment_count,
                "meaningful_word_count": meaningful_word_count
            }
        }

        logger.info(
            f"Quality analysis complete: status={status}, "
            f"issues={len(issues)}, "
            f"length={description_length}, "
            f"attachments={attachment_count}, "
            f"meaningful_words={meaningful_word_count}"
        )

        return result

    def _determine_status(self, issues: List[str]) -> str:
        """
        Determine overall quality status based on detected issues.

        Status determination logic:
        - "unusable": Multiple critical issues (too_short AND too_vague)
        - "poor": One or more issues detected
        - "usable": No issues detected

        Args:
            issues: List of detected issue strings

        Returns:
            Quality status: "usable", "poor", or "unusable"
        """
        if not issues:
            return "usable"

        # Check for multiple critical issues
        critical_issues = {"too_short", "too_vague"}
        detected_critical = set(issues) & critical_issues

        if len(detected_critical) >= 2:
            # Both too_short and too_vague = unusable
            return "unusable"

        # Any issues = poor quality
        return "poor"
