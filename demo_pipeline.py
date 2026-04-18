"""
Demo script for the complete analysis pipeline.

This script demonstrates the end-to-end analysis orchestration using
the pipeline module with pre-trained models.
"""

import logging
from sav_copilot.pipeline import analyze_reclamation
from sav_copilot.trainer import ModelTrainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 80 + "\n")


def print_analysis_result(result):
    """
    Print analysis result in a formatted way.

    Args:
        result: AnalysisResult object
    """
    print_separator()
    print("ANALYSIS RESULT")
    print_separator()

    # Reclamation info
    print("RECLAMATION:")
    print(f"  Description: {result.reclamation['description'][:100]}...")
    print(f"  Attachments: {len(result.reclamation.get('attachments', []))}")

    # Predictions
    print("\nPREDICTIONS:")
    for key, value in result.predictions.items():
        if value.get('available', False):
            print(
                f"  {key}: {value['prediction']} (confidence: {value['confidence']:.3f})")
        else:
            print(f"  {key}: Not available")

    # Solution alternatives
    if result.predictions.get('solution', {}).get('top_3'):
        print("\n  Top 3 Solutions:")
        for i, sol in enumerate(result.predictions['solution']['top_3'], 1):
            print(
                f"    {i}. {sol['label']} (confidence: {sol['confidence']:.3f})")

    # Quality assessment
    print("\nQUALITY ASSESSMENT:")
    print(f"  Status: {result.quality['status']}")
    if result.quality['issues']:
        print(f"  Issues: {', '.join(result.quality['issues'])}")
    print(
        f"  Description length: {result.quality['details']['description_length']} chars")
    print(f"  Attachments: {result.quality['details']['attachment_count']}")
    print(
        f"  Meaningful words: {result.quality['details']['meaningful_word_count']}")

    # Warranty evaluation
    print("\nWARRANTY EVALUATION:")
    print(f"  Status: {result.warranty['status']}")
    if result.warranty['reasons']:
        print("  Reasons:")
        for reason in result.warranty['reasons']:
            print(f"    - {reason}")
    if result.warranty['matched_patterns']:
        print("  Matched patterns:")
        for category, patterns in result.warranty['matched_patterns'].items():
            print(f"    {category}: {', '.join(patterns)}")

    # Complexity score
    print("\nCOMPLEXITY SCORE:")
    print(f"  Score: {result.complexity['score']}")
    print(f"  Level: {result.complexity['level']}")
    print(f"  Priority: {result.complexity['priority']}")
    print("  Breakdown:")
    for component, score in result.complexity['breakdown'].items():
        print(f"    {component}: {score:+d}")

    # Customer message
    print("\nCUSTOMER MESSAGE:")
    if result.message:
        print(f"  {result.message[:200]}...")
    else:
        print("  No automatic message (manual review required)")

    # Processing time
    print(f"\nPROCESSING TIME: {result.processing_time:.3f} seconds")
    print_separator()


def main():
    """Run pipeline demo with sample reclamations."""
    print("SAV COPILOT - PIPELINE DEMO")
    print_separator()

    # Load models
    print("Loading trained models...")
    trainer = ModelTrainer(models_dir="models")
    models_loaded = trainer.load_models()

    if not models_loaded:
        print("ERROR: No trained models found. Please run train_models.py first.")
        return

    print(f"Successfully loaded {len(trainer.vectorizers)} model(s)")

    # Sample reclamations
    reclamations = [
        {
            "description": "Le portail coulissant ne ferme pas correctement depuis 2 semaines. "
            "Il reste bloqué à mi-course et fait un bruit anormal. "
            "J'ai essayé de le nettoyer mais le problème persiste.",
            "attachments": ["photo1.jpg", "photo2.jpg"]
        },
        {
            "description": "Usure normale du portail après 10 ans d'utilisation. "
            "La peinture est décolorée et il y a des traces de rouille "
            "car nous habitons en bord de mer.",
            "attachments": ["photo_rouille.jpg"]
        },
        {
            "description": "Problème",
            "attachments": []
        },
        {
            "description": "Le portail a été endommagé lors de la livraison. "
            "Il y a plusieurs rayures importantes et une bosse sur le panneau gauche. "
            "Le livreur a reconnu avoir heurté le portail avec son camion.",
            "attachments": ["photo_rayure1.jpg", "photo_rayure2.jpg", "photo_bosse.jpg"]
        }
    ]

    # Analyze each reclamation
    for i, reclamation in enumerate(reclamations, 1):
        print(f"\n\nANALYZING RECLAMATION #{i}")
        print(f"Description: {reclamation['description'][:80]}...")

        try:
            result = analyze_reclamation(reclamation, trainer=trainer)
            print_analysis_result(result)
        except Exception as e:
            print(f"ERROR: Failed to analyze reclamation: {e}")
            logger.error(
                f"Analysis failed for reclamation #{i}", exc_info=True)

    print("\n\nDEMO COMPLETED")
    print_separator()


if __name__ == "__main__":
    main()
