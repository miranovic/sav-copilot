# Implementation Plan: SAV Copilot

## Overview

This implementation plan breaks down the SAV Copilot feature into discrete coding tasks suitable for a hackathon MVP. The approach follows a bottom-up strategy: build core data and ML infrastructure first, then add business logic layers, and finally wire everything together in the UI. Each task builds incrementally on previous work, with checkpoints to validate progress.

The implementation uses Python with scikit-learn for ML, pandas for data processing, and Streamlit for the demo UI. Testing tasks are marked as optional to allow faster MVP delivery while maintaining code quality options.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directory structure: `sav_copilot/` package, `models/`, `tests/`
  - Create `requirements.txt` with core dependencies (streamlit, scikit-learn, pandas, numpy, joblib, PyPDF2, openpyxl)
  - Create `config.py` with paths and configuration constants
  - Create package `__init__.py` files
  - Create `.gitignore` to exclude `models/` and data directories
  - _Requirements: 13.5_

- [ ] 2. Implement data loading module
  - [x] 2.1 Create `data_loader.py` with DataLoader class
    - Implement `load_training_data()` to read Excel file from Data_WithSolution_Week13
    - Implement `load_linking_table()` to read CSV linking reclamations to attachments
    - Implement `load_general_referencing()` to read metadata Excel
    - Implement `merge_attachments()` to join linking table with reclamations
    - Add error handling for missing files with descriptive logging
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 14.1, 14.3_
  
  - [ ]* 2.2 Write unit tests for data loader
    - Test flexible column matching with various schemas
    - Test handling of missing files
    - Test CSV and Excel parsing
    - _Requirements: 1.6, 14.1_

- [ ] 3. Implement preprocessing module
  - [x] 3.1 Create `preprocessor.py` with Preprocessor class
    - Implement `normalize_text()` for whitespace and encoding cleanup
    - Implement `handle_missing_values()` for non-critical fields
    - Implement `extract_features()` to prepare text for TF-IDF
    - Implement `flexible_column_match()` for schema variations
    - Preserve original data in separate columns for traceability
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 14.1_
  
  - [ ]* 3.2 Write unit tests for preprocessor
    - Test text normalization with various inputs
    - Test missing value handling
    - Test feature extraction
    - _Requirements: 2.1, 2.2_

- [x] 4. Checkpoint - Verify data pipeline
  - Ensure data loading and preprocessing work end-to-end with sample data, ask the user if questions arise.

- [ ] 5. Implement model training module
  - [x] 5.1 Create `trainer.py` with ModelTrainer class
    - Implement `__init__()` to initialize models directory and storage dictionaries
    - Implement `train_classifier()` to train TF-IDF + LogisticRegression for one target
    - Configure TfidfVectorizer with max_features=5000, ngram_range=(1,2), min_df=2
    - Configure LogisticRegression with max_iter=1000, multi_class='ovr', solver='lbfgs'
    - Implement `train_all()` to train classifiers for litige, responsibility, product, solution
    - Implement `save_models()` to persist models with joblib
    - Implement `load_models()` to reload existing models
    - Add logging for training progress and warnings for insufficient data
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 12.1, 12.2, 12.3, 12.4_
  
  - [ ]* 5.2 Write unit tests for model trainer
    - Test training on small dataset subset
    - Test model save and load cycle
    - Test handling of insufficient training data
    - _Requirements: 3.6, 12.1, 12.2, 12.3_

- [ ] 6. Implement prediction module
  - [x] 6.1 Create `predictor.py` with Predictor class
    - Implement `predict_single()` to predict one target with confidence score
    - Implement `predict_top_k()` to get top K predictions with scores
    - Implement `predict_all()` to predict all four targets (litige, responsibility, product, solution)
    - Return predictions in structured format with confidence scores
    - Handle cases where models are unavailable with fallback values
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 14.2_
  
  - [ ]* 6.2 Write unit tests for predictor
    - Test prediction with various text inputs
    - Test top-K prediction logic
    - Test fallback handling for missing models
    - _Requirements: 4.6, 14.2_

- [x] 7. Checkpoint - Verify ML pipeline
  - Ensure model training and prediction work end-to-end, ask the user if questions arise.

