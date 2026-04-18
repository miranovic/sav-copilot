"""
Demo script for InputQualityAnalyzer.

This script demonstrates the quality analysis functionality with various
example reclamations.
"""

from sav_copilot.quality_analyzer import InputQualityAnalyzer


def print_analysis(title, reclamation, result):
    """Print analysis results in a formatted way."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"Description: {reclamation.get('description', 'N/A')}")
    print(f"Attachments: {reclamation.get('attachments', [])}")
    print(f"\nStatus: {result['status'].upper()}")
    print(
        f"Issues: {', '.join(result['issues']) if result['issues'] else 'None'}")
    print(f"\nDetails:")
    print(
        f"  - Description length: {result['details']['description_length']} characters")
    print(f"  - Attachment count: {result['details']['attachment_count']}")
    print(
        f"  - Meaningful words: {result['details']['meaningful_word_count']}")


def main():
    """Run quality analyzer demo."""
    print("SAV Copilot - Input Quality Analyzer Demo")
    print("=" * 70)

    # Initialize analyzer
    analyzer = InputQualityAnalyzer(
        min_description_length=20,
        min_meaningful_words=5
    )

    # Example 1: High quality input
    reclamation1 = {
        "description": "Le portail coulissant présente un défaut de fabrication important avec rayures visibles sur le panneau principal.",
        "attachments": ["photo1.jpg", "photo2.jpg", "facture.pdf"]
    }
    result1 = analyzer.analyze(reclamation1)
    print_analysis("Example 1: High Quality Input", reclamation1, result1)

    # Example 2: Short description
    reclamation2 = {
        "description": "Portail cassé",
        "attachments": ["photo1.jpg"]
    }
    result2 = analyzer.analyze(reclamation2)
    print_analysis("Example 2: Short Description", reclamation2, result2)

    # Example 3: Missing attachments
    reclamation3 = {
        "description": "Le portail coulissant présente un défaut de fabrication important.",
        "attachments": []
    }
    result3 = analyzer.analyze(reclamation3)
    print_analysis("Example 3: Missing Attachments", reclamation3, result3)

    # Example 4: Vague description
    reclamation4 = {
        "description": "Le portail est cassé maintenant",
        "attachments": ["photo1.jpg"]
    }
    result4 = analyzer.analyze(reclamation4)
    print_analysis("Example 4: Vague Description", reclamation4, result4)

    # Example 5: Multiple issues (unusable)
    reclamation5 = {
        "description": "Cassé",
        "attachments": []
    }
    result5 = analyzer.analyze(reclamation5)
    print_analysis("Example 5: Multiple Critical Issues",
                   reclamation5, result5)

    # Example 6: Empty reclamation
    reclamation6 = {}
    result6 = analyzer.analyze(reclamation6)
    print_analysis("Example 6: Empty Reclamation", reclamation6, result6)

    print(f"\n{'='*70}")
    print("Demo complete!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
