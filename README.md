# SAV Copilot

> AI-powered decision-support system for after-sales complaint qualification.  
> Winner project built from a real Atlantem / HERIGE use case during the AI for Business Hackathon at Centrale Nantes.

SAV Copilot is a **hybrid ML + business-rules + human-in-the-loop** prototype designed to help an after-sales team pre-qualify customer complaints faster without removing human control from uncertain or sensitive cases.

The objective is not to "automate everything". The system uses machine learning where classification is useful, deterministic rules where they are more reliable, and human review when confidence is too low.

---

## The business problem

Atlantem's after-sales team handles hundreds of complaint files every week. A complaint can include a written description, product information and attachments, and then needs to be qualified by the SAV team.

The prototype focuses on helping answer questions such as:

- What type of dispute is this?
- Which internal responsibility is the most likely?
- Which product / component is concerned?
- What is the most likely solution?
- Is the information provided good enough to process the case?
- Is the case simple enough to accelerate, or should it be reviewed by an expert?

---

## Solution overview

The pipeline combines several independent components:

```text
Complaint
   |
   v
Input quality assessment
   |
   v
Text classification
(dispute / responsibility / product / solution)
   |
   v
Confidence scores + Top-3 solution candidates
   |
   v
Business rules for warranty-related signals
   |
   v
Complexity scoring
   |
   +----> Quick / clear case ----> Suggested customer message
   |
   +----> Ambiguous / complex ---> Human review
```

The complete result is exposed through a **Streamlit operator interface**.

---

## ML approach

For the MVP, the classification tasks use a deliberately simple and explainable baseline:

**TF-IDF + Logistic Regression**

Separate classifiers are trained for:

- dispute type
- responsibility
- product detail
- solution

Why this choice?

The problem contains known business categories and historical labelled examples. A classical supervised baseline is therefore:

- fast to train and run
- inexpensive
- easy to evaluate
- easier to explain than a fully generative approach

The prediction layer also exposes confidence scores, and the solution classifier can return a **Top 3** rather than forcing a single answer.

---

## Human-in-the-loop logic

A core design choice is that the system can also decide **not to automate**.

The complexity score combines signals such as:

- input quality
- model confidence
- warranty uncertainty
- contradictory prediction confidence
- attachment volume

Clear cases can be prioritized for faster handling. Ambiguous cases are routed to standard or expert review.

This makes the prototype a **copilot** rather than an autonomous decision-maker.

---

## Business rules and guardrails

Not every part of the problem requires machine learning.

The warranty module uses explicit patterns to identify signals related to situations such as:

- normal wear
- poor maintenance / installation issues
- handling damage
- aggressive environment / corrosion
- hardware or electronic accessories

The output remains deliberately cautious: the engine provides an indicative status and does **not** claim to make a legal warranty decision.

---

## Main features

- Multi-target complaint classification
- Prediction confidence scores
- Top-3 solution suggestions
- Input quality analysis
- Warranty-related rule engine
- Complexity and priority scoring
- Human-in-the-loop routing
- Contextual customer-message suggestions
- Streamlit operator interface
- End-to-end demo script
- Unit / pipeline tests

---

## Tech stack

- **Python**
- **scikit-learn**
- **pandas / NumPy**
- **Streamlit**
- **joblib**
- **openpyxl / PyPDF2**

---

## Repository structure

```text
sav-copilot/
├── app.py                         # Streamlit interface
├── train_models.py                # Model training entry point
├── demo_pipeline.py               # End-to-end demo
├── config.py                      # Paths, thresholds and ML configuration
├── requirements.txt
├── sav_copilot/
│   ├── data_loader.py
│   ├── trainer.py
│   ├── predictor.py
│   ├── quality_analyzer.py
│   ├── warranty_engine.py
│   ├── complexity_scorer.py
│   ├── message_generator.py
│   └── pipeline.py
└── tests/
```

---

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/miranovic/sav-copilot.git
cd sav-copilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add compatible training data and train the classifiers

The original hackathon dataset is **not redistributed in this public repository**.

The training pipeline expects complaint descriptions and labelled target columns compatible with the schema documented in `sav_copilot/data_loader.py`.

Then run:

```bash
python train_models.py
```

### 5. Launch the interface

```bash
streamlit run app.py
```

You can also inspect the end-to-end pipeline from the command line:

```bash
python demo_pipeline.py
```

---

## Current scope and limitations

This repository represents a **prototype / MVP**, not a production-grade SAV system.

Current limitations include:

- trained models and proprietary hackathon data are not included
- image processing was part of the original use-case scope, but this public MVP primarily focuses on text and business-data qualification
- the warranty engine is heuristic and indicative only
- confidence thresholds would need calibration on a larger validation set
- monitoring, authentication and production observability are not implemented
- the application is not containerized yet

---

## What I would improve next

If I were taking the project from prototype to production, I would prioritize:

1. **Benchmark classical ML vs. LLM / hybrid classification**  
   Compare accuracy, latency, cost and maintainability.

2. **Add true multimodal processing**  
   Analyze SAV images and documents instead of only using attachment metadata.

3. **Introduce stronger evaluation and monitoring**  
   Track precision/recall per class, confidence calibration, drift and human overrides.

4. **Expose the analysis pipeline through an API**  
   Separate the UI from the decision service.

5. **Containerize and harden deployment**  
   Docker, environment-based secrets, CI/CD, structured logging and observability.

6. **Improve human-review workflows**  
   Capture operator corrections and feed them back into future model iterations.

---

## Product principles behind the prototype

This project reflects three principles I try to apply when building AI products:

- **Problem first, technology second.**
- **Use deterministic rules when they are safer than AI.**
- **Automation is only valuable if uncertainty and human escalation are designed explicitly.**

---

## Context

This prototype was developed from an **Atlantem / HERIGE after-sales use case** during the **AI for Business Hackathon - Centrale Nantes (2026)**.

Some code and structure were cleaned up / extended after the initial hackathon prototype so the project could be documented and demonstrated more clearly.

---

## Author

**Imran**  
Product × Data × AI / Automation Builder

GitHub: https://github.com/miranovic
