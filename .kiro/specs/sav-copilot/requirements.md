# Requirements Document - SAV Copilot

## Introduction

Le SAV Copilot est un système d'aide à la décision pour les opérateurs du service après-vente d'Atlantem / HERIGE. Le système analyse automatiquement les réclamations clients et propose une préqualification complète incluant le type de litige, la responsabilité, le produit concerné, les solutions recommandées avec scores de confiance, l'éligibilité garantie probable, la complexité de traitement, et des messages clients prêts à l'emploi.

L'objectif est d'accélérer le traitement des dossiers SAV en identifiant rapidement les cas simples (quick wins), en détectant les dossiers incomplets nécessitant des informations complémentaires, et en orientant les cas complexes vers une revue experte.

## Glossary

- **SAV_Copilot**: Le système d'aide à la décision pour le service après-vente
- **Reclamation**: Une réclamation client contenant numéro de commande, description du problème, informations produit et pièces jointes
- **Classifier**: Un modèle de classification machine learning entraîné sur les données historiques
- **Input_Quality_Analyzer**: Le composant qui évalue la qualité et l'exploitabilité des données d'entrée
- **Warranty_Engine**: Le moteur de règles métier qui évalue l'éligibilité garantie probable
- **Complexity_Scorer**: Le composant qui calcule un score de complexité de traitement
- **Message_Generator**: Le composant qui génère des messages clients contextuels
- **RAG_System**: Le système de récupération documentaire léger pour enrichir les décisions
- **Training_Dataset**: Les données Data_WithSolution_Week13 utilisées pour l'entraînement
- **Warranty_Documentation**: La documentation de garantie utilisée pour les règles métier
- **GeneralReferencing**: Le référentiel métier des catégories et classifications autorisées
- **Linking_Table**: La table de liaison entre réclamations et pièces jointes
- **Operator**: Un opérateur du service après-vente utilisant le système
- **Streamlit_UI**: L'interface utilisateur de démonstration

## Requirements

### Requirement 1: Data Loading and Integration

**User Story:** As an Operator, I want the system to load and integrate all available data sources, so that I can analyze complete customer complaints with all relevant context.

#### Acceptance Criteria

1. WHEN the system starts, THE SAV_Copilot SHALL load the Training_Dataset from Data_WithSolution_Week13
2. WHEN the system starts, THE SAV_Copilot SHALL load the Warranty_Documentation files
3. WHEN the system starts, THE SAV_Copilot SHALL load the GeneralReferencing metadata
4. WHEN the Linking_Table exists, THE SAV_Copilot SHALL merge attachments with their corresponding Reclamation records
5. THE SAV_Copilot SHALL create a unified dataset where each Reclamation has all associated metadata and attachment references
6. IF a data file is missing or corrupted, THEN THE SAV_Copilot SHALL log a descriptive error and continue with available data

### Requirement 2: Data Preprocessing and Normalization

**User Story:** As a developer, I want the system to clean and normalize input data, so that the classifiers receive consistent, high-quality features.

#### Acceptance Criteria

1. THE SAV_Copilot SHALL normalize text fields by removing extra whitespace and standardizing encoding
2. THE SAV_Copilot SHALL handle missing values in non-critical fields without failing
3. THE SAV_Copilot SHALL extract text features suitable for TF-IDF vectorization
4. THE SAV_Copilot SHALL preserve all original data fields for traceability
5. WHEN column names vary from expected schema, THE SAV_Copilot SHALL attempt flexible column matching using common patterns

### Requirement 3: Classification Model Training

**User Story:** As a developer, I want to train separate classifiers for each prediction target, so that the system can predict litige type, responsibility, product detail, and solution independently.

#### Acceptance Criteria

1. THE SAV_Copilot SHALL train a Classifier for litige type using TF-IDF and LogisticRegression
2. THE SAV_Copilot SHALL train a Classifier for responsibility using TF-IDF and LogisticRegression
3. THE SAV_Copilot SHALL train a Classifier for product detail using TF-IDF and LogisticRegression
4. THE SAV_Copilot SHALL train a Classifier for solution using TF-IDF and LogisticRegression
5. THE SAV_Copilot SHALL persist trained models to disk for reuse
6. WHEN training data is insufficient for a target, THEN THE SAV_Copilot SHALL log a warning and create a fallback model

### Requirement 4: Prediction with Confidence Scoring

