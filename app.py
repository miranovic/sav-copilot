"""
Streamlit UI for SAV Copilot

This module provides the web interface for demonstrating the SAV Copilot system.
It allows operators to analyze customer complaints and view complete analysis results.

"""

import streamlit as st
import logging
from typing import Dict, Any, Optional
import os
import pandas as pd

from sav_copilot.pipeline import analyze_reclamation
from sav_copilot.trainer import ModelTrainer
from sav_copilot.data_loader import DataLoader
from config import MODELS_DIR, TRAINING_DATA_PATH, TRAINING_EXCEL_FILE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_models() -> Optional[ModelTrainer]:
    """
    Initialize and load models on startup.

    Returns:
        ModelTrainer instance with loaded models, or None if loading fails
    """
    try:
        trainer = ModelTrainer(models_dir=MODELS_DIR)
        models_loaded = trainer.load_models()

        if models_loaded:
            logger.info(
                f"Successfully loaded {len(trainer.vectorizers)} model(s)")
            return trainer
        else:
            logger.warning("No models found. Please train models first.")
            return None
    except Exception as e:
        logger.error(f"Error loading models: {e}", exc_info=True)
        return None


def display_sidebar(trainer: Optional[ModelTrainer]) -> Dict[str, Any]:
    """
    Display sidebar with configuration options.


    Args:
        trainer: ModelTrainer instance or None

    Returns:
        Dictionary with configuration settings
    """
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Model status
        st.subheader("État des modèles")
        if trainer and trainer.vectorizers:
            st.success(f"✅ {len(trainer.vectorizers)} modèle(s) chargé(s)")

            # Show loaded models
            with st.expander("Détails des modèles"):
                for target in trainer.vectorizers.keys():
                    st.text(f"• {target}")
        else:
            st.error("❌ Aucun modèle chargé")
            st.info("Veuillez entraîner les modèles avec train_models.py")

        st.divider()

        # Settings
        st.subheader("Paramètres")
        show_confidence = st.checkbox(
            "Afficher les scores de confiance", value=True)
        show_details = st.checkbox(
            "Afficher les détails techniques", value=False)

        st.divider()

        # About
        st.subheader("À propos")
        st.markdown("""
        **SAV Copilot** v1.0
        
        Système d'aide à la décision pour le service après-vente.
        
        Développé pour le hackathon Atlantem/HERIGE.
        """)

        return {
            "show_confidence": show_confidence,
            "show_details": show_details
        }


def load_real_reclamations() -> Optional[pd.DataFrame]:
    """
    Load real reclamations from training data.

    Returns:
        DataFrame with reclamations or None if loading fails
    """
    try:
        data_loader = DataLoader()
        excel_path = os.path.join(TRAINING_DATA_PATH, TRAINING_EXCEL_FILE)
        df = data_loader.load_training_data(excel_path)
        return df
    except Exception as e:
        logger.error(f"Error loading reclamations: {e}", exc_info=True)
        return None