- [ ] 8. Implement input quality analyzer
  - [x] 8.1 Create `quality_analyzer.py` with InputQualityAnalyzer class
    - Implement `analyze()` to assess overall input quality
    - Implement `check_description_length()` to flag descriptions < 20 characters
    - Implement `check_attachments()` to flag missing attachments
    - Implement `check_vagueness()` to flag descriptions with < 5 meaningful words
    - Return quality status (usable/poor/unusable) and list of specific issues
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 8.2 Write unit tests for quality analyzer
    - Test length checks with various inputs
    - Test vagueness detection with stop words
    - Test status assignment logic
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 9. Implement warranty engine
  - [x] 9.1 Create `warranty_engine.py` with WarrantyEngine class
    - Implement `__init__()` to load exclusion patterns for 5 categories
    - Define patterns for normal wear/aging (usure normale, vieillissement, décoloration)
    - Define patterns for poor maintenance (mauvais entretien, installation non conforme)
    - Define patterns for handling damage (choc, rayure, dommage de manipulation)
    - Define patterns for aggressive environment (environnement agressif, bord de mer, corrosion)
    - Define patterns for hardware/accessories (quincaillerie, accessoires, moteur, électronique)
    - Implement `evaluate()` to assess warranty eligibility based on text patterns
    - Return status (hors_garantie_probable/incertaine/eligible_probable) with reasons
    - Include disclaimer that assessment is indicative, not a legal decision
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_
  
  - [ ]* 9.2 Write unit tests for warranty engine
    - Test pattern matching for each exclusion category
    - Test status determination logic
    - Test with real complaint examples from training data
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [ ] 10. Implement complexity scorer
  - [x] 10.1 Create `complexity_scorer.py` with ComplexityScorer class
    - Implement `calculate()` to compute overall complexity score
    - Implement `_score_data_quality()` to add points for missing data and poor quality
    - Implement `_score_predictions()` to add/subtract points based on confidence levels
    - Implement `_score_warranty()` to add points for warranty uncertainty
    - Apply all scoring rules: +2 missing data, +1 multiple attachments, +2 warranty uncertain, +1 low confidence, -1 high confidence, +1 contradictions, +1 poor quality
    - Assign priority: score ≤1 → quick_win/rapide, 2-3 → standard_review/standard, ≥4 → expert_review/complexe
    - Return score, level, priority, and breakdown
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12_
  
  - [ ]* 10.2 Write unit tests for complexity scorer
    - Test scoring rules with different scenarios
    - Test priority assignment boundaries
    - Test edge cases (all high confidence, all low confidence)
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12_

- [ ] 11. Implement message generator
  - [x] 11.1 Create `message_generator.py` with MessageGenerator class
    - Implement `generate()` to select and create appropriate customer message
    - Implement `_need_more_info_message()` for poor/unusable input quality
    - Implement `_warranty_not_applicable_message()` for probable warranty exclusions
    - Implement `_reassurance_fast_case_message()` for quick-win cases
    - Create French message templates with professional tone
    - Ensure messages avoid definitive legal warranty decisions
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ]* 11.2 Write unit tests for message generator
    - Test message selection logic for different scenarios
    - Test template rendering with various inputs
    - Test French text formatting
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 12. Checkpoint - Verify business logic components
  - Ensure quality analyzer, warranty engine, complexity scorer, and message generator work correctly, ask the user if questions arise.

- [ ] 13. Create training script
  - [x] 13.1 Create `train_models.py` script
    - Add command-line argument parsing for data path
    - Load training data using DataLoader
    - Preprocess data using Preprocessor
    - Train all models using ModelTrainer
    - Save trained models to models directory
    - Log training statistics and performance metrics
    - Handle errors gracefully with descriptive messages
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 12.1, 12.4_
  
  - [ ]* 13.2 Test training script execution
    - Run training script on sample data
    - Verify models are saved correctly
    - Verify models can be loaded and used for prediction
    - _Requirements: 12.1, 12.2, 12.3_

- [ ] 14. Implement main analysis pipeline
  - [x] 14.1 Create `pipeline.py` with analysis orchestration
    - Implement `analyze_reclamation()` function to orchestrate complete analysis
    - Load models if available, otherwise trigger training
    - Run predictions using Predictor
    - Assess input quality using InputQualityAnalyzer
    - Evaluate warranty using WarrantyEngine
    - Calculate complexity using ComplexityScorer
    - Generate message using MessageGenerator
    - Measure and log processing time
    - Return complete AnalysisResult with all components
    - Handle errors in non-critical components gracefully
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 12.2, 12.3_
  
  - [ ]* 14.2 Write integration tests for pipeline
    - Test end-to-end analysis with sample reclamations
    - Verify all components produce output
    - Verify processing time < 2 seconds
    - _Requirements: 11.4_