**User Story:** As an Operator, I want the system to predict classification targets with confidence scores, so that I can assess the reliability of recommendations.

#### Acceptance Criteria

1. WHEN a Reclamation is analyzed, THE SAV_Copilot SHALL predict the litige type with a confidence score
2. WHEN a Reclamation is analyzed, THE SAV_Copilot SHALL predict the responsibility with a confidence score
3. WHEN a Reclamation is analyzed, THE SAV_Copilot SHALL predict the product detail with a confidence score
4. WHEN a Reclamation is analyzed, THE SAV_Copilot SHALL predict the solution with a confidence score
5. THE SAV_Copilot SHALL provide the top 3 candidate solutions with their respective confidence scores
6. THE SAV_Copilot SHALL calculate confidence scores as probability estimates from the Classifier models

### Requirement 5: Input Quality Assessment

**User Story:** As an Operator, I want the system to detect poor quality or incomplete inputs, so that I can request additional information from customers when needed.

#### Acceptance Criteria

1. WHEN a Reclamation description is shorter than 20 characters, THE Input_Quality_Analyzer SHALL flag it as too_short
2. WHEN a Reclamation has no attached files, THE Input_Quality_Analyzer SHALL flag it as missing_attachments
3. WHEN a Reclamation description contains fewer than 5 meaningful words, THE Input_Quality_Analyzer SHALL flag it as too_vague
4. THE Input_Quality_Analyzer SHALL produce an overall usability status of usable, poor, or unusable
5. THE Input_Quality_Analyzer SHALL provide a list of specific quality issues detected

### Requirement 6: Warranty Eligibility Assessment

**User Story:** As an Operator, I want the system to assess probable warranty eligibility based on business rules, so that I can quickly identify cases likely outside warranty coverage.

#### Acceptance Criteria

1. WHEN a Reclamation mentions normal wear or aging, THE Warranty_Engine SHALL flag it as hors_garantie_probable
2. WHEN a Reclamation mentions poor maintenance or non-compliant installation, THE Warranty_Engine SHALL flag it as hors_garantie_probable
3. WHEN a Reclamation mentions shock, scratch, or handling damage, THE Warranty_Engine SHALL flag it as hors_garantie_probable
4. WHEN a Reclamation mentions aggressive environment, seaside, or corrosion, THE Warranty_Engine SHALL flag it as hors_garantie_probable
5. WHEN a Reclamation mentions hardware, accessories, motors, or electronics, THE Warranty_Engine SHALL flag it as hors_garantie_probable
6. WHEN warranty eligibility cannot be determined, THE Warranty_Engine SHALL return status incertaine
7. THE Warranty_Engine SHALL provide a list of reasons explaining the warranty status
8. THE Warranty_Engine SHALL never claim to make a final legal warranty decision

### Requirement 7: Complexity Scoring and Prioritization

**User Story:** As an Operator, I want the system to calculate a complexity score for each case, so that I can prioritize simple cases for quick resolution.

#### Acceptance Criteria

1. THE Complexity_Scorer SHALL add 2 points when important data is missing
2. THE Complexity_Scorer SHALL add 1 point when multiple attachments are present
3. THE Complexity_Scorer SHALL add 2 points when warranty status is incertaine
4. THE Complexity_Scorer SHALL add 1 point when solution confidence is below 0.5
5. THE Complexity_Scorer SHALL add 1 point when responsibility confidence is below 0.5
6. THE Complexity_Scorer SHALL subtract 1 point when solution confidence exceeds 0.8
7. THE Complexity_Scorer SHALL subtract 1 point when the case is very clear
8. THE Complexity_Scorer SHALL add 1 point when contradictory signals are detected
9. THE Complexity_Scorer SHALL add 1 point when input quality is poor
10. WHEN the complexity score is 1 or less, THE Complexity_Scorer SHALL assign priority quick_win and level rapide
11. WHEN the complexity score is between 2 and 3, THE Complexity_Scorer SHALL assign priority standard_review and level standard
12. WHEN the complexity score is 4 or more, THE Complexity_Scorer SHALL assign priority expert_review and level complexe

### Requirement 8: Customer Message Generation

**User Story:** As an Operator, I want the system to generate contextual customer messages, so that I can quickly communicate with customers in common scenarios.

#### Acceptance Criteria