def get_reclamation_input() -> Optional[Dict[str, Any]]:
    """
    Display input section for reclamation data.


    Returns:
        Dictionary with reclamation data, or None if incomplete
    """
    st.header("📝 Nouvelle Réclamation")

    # Input method selection
    input_method = st.radio(
        "Méthode de saisie",
        ["Saisie manuelle", "Exemples prédéfinis", "Réclamations réelles"],
        horizontal=True
    )

    reclamation = {}

    if input_method == "Saisie manuelle":
        # Manual input
        col1, col2 = st.columns(2)

        with col1:
            reference = st.text_input(
                "Référence (optionnel)",
                placeholder="R20260323002#SAVF-47517-260001"
            )
            if reference:
                reclamation['reference'] = reference

        with col2:
            order_number = st.text_input(
                "Numéro de commande (optionnel)",
                placeholder="CMD-2026-12345"
            )
            if order_number:
                reclamation['order_number'] = order_number

        # Complaint description (required)
        description = st.text_area(
            "Description de la réclamation *",
            placeholder="Décrivez le problème rencontré par le client...",
            height=150,
            help="Saisissez la description du problème. Ce champ est obligatoire."
        )

        # Product info (optional)
        product_info = st.text_input(
            "Informations produit (optionnel)",
            placeholder="Portail coulissant, modèle XYZ"
        )
        if product_info:
            reclamation['product_info'] = product_info

        # File uploader for attachments
        uploaded_files = st.file_uploader(
            "Pièces jointes",
            accept_multiple_files=True,
            type=['pdf', 'jpg', 'jpeg', 'png'],
            help="Téléchargez des photos ou documents relatifs à la réclamation"
        )

        # Process attachments
        attachments = []
        if uploaded_files:
            for file in uploaded_files:
                attachments.append(file.name)
            st.info(f"📎 {len(attachments)} fichier(s) téléchargé(s)")

        reclamation['attachments'] = attachments

        # Validate required fields
        if description:
            reclamation['description'] = description
            return reclamation
        else:
            if st.button("Analyser", type="primary", disabled=True):
                pass
            st.warning("⚠️ La description est obligatoire")
            return None

    elif input_method == "Exemples prédéfinis":
        # Example selection
        examples = {
            "Exemple 1: Défaut de fabrication": {
                "reference": "R20260323001",
                "description": "Le portail coulissant présente des traces de rouille après seulement 3 mois d'installation. Les soudures semblent défectueuses.",
                "product_info": "Portail coulissant acier",
                "attachments": ["photo_rouille_1.jpg", "photo_soudure.jpg"]
            },
            "Exemple 2: Problème d'installation": {
                "reference": "R20260323002",
                "description": "Le portail ne ferme pas correctement, il y a un espace de 5cm en bas.",
                "product_info": "Portail battant aluminium",
                "attachments": ["photo_espace.jpg"]
            },
            "Exemple 3: Usure normale": {
                "reference": "R20260323003",
                "description": "Après 8 ans d'utilisation, la peinture du portail est décolorée et s'écaille par endroits.",
                "product_info": "Portail acier peint",
                "attachments": []
            },
            "Exemple 4: Environnement agressif": {
                "reference": "R20260323004",
                "description": "Nous habitons en bord de mer et le portail montre des signes de corrosion importante.",
                "product_info": "Portail acier galvanisé",
                "attachments": ["photo_corrosion.jpg"]
            }
        }

        selected_example = st.selectbox(
            "Choisissez un exemple",
            options=list(examples.keys())
        )

        if selected_example:
            example_data = examples[selected_example]

            # Display example details
            st.text_input(
                "Référence", value=example_data['reference'], disabled=True)
            st.text_area(
                "Description", value=example_data['description'], height=100, disabled=True)
            st.text_input("Informations produit",
                          value=example_data['product_info'], disabled=True)

            if example_data['attachments']:
                st.info(
                    f"📎 {len(example_data['attachments'])} pièce(s) jointe(s): {', '.join(example_data['attachments'])}")
            else:
                st.info("📎 Aucune pièce jointe")

            return example_data

    else:  # Réclamations réelles
        # Load real reclamations
        if 'real_reclamations' not in st.session_state:
            with st.spinner("Chargement des réclamations réelles..."):
                st.session_state.real_reclamations = load_real_reclamations()

        df = st.session_state.real_reclamations

        if df is None or df.empty:
            st.error("❌ Impossible de charger les réclamations réelles")
            st.info(
                "Vérifiez que les données d'entraînement sont disponibles dans le dossier Data/")
            return None

        # Complexity filter
        st.subheader("🎯 Filtrer par complexité")

        col_filter1, col_filter2 = st.columns(2)

        with col_filter1:
            complexity_filter = st.selectbox(
                "Niveau de complexité",
                ["Toutes", "⚡ Rapide (< 15 min)",
                 "📋 Standard (15-45 min)", "🔬 Complexe (> 45 min)"],
                help="Filtrez les réclamations selon leur complexité estimée"
            )

        with col_filter2:
            sort_order = st.selectbox(
                "Ordre de tri",
                ["Plus rapides d'abord", "Plus complexes d'abord", "Ordre original"],
                help="Triez les réclamations selon votre priorité"
            )

        # Calculate complexity for each reclamation (simplified estimation)
        if 'reclamation_complexity' not in st.session_state:
            with st.spinner("Calcul de la complexité..."):
                complexities = []
                for idx, row in df.iterrows():
                    # Find description column
                    desc_col = None
                    for col in df.columns:
                        if 'description' in col.lower() or 'desc' in col.lower():
                            desc_col = col
                            break

                    if desc_col and pd.notna(row[desc_col]):
                        desc = str(row[desc_col])
                        # Simple complexity estimation based on description length and keywords
                        score = 0

                        # Length factor
                        if len(desc) < 50:
                            score += 0
                        elif len(desc) < 150:
                            score += 1
                        else:
                            score += 2

                        # Keyword complexity
                        complex_keywords = [
                            'défaut', 'cassé', 'rouille', 'corrosion', 'garantie', 'installation']
                        score += sum(1 for kw in complex_keywords if kw.lower()
                                     in desc.lower())

                        # Classify
                        if score <= 2:
                            level = 'rapide'
                            time_est = '10-15 min'
                        elif score <= 4:
                            level = 'standard'
                            time_est = '20-45 min'
                        else:
                            level = 'complexe'
                            time_est = '45-90 min'

                        complexities.append(
                            {'level': level, 'score': score, 'time': time_est})
                    else:
                        complexities.append(
                            {'level': 'standard', 'score': 3, 'time': '20-45 min'})

                st.session_state.reclamation_complexity = complexities

        # Apply filter
        filtered_indices = []
        for idx, complexity in enumerate(st.session_state.reclamation_complexity):
            if complexity_filter == "Toutes":
                filtered_indices.append(idx)
            elif "Rapide" in complexity_filter and complexity['level'] == 'rapide':
                filtered_indices.append(idx)
            elif "Standard" in complexity_filter and complexity['level'] == 'standard':
                filtered_indices.append(idx)
            elif "Complexe" in complexity_filter and complexity['level'] == 'complexe':
                filtered_indices.append(idx)

        # Apply sorting
        if sort_order == "Plus rapides d'abord":
            filtered_indices.sort(
                key=lambda i: st.session_state.reclamation_complexity[i]['score'])
        elif sort_order == "Plus complexes d'abord":
            filtered_indices.sort(
                key=lambda i: st.session_state.reclamation_complexity[i]['score'], reverse=True)

        # Display filtered count
        st.info(
            f"📊 {len(filtered_indices)} réclamation(s) disponible(s) (sur {len(df)} total)")

        # Create selection options
        # Try to find reference column
        ref_col = None
        for col in df.columns:
            if 'ref' in col.lower() or 'reference' in col.lower():
                ref_col = col
                break

        # Create display options with complexity indicators
        complexity_icons = {
            'rapide': '⚡',
            'standard': '📋',
            'complexe': '🔬'
        }

        if ref_col and ref_col in df.columns:
            options = []
            for idx in filtered_indices:
                row = df.loc[idx]
                complexity = st.session_state.reclamation_complexity[idx]
                icon = complexity_icons.get(complexity['level'], '📋')
                time = complexity['time']

                if pd.notna(row[ref_col]):
                    options.append(f"{idx} - {icon} {row[ref_col]} ({time})")
                else:
                    options.append(f"{idx} - {icon} Sans référence ({time})")
        else:
            options = []
            for idx in filtered_indices:
                complexity = st.session_state.reclamation_complexity[idx]
                icon = complexity_icons.get(complexity['level'], '📋')
                time = complexity['time']
                options.append(f"Réclamation {idx} {icon} ({time})")

        # Selection dropdown
        if not options:
            st.warning(
                "⚠️ Aucune réclamation ne correspond aux filtres sélectionnés")
            return None

        selected_option = st.selectbox(
            "Sélectionnez une réclamation",
            options=options,
            help="Choisissez une réclamation réelle depuis les données d'entraînement"
        )

        if selected_option:
            # Extract index from selection - handle multiple formats
            if " - " in selected_option:
                # Format: "idx - icon REF (time)" or "idx - icon Sans référence (time)"
                selected_idx = int(selected_option.split(" - ")[0])
            elif "Réclamation " in selected_option:
                # Format: "Réclamation idx icon (time)"
                parts = selected_option.split(" ")
                selected_idx = int(parts[1])
            else:
                st.error("❌ Format d'option non reconnu")
                return None

            selected_row = df.loc[selected_idx]

            # Display complexity badge
            complexity = st.session_state.reclamation_complexity[selected_idx]
            complexity_colors = {
                'rapide': '🟢',
                'standard': '🟡',
                'complexe': '🔴'
            }
            complexity_labels = {
                'rapide': 'Rapide',
                'standard': 'Standard',
                'complexe': 'Complexe'
            }

            col_badge1, col_badge2 = st.columns(2)
            with col_badge1:
                st.metric(
                    label="Complexité estimée",
                    value=f"{complexity_colors[complexity['level']]} {complexity_labels[complexity['level']]}",
                    help="Estimation basée sur l'analyse du contenu"
                )
            with col_badge2:
                st.metric(
                    label="Temps estimé",
                    value=complexity['time'],
                    help="Temps de traitement estimé pour cette réclamation"
                )

            # Find description column
            desc_col = None
            for col in df.columns:
                if 'description' in col.lower() or 'desc' in col.lower():
                    desc_col = col
                    break

            if desc_col is None:
                st.error("❌ Colonne 'description' non trouvée dans les données")
                return None

            description = selected_row[desc_col] if pd.notna(
                selected_row[desc_col]) else ""

            if not description:
                st.warning("⚠️ Cette réclamation n'a pas de description")
                return None

            # Build reclamation dict
            reclamation = {
                "description": str(description),
                "attachments": []
            }

            # Add reference if available
            if ref_col and pd.notna(selected_row[ref_col]):
                reclamation['reference'] = str(selected_row[ref_col])

            # Try to find product info
            for col in df.columns:
                if 'produit' in col.lower() or 'product' in col.lower():
                    if pd.notna(selected_row[col]):
                        reclamation['product_info'] = str(selected_row[col])
                    break

            # Display selected reclamation details
            st.text_input(
                "Référence",
                value=reclamation.get('reference', 'N/A'),
                disabled=True
            )
            st.text_area(
                "Description",
                value=description,
                height=150,
                disabled=True
            )
            if 'product_info' in reclamation:
                st.text_input(
                    "Informations produit",
                    value=reclamation['product_info'],
                    disabled=True
                )

            st.info("📎 Aucune pièce jointe (données d'entraînement)")

            return reclamation

    return None


