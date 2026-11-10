<div align="center">
  <h1>📄 Model Card & Datasheet Generator</h1>
  <p><b>Automated Responsible AI Documentation for Hugging Face Models</b></p>

  <!-- Badges -->
  <a href="https://model-card-generator-fyuxi9ap8wqebavksdd3op.streamlit.app/"><img src="https://img.shields.io/badge/🚀_Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo"></a>
  <a href="https://github.com/VirajPathare/Model-Card-Generator/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://huggingface.co"><img src="https://img.shields.io/badge/🤗_Hugging_Face-Transformers-FFD21E?style=for-the-badge" alt="Hugging Face"></a>
  <a href="https://groq.com"><img src="https://img.shields.io/badge/⚡_Groq-LLM-f55036?style=for-the-badge" alt="Groq"></a>
</div>

<br />

## 📖 Overview
This application automatically drafts a **Model Card** and **Dataset Datasheet** for a given Hugging Face model. It reads the model's `README.md`, uses a Large Language Model (Groq) to generate the documentation, uses a DistilBERT classifier to check for missing sections, and includes responsible AI guardrails to prevent hallucinated metrics.

## 🧠 Generative AI Syllabus Coverage

| Layer | Unit | Implementation in this Project |
| :---: | :--- | :--- |
| **I** | **Foundations** | **U1:** Compares Zero-shot vs. Structured prompting techniques. Includes ML Lifecycle positioning. |
| **II** | **GANs & LLMs** | **U2:** Uses the Groq API (`openai/gpt-oss-20b`) Transformer LLM for core text generation. |
| **III** | **GPT, BERT & Multimodal** | **U3:** Uses `typeform/distilbert-base-uncased-mnli` for gap analysis. Generates an AI Cover Image (Pollinations AI) and Audio (gTTS). |
| **IV** | **Tools & Generation** | **U4:** Built with Python & Streamlit. Uses `ReportLab` to export a downloadable PDF and `Matplotlib` for a Radar chart. |
| **V** | **Responsible AI** | **U5:** Features a Regex-based guardrail to catch hallucinated metrics, flags missing README sections, and provides an ethical License/IP note. |

## 📊 Results and Evaluation

### Prompt Engineering Comparison (U1)
| Technique | Output Length | Has Required Sections? |
| :--- | :--- | :--- |
| **Zero-shot** | 0 characters | No |
| **Structured** | 318 characters | Yes |

### Model Testing Results (U5 Guardrail)
| Model Tested | Guardrail Flagged Hallucinations? | Image Gen | Audio Gen |
| :--- | :--- | :--- | :--- |
| `bert-base-uncased` | **Yes** (Flagged "110", "768", "12") | Success | Success |
| `distilbert-sst2` | **Yes** (Flagged "0.9106", "0.9717") | Success | Success |

### ⚠️ Documented Failure Cases
* **Groq Rate Limit:** During testing, the app encountered a `429 Too Many Requests` error. *Mitigation:* Added `max_tokens=500` and truncated README input to 2000 chars.
* **Gated Models:** The app cannot fetch READMEs for models like Meta's Llama. *Mitigation:* The UI includes a "Paste README manually" text box.

## 📂 Generated Examples
As per the project deliverables, here are the generated cards for 2 Hugging Face models:
* 📄 [Example 1: BERT Base Uncased (Markdown)](./examples/card_bert.md)
* 📄 [Example 2: DistilBERT SST-2 (Markdown)](./examples/card_distilbert.md)

## 🛠️ Installation (Local)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VirajPathare/Model-Card-Generator.git