1. WHEN input quality is poor or unusable, THE Message_Generator SHALL create a need_more_info message requesting clarification or better photos
2. WHEN warranty status is hors_garantie_probable or non_applicable, THE Message_Generator SHALL create a warranty_not_applicable message informing the customer prudently
3. WHEN complexity level is rapide and input quality is usable and solution confidence is high, THE Message_Generator SHALL create a reassurance_fast_case message to reassure the customer
4. THE Message_Generator SHALL produce messages in French appropriate for customer communication
5. THE Message_Generator SHALL avoid making definitive legal warranty decisions in messages

### Requirement 9: Optional RAG Document Retrieval

**User Story:** As a developer, I want to optionally retrieve relevant warranty documentation passages, so that I can enrich decision justifications when needed.

#### Acceptance Criteria

1. WHERE RAG_System is enabled, THE SAV_Copilot SHALL retrieve relevant passages from Warranty_Documentation based on Reclamation text
2. WHERE RAG_System is enabled, THE SAV_Copilot SHALL retrieve relevant category definitions from GeneralReferencing
3. WHERE RAG_System is enabled, THE SAV_Copilot SHALL include retrieved passages in the analysis output
4. THE SAV_Copilot SHALL function correctly when RAG_System is disabled

### Requirement 10: Streamlit User Interface

**User Story:** As an Operator, I want a simple web interface to analyze complaints, so that I can demonstrate the system's capabilities during the hackathon.

#### Acceptance Criteria

1. THE Streamlit_UI SHALL allow uploading or selecting a Reclamation for analysis
2. THE Streamlit_UI SHALL display predicted litige type, responsibility, product detail, and solution
3. THE Streamlit_UI SHALL display the top 3 solution candidates with confidence scores
4. THE Streamlit_UI SHALL display warranty status with reasons
5. THE Streamlit_UI SHALL display complexity score, level, and priority
6. THE Streamlit_UI SHALL display input quality assessment
7. THE Streamlit_UI SHALL display the generated customer message when applicable
8. THE Streamlit_UI SHALL present results in a clear, professional layout suitable for demonstration

### Requirement 11: Pipeline Execution and Error Handling

**User Story:** As a developer, I want the system to execute the complete analysis pipeline robustly, so that the demo runs reliably during the hackathon.

#### Acceptance Criteria

1. THE SAV_Copilot SHALL execute the complete pipeline from data loading through prediction to message generation
2. WHEN an error occurs in a non-critical component, THE SAV_Copilot SHALL continue execution and log the error
3. WHEN an error occurs in a critical component, THE SAV_Copilot SHALL fail gracefully with a descriptive error message
4. THE SAV_Copilot SHALL complete analysis of a single Reclamation in under 2 seconds on typical hardware

### Requirement 12: Model Persistence and Reuse

**User Story:** As a developer, I want trained models to be saved and reloaded, so that I don't need to retrain for every demo run.

#### Acceptance Criteria

1. WHEN models are trained, THE SAV_Copilot SHALL save all Classifier models to the models directory
2. WHEN the system starts, THE SAV_Copilot SHALL load existing models if available
3. WHEN existing models are not found, THE SAV_Copilot SHALL train new models from Training_Dataset
4. THE SAV_Copilot SHALL save model metadata including training date and performance metrics

### Requirement 13: Modular Code Architecture

**User Story:** As a developer, I want a clean, modular code structure, so that the code is easy to understand, modify, and present during the hackathon.

#### Acceptance Criteria

1. THE SAV_Copilot SHALL organize code into separate modules for data loading, preprocessing, training, prediction, warranty rules, complexity scoring, and message generation
2. THE SAV_Copilot SHALL use clear function names with docstrings
3. THE SAV_Copilot SHALL include inline comments for complex logic
4. THE SAV_Copilot SHALL follow Python best practices for readability
5. THE SAV_Copilot SHALL provide a requirements.txt file with minimal necessary dependencies

### Requirement 14: Fallback Handling for Missing Data

**User Story:** As a developer, I want the system to handle missing or unexpected data gracefully, so that the demo doesn't crash on edge cases.

#### Acceptance Criteria

1. WHEN expected columns are missing from input data, THE SAV_Copilot SHALL use fallback column name matching
2. WHEN a prediction target is unavailable, THE SAV_Copilot SHALL return a default value with zero confidence
3. WHEN attachments cannot be linked, THE SAV_Copilot SHALL proceed with text-only analysis
4. THE SAV_Copilot SHALL never crash due to missing optional data fields