def display_predictions(predictions: Dict[str, Any], show_confidence: bool):
    """
    Display prediction results with confidence scores.


    Args:
        predictions: Prediction results from pipeline
        show_confidence: Whether to show confidence scores
    """
    st.subheader("🎯 Prédictions")

    # Check if predictions are available
    if not predictions:
        st.warning("Aucune prédiction disponible")
        return

    # Create columns for the four main predictions
    col1, col2 = st.columns(2)

    with col1:
        # Litige type
        litige = predictions.get('litige_type', {})
        if litige.get('available', True):
            st.metric(
                label="Type de litige",
                value=litige.get('prediction', 'N/A'),
                help="Classification du type de litige"
            )
            if show_confidence:
                confidence = litige.get('confidence', 0.0)
                st.progress(confidence, text=f"Confiance: {confidence:.1%}")
        else:
            st.metric(label="Type de litige", value="Non disponible")

        st.divider()

        # Product detail
        product = predictions.get('product_detail', {})
        if product.get('available', True):
            st.metric(
                label="Précision produit",
                value=product.get('prediction', 'N/A'),
                help="Identification du produit concerné"
            )
            if show_confidence:
                confidence = product.get('confidence', 0.0)
                st.progress(confidence, text=f"Confiance: {confidence:.1%}")
        else:
            st.metric(label="Précision produit", value="Non disponible")

    with col2:
        # Responsibility
        responsibility = predictions.get('responsibility', {})
        if responsibility.get('available', True):
            st.metric(
                label="Responsabilité",
                value=responsibility.get('prediction', 'N/A'),
                help="Attribution de la responsabilité"
            )
            if show_confidence:
                confidence = responsibility.get('confidence', 0.0)
                st.progress(confidence, text=f"Confiance: {confidence:.1%}")
        else:
            st.metric(label="Responsabilité", value="Non disponible")

        st.divider()

        # Solution (main prediction)
        solution = predictions.get('solution', {})
        if solution.get('available', True):
            st.metric(
                label="Solution recommandée",
                value=solution.get('prediction', 'N/A'),
                help="Solution principale recommandée"
            )
            if show_confidence:
                confidence = solution.get('confidence', 0.0)
                st.progress(confidence, text=f"Confiance: {confidence:.1%}")
        else:
            st.metric(label="Solution recommandée", value="Non disponible")

    # Display top 3 solution candidates
    st.divider()
    solution = predictions.get('solution', {})
    top_3 = solution.get('top_3', [])

    if top_3 and len(top_3) > 0:
        st.markdown("**Top 3 des solutions candidates:**")

        for i, candidate in enumerate(top_3[:3], 1):
            label = candidate.get('label', 'N/A')
            confidence = candidate.get('confidence', 0.0)

            col_label, col_conf = st.columns([3, 1])
            with col_label:
                st.text(f"{i}. {label}")
            with col_conf:
                if show_confidence:
                    st.text(f"{confidence:.1%}")


