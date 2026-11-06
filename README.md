# Model Card & Datasheet Generator

## Project Objective
This application automatically drafts a Model Card and Datasheet for a given Hugging Face model using an LLM (Groq), checks for missing sections using a BERT-family classifier, and provides a downloadable PDF.

## Live Demo
[Insert Streamlit URL Here]

## Features
- **U1 (Foundations):** Prompt engineering compared (Zero-shot vs Structured).
- **U2 (LLMs):** Uses `openai/gpt-oss-20b` via Groq for text generation.
- **U3 (Multimodal/BERT):** Uses `facebook/bart-large-mnli` to detect missing sections.
- **U4 (Tools):** Python + Streamlit, ReportLab for PDF export, Matplotlib for radar chart.
- **U5 (Responsible AI):** Guardrails against hallucinating metrics; requires manual license input.
