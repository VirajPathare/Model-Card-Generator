# 📄 Model Card & Datasheet Generator

## 📖 Project Objective
This application automatically drafts a Model Card and Dataset Datasheet for a given Hugging Face model. It uses a Large Language Model (via Groq) to read the model's README, a DistilBERT classifier to check for missing documentation sections, and generates a cover image using Stable Diffusion. 

**Live Demo:** [https://model-card-generator-fyuxi9ap8wqebavksdd3op.streamlit.app/](https://model-card-generator-fyuxi9ap8wqebavksdd3op.streamlit.app/)

## 🚀 Key Features (Syllabus Coverage)
- **Foundations (U1):** Compares Zero-shot vs. Structured prompting techniques.
- **LLMs & GANs (U2):** Uses the `openai/gpt-oss-20b` model for text generation.
- **Multimodal (U3):** Uses `typeform/distilbert-base-uncased-mnli` for text classification and `stabilityai/sd-turbo` for image generation.
- **Tools (U4):** Built with Streamlit, ReportLab (PDF export), and gTTS (Audio summary).
- **Responsible AI (U5):** Features a regex-based guardrail to catch hallucinated metrics, requires manual license input, and flags missing sections in the source README.

## 📊 Results and Evaluation
We tested the generator on two models. The table below shows the evaluation:

| Model Tested | Prompt Style | Latency | Guardrail Flagged Hallucinations? |
| :--- | :--- | :--- | :--- |
| `bert-base-uncased` | Structured | ~2.1s | No (Clean generation) |
| `distilbert-sst2` | Structured | ~2.4s | **Yes** (Flagged numbers like 0.9106) |

### ⚠️ Failure Case Documented
**Scenario:** Gated Models or Empty READMEs
If the user inputs a gated model (e.g., `meta-llama/Llama-2-7b`), the `hf_hub_download` function fails due to access restrictions. 
**Mitigation:** The UI handles this gracefully by displaying an error and prompting the user to use the "Paste README manually" input box.

## 🛠️ Installation (Local)
1. Clone the repo: `git clone https://github.com/VirajPathare/Model-Card-Generator.git`
2. Install requirements: `pip install -r requirements.txt`
3. Set your API keys:
   ```bash
   export GROQ_API_KEY="gsk_..."
   export HF_TOKEN="hf_..."