def display_quality(quality: Dict[str, Any]):
    """
    Display quality assessment results.


    Args:
        quality: Quality assessment from pipeline
    """
    st.subheader("✅ Évaluation de la qualité")

    status = quality.get('status', 'unknown')
    issues = quality.get('issues', [])
    details = quality.get('details', {})

    # Status indicator
    status_colors = {
        'usable': '🟢',
        'poor': '🟡',
        'unusable': '🔴'
    }
    status_labels = {
        'usable': 'Exploitable',
        'poor': 'Qualité moyenne',
        'unusable': 'Non exploitable'
    }

    status_icon = status_colors.get(status, '⚪')
    status_label = status_labels.get(status, status)

    st.markdown(f"**Statut:** {status_icon} {status_label}")

    # Issues
    if issues:
        st.markdown("**Problèmes détectés:**")
        issue_labels = {
            'too_short': '📏 Description trop courte',
            'missing_attachments': '📎 Pièces jointes manquantes',
            'too_vague': '💭 Description trop vague'
        }
        for issue in issues:
            issue_label = issue_labels.get(issue, issue)
            st.markdown(f"- {issue_label}")
    else:
        st.success("Aucun problème détecté")

    # Details in expander
    with st.expander("Détails techniques"):
        st.json(details)


def display_warranty(warranty: Dict[str, Any]):
    """
    Display warranty evaluation results.


    Args:
        warranty: Warranty evaluation from pipeline
    """
    st.subheader("🛡️ Évaluation de la garantie")

    status = warranty.get('status', 'unknown')
    reasons = warranty.get('reasons', [])
    disclaimer = warranty.get('disclaimer', '')

    # Status indicator
    status_colors = {
        'hors_garantie_probable': '🔴',
        'incertaine': '🟡',
        'eligible_probable': '🟢'
    }
    status_labels = {
        'hors_garantie_probable': 'Hors garantie probable',
        'incertaine': 'Incertaine',
        'eligible_probable': 'Éligible probable'
    }

    status_icon = status_colors.get(status, '⚪')
    status_label = status_labels.get(status, status)

    st.markdown(f"**Statut:** {status_icon} {status_label}")

    # Reasons
    if reasons:
        st.markdown("**Raisons:**")
        for reason in reasons:
            st.markdown(f"- {reason}")

    # Disclaimer
    if disclaimer:
        st.info(f"ℹ️ {disclaimer}")


