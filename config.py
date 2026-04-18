"""
Configuration constants and paths for SAV Copilot.
"""
import os

# ============================================================================
# Path Configuration
# ============================================================================

# Base directories
DATA_DIR = os.getenv("SAV_DATA_DIR", "Data")
MODELS_DIR = os.getenv("SAV_MODELS_DIR", "models")

# Training data paths
TRAINING_DATA_PATH = os.path.join(
    DATA_DIR,
    "Data_WithSolution_Week13",
    "Data_WithSolution_Week13"
)
TRAINING_EXCEL_FILE = "Reclamations_Digit_20260323-20260327.xlsx"
LINKING_CSV_FILE = "Lien_Reclamation_PJ_20260323-20260327.CSV"

# Warranty documentation paths
WARRANTY_DOCS_PATH = os.path.join(
    DATA_DIR,
    "Warranty_Documentation",
    "Warranty_Documentation"
)
GENERAL_REFERENCING_FILE = "GeneralReferencing.xlsx"

# ============================================================================
# Model Configuration
# ============================================================================

# TF-IDF Vectorizer parameters
TFIDF_MAX_FEATURES = 5000
TFIDF_NGRAM_RANGE = (1, 2)
TFIDF_MIN_DF = 2
TFIDF_SUBLINEAR_TF = True

# Logistic Regression parameters
LOGREG_MAX_ITER = 1000
LOGREG_SOLVER = "lbfgs"
LOGREG_MULTI_CLASS = "ovr"
LOGREG_RANDOM_STATE = 42

# Target columns for classification
TARGET_COLUMNS = {
    "litige": "Type de litige",
    "responsibility": "Responsabilité",
    "product": "Précision produit",
    "solution": "Solution"
}

# Text column for training
TEXT_COLUMN = "description"

# ============================================================================
# Quality Assessment Configuration
# ============================================================================

# Input quality thresholds
MIN_DESCRIPTION_LENGTH = 20
MIN_MEANINGFUL_WORDS = 5

# Quality status levels
QUALITY_USABLE = "usable"
QUALITY_POOR = "poor"
QUALITY_UNUSABLE = "unusable"

# ============================================================================
# Complexity Scoring Configuration
# ============================================================================

# Complexity thresholds
QUICK_WIN_THRESHOLD = 1
EXPERT_REVIEW_THRESHOLD = 4

# Priority levels
PRIORITY_QUICK_WIN = "quick_win"
PRIORITY_STANDARD = "standard_review"
PRIORITY_EXPERT = "expert_review"

# Complexity levels (French)
LEVEL_RAPIDE = "rapide"
LEVEL_STANDARD = "standard"
LEVEL_COMPLEXE = "complexe"

# ============================================================================
# Warranty Configuration
# ============================================================================

# Warranty status values
WARRANTY_HORS_GARANTIE = "hors_garantie_probable"
WARRANTY_INCERTAINE = "incertaine"
WARRANTY_ELIGIBLE = "eligible_probable"

# Warranty disclaimer
WARRANTY_DISCLAIMER = (
    "Cette évaluation est indicative et ne constitue pas une décision légale."
)

# ============================================================================
# Performance Configuration
# ============================================================================

# Maximum processing time target (seconds)
MAX_PROCESSING_TIME = 2.0

# ============================================================================
# RAG Configuration
# ============================================================================

# RAG system settings
RAG_ENABLED = False
RAG_TOP_K = 3

# ============================================================================
# Logging Configuration
# ============================================================================

# Log file path
LOG_FILE = "sav_copilot.log"
LOG_LEVEL = "INFO"