- [ ] 15. Implement Streamlit UI
  - [x] 15.1 Create `app.py` with Streamlit interface
    - Create title and sidebar with configuration options
    - Add input section for reclamation selection/upload
    - Add text area for complaint description
    - Add file uploader for attachments
    - Add "Analyser" button to trigger analysis
    - Display predictions section with all four targets and confidence scores
    - Display top 3 solution candidates with scores
    - Display quality assessment with status and issues
    - Display warranty evaluation with status and reasons
    - Display complexity score, level, and priority
    - Display generated customer message when applicable
    - Use clear, professional layout with sections and formatting
    - Add spinner during analysis
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_
  
  - [ ]* 15.2 Manual UI testing
    - Test file upload functionality
    - Test result display formatting
    - Test with various reclamation scenarios
    - _Requirements: 10.8_

- [ ] 16. Implement optional RAG system
  - [~] 16.1 Create `rag.py` with SimpleRAG class (optional)
    - Implement `__init__()` to load warranty documents
    - Implement `_build_index()` to create TF-IDF index for documents
    - Implement `retrieve()` to find top K relevant passages using cosine similarity
    - Return passages with source, text, similarity score, and page number
    - Keep implementation in-memory without external vector database
    - _Requirements: 9.1, 9.2, 9.3_
  
  - [~] 16.2 Integrate RAG into pipeline (optional)
    - Add RAG toggle to configuration
    - Call RAG system when enabled during analysis
    - Include retrieved passages in AnalysisResult
    - Display RAG results in Streamlit UI
    - Ensure pipeline works correctly when RAG is disabled
    - _Requirements: 9.3, 9.4_

- [ ] 17. Add PDF text extraction for warranty docs
  - [~] 17.1 Extend DataLoader with PDF extraction
    - Implement `load_warranty_docs()` using PyPDF2 or pdfplumber
    - Extract text from all warranty PDF files
    - Handle extraction errors gracefully (log and continue)
    - Return list of documents with source filename and extracted text
    - _Requirements: 1.2, 1.6_
  
  - [ ]* 17.2 Test PDF extraction
    - Test with warranty documentation PDFs
    - Verify text extraction quality
    - Test error handling for corrupted PDFs
    - _Requirements: 1.2, 1.6_

- [ ] 18. Create documentation and setup instructions
  - [~] 18.1 Create README.md
    - Document project overview and goals
    - List prerequisites (Python 3.8+, 4GB RAM)
    - Provide installation instructions
    - Document training command: `python train_models.py --data-path Data/Data_WithSolution_Week13`
    - Document demo command: `streamlit run app.py`
    - Include troubleshooting section
    - _Requirements: 13.5_
  
  - [~] 18.2 Add inline code documentation
    - Add docstrings to all classes and public methods
    - Add inline comments for complex logic
    - Ensure code follows Python best practices
    - _Requirements: 13.2, 13.3, 13.4_

- [ ] 19. Final integration and testing
  - [~] 19.1 End-to-end integration test
    - Run training script on full dataset
    - Launch Streamlit app
    - Test with multiple reclamation scenarios: simple cases, complex cases, poor quality inputs
    - Verify all predictions, quality assessment, warranty evaluation, complexity scoring, and messages work correctly
    - Measure processing time for typical cases
    - _Requirements: 11.1, 11.4_
  
  - [~] 19.2 Performance validation
    - Verify analysis completes in < 2 seconds for typical reclamations
    - Profile slow components if needed
    - Optimize if performance targets not met
    - _Requirements: 11.4_

- [~] 20. Final checkpoint - Demo readiness
  - Ensure all components work together, demo runs smoothly, and code is ready for presentation, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- The implementation follows a bottom-up approach: data → ML → business logic → UI
- RAG system (tasks 16.x) is entirely optional and can be deferred post-hackathon
- Focus on getting a working demo first, then add optional testing and RAG features
- All code should be in Python following the design document specifications