def display_complexity(complexity: Dict[str, Any], show_details: bool):
    """
    Display complexity score and priority.


    Args:
        complexity: Complexity score from pipeline
        show_details: Whether to show detailed breakdown
    """
    st.subheader("📊 Complexité et priorité")

    score = complexity.get('score', 0)
    level = complexity.get('level', 'unknown')
    priority = complexity.get('priority', 'unknown')
    breakdown = complexity.get('breakdown', {})

    # Display metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Score de complexité",
            value=score,
            help="Score calculé basé sur plusieurs facteurs"
        )

    with col2:
        level_labels = {
            'rapide': '⚡ Rapide',
            'standard': '📋 Standard',
            'complexe': '🔬 Complexe'
        }
        level_label = level_labels.get(level, level)
        st.metric(
            label="Niveau",
            value=level_label,
            help="Niveau de complexité du dossier"
        )

    with col3:
        priority_labels = {
            'quick_win': '🎯 Quick Win',
            'standard_review': '📝 Revue Standard',
            'expert_review': '👨‍🔬 Revue Expert'
        }
        priority_label = priority_labels.get(priority, priority)
        st.metric(
            label="Priorité",
            value=priority_label,
            help="Priorité de traitement recommandée"
        )

    # Breakdown details
    if show_details and breakdown:
        with st.expander("Détail du calcul"):
            for key, value in breakdown.items():
                st.text(f"{key}: {value:+d}")


