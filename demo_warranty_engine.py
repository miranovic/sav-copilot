"""
Demo script for the WarrantyEngine module.

This script demonstrates the warranty eligibility assessment functionality.
"""

from sav_copilot.warranty_engine import WarrantyEngine


def print_result(text: str, result: dict):
    """Pretty print warranty evaluation result."""
    print(f"\n{'='*70}")
    print(f"Texte: {text}")
    print(f"{'='*70}")
    print(f"Statut: {result['status']}")
    print(f"\nRaisons:")
    for reason in result['reasons']:
        print(f"  - {reason}")

    if result['matched_patterns']:
        print(f"\nMotifs détectés:")
        for category, matches in result['matched_patterns'].items():
            print(f"  {category}: {', '.join(matches)}")

    print(f"\nDisclaimer: {result['disclaimer']}")


def main():
    """Run warranty engine demo with various test cases."""
    print("=== Démonstration du Moteur de Garantie ===\n")

    # Initialize the engine
    engine = WarrantyEngine()
    print(
        f"Moteur initialisé avec {len(engine.get_exclusion_categories())} catégories d'exclusion\n")

    # Test cases
    test_cases = [
        # Normal wear
        "Le portail montre des signes d'usure normale après 5 ans",

        # Poor maintenance
        "Le problème vient d'un mauvais entretien et d'une installation non conforme",

        # Handling damage
        "Le portail a subi un choc lors de la livraison et présente des rayures",

        # Aggressive environment
        "Installation en bord de mer, corrosion visible sur les éléments métalliques",

        # Hardware/accessories
        "Problème avec le moteur et la carte électronique de la télécommande",

        # Multiple exclusions
        "Portail installé en bord de mer avec usure normale et rayures",

        # No exclusions (uncertain)
        "Le portail ne ferme pas correctement, défaut de fabrication apparent",

        # Empty text
        ""
    ]

    for text in test_cases:
        result = engine.evaluate(text)
        print_result(text if text else "(texte vide)", result)

    print(f"\n{'='*70}")
    print("Démonstration terminée")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
