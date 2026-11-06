# Model Card for Model Card & Datasheet Generator App

## Model Details
- **Developed by:** Viraj Pathare
- **Model type:** LLM Wrapper (Groq `openai/gpt-oss-20b`) + DistilBERT Classifier (`typeform/distilbert-base-uncased-mnli`) + Hugging Face Inference API (`stabilityai/sd-turbo`).
- **Language:** English
- **License:** MIT

## Intended Use
- **Primary use:** Assisting ML developers and researchers in drafting Model Cards and Dataset Datasheets from raw Hugging Face README files.
- **Primary users:** AI practitioners, auditors, and students.
- **Out-of-scope:** Generating legal documentation, compliance certificates, or publishing text without human review.

## Factors
- The tool's output is heavily dependent on the quality and length of the source README. 
- The BERT classifier only reads the first 1500 characters of the README for gap analysis.

## Metrics
- **Latency:** Average generation time is ~2.5 seconds.
- **Guardrail Accuracy:** Regex-based hallucination checker successfully flags fabricated percentages (e.g., "95% accuracy") that are not grounded in the source README.

## Evaluation Data
- Evaluated on public Hugging Face models: `bert-base-uncased` and `distilbert-base-uncased-finetuned-sst-2-english`.

## Ethical Considerations
- **Hallucination Risk:** LLMs are prone to making up facts. This app includes a guardrail to warn users, but human review is strictly required.
- **Bias:** The LLM may generate biased text if the source README contains biased language. 

## Limitations
- **Gated Models:** The app cannot fetch READMEs for gated models (e.g., Llama-2). Users must paste the README manually.
- **Context Window:** Long READMEs are truncated to 4000 characters to fit the LLM's context window.