def display_message(message: Optional[str]):
    """
    Display generated customer message.


    Args:
        message: Generated message from pipeline
    """
    st.subheader("💬 Message client suggéré")

    if message:
        st.text_area(
            label="Message",
            value=message,
            height=200,
            help="Message prêt à envoyer au client (peut être modifié)"
        )

        # Copy button hint
        st.caption(
            "💡 Vous pouvez copier et modifier ce message avant de l'envoyer")
    else:
        st.info("Aucun message automatique généré. Revue manuelle recommandée.")


def display_results(result: Any, config: Dict[str, Any]):
    """
    Display complete analysis results.


    Args:
        result: AnalysisResult from pipeline
        config: Configuration settings from sidebar
    """
    st.header("📋 Résultats de l'analyse")

    # Processing time
    processing_time = result.processing_time
    st.caption(f"⏱️ Temps de traitement: {processing_time:.3f} secondes")

    st.divider()

    # Display each section
    display_predictions(result.predictions, config['show_confidence'])

    st.divider()

    display_quality(result.quality)

    st.divider()

    display_warranty(result.warranty)

    st.divider()

    display_complexity(result.complexity, config['show_details'])

    st.divider()

    display_message(result.message)

    # Raw data in expander (for debugging)
    if config['show_details']:
        with st.expander("🔍 Données brutes (debug)"):
            st.json(result.to_dict())


def main():
    """
    Main application entry point.

    """
    # Page configuration
    st.set_page_config(
        page_title="SAV Copilot",
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Title
    st.title("🔧 SAV Copilot - Aide à la Décision")
    st.markdown("*Système d'analyse automatique des réclamations clients*")

    st.divider()

    # Initialize models on startup
    if 'trainer' not in st.session_state:
        with st.spinner("Chargement des modèles..."):
            st.session_state.trainer = initialize_models()

    trainer = st.session_state.trainer

    # Display sidebar and get configuration
    config = display_sidebar(trainer)

    # Get reclamation input
    reclamation = get_reclamation_input()

    # Analysis button
    if reclamation:
        if st.button("🔍 Analyser", type="primary", use_container_width=True):
            if not trainer:
                st.error("❌ Impossible d'analyser: aucun modèle chargé")
                st.info(
                    "Veuillez entraîner les modèles avec: `python train_models.py`")
            else:
                # Run analysis with spinner
                with st.spinner("Analyse en cours..."):
                    try:
                        result = analyze_reclamation(
                            reclamation, trainer=trainer)
                        st.session_state.result = result
                        st.success("✅ Analyse terminée!")
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
                        logger.error(f"Analysis error: {e}", exc_info=True)

    # Display results if available
    if 'result' in st.session_state:
        st.divider()
        display_results(st.session_state.result, config)


if __name__ == "__main__":
    main()
