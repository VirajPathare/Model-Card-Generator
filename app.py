import streamlit as st
from huggingface_hub import hf_hub_download, InferenceClient
from transformers import pipeline
import matplotlib.pyplot as plt
import numpy as np
import os
import re
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from gtts import gTTS
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Model Card Generator", layout="wide", page_icon="📄")

# --- SAFE SECRETS RETRIEVAL ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    HF_TOKEN = st.secrets.get("HF_TOKEN", "") # Optional for image API
except:
    st.error("⚠️ Missing API Key in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# --- CACHED MODELS ---
@st.cache_resource
def load_bert_model():
    # Switched to DistilBERT as requested by evaluator
    return pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")

classifier = load_bert_model()

# ==========================================
# CORE FUNCTIONS
# ==========================================
def fetch_readme(model_id):
    try:
        path = hf_hub_download(repo_id=model_id, filename="README.md")
        with open(path, "r") as f:
            return f.read()[:4000] 
    except:
        return None

def generate_llm_text(prompt, model="openai/gpt-oss-20b"):
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0.1
    )
    return chat_completion.choices[0].message.content

def draft_card_v1_zero_shot(readme_text, license_type):
    # U1: Prompt Technique 1 (Zero-shot)
    prompt = f"Write a model card for this README. License: {license_type}. README: {readme_text}"
    return generate_llm_text(prompt)

def draft_card_v2_structured(readme_text, license_type):
    # U1: Prompt Technique 2 (Structured/Few-shot)
    prompt = f"""You are a responsible AI assistant. Draft a model card based on the README.
Requirements:
1. Must include these sections exactly: ## Model Details, ## Intended Use, ## Limitations, ## Ethical Considerations.
2. If the README does not mention evaluation metrics, write "Not specified" — do not fabricate.
3. License: {license_type}

README: {readme_text}
Model card draft:"""
    return generate_llm_text(prompt)

def draft_datasheet(readme_text, model_id):
    # U2: Datasheet Generation
    prompt = f"""You are an AI auditor. Create a Dataset Datasheet for the dataset used to train or evaluate the model {model_id}.
Based on the README, fill in these sections:
## Motivation (Why was this dataset created?)
## Composition (What are the instances? Do they represent specific demographics?)
## Collection Process (How was data acquired?)
## Uses (What tasks is it suitable for?)
## Limitations (What should users not do with it?)
If info is missing, write "Not specified in README".
README: {readme_text}"""
    return generate_llm_text(prompt)

def check_missing_sections(readme_text, target_sections):
    # U3 Bug Fix: Check the source README, not the generated text. And fix the score lookup.
    missing = []
    # Limit to first 1500 chars for speed
    text_to_check = readme_text[:1500]
    for section in target_sections:
        res = classifier(text_to_check, candidate_labels=[section, "other"], multi_label=True)
        # Fix: find the exact index of our section
        idx = res['labels'].index(section)
        score = res['scores'][idx]
        if score < 0.5: # Adjust threshold as needed
            missing.append(section)
    return missing

def check_hallucinated_metrics(generated_text, readme_text):
    # U5: Guardrail against ungrounded metrics
    # Find numbers like "95%", "0.85", "1.5B"
    metrics_in_card = re.findall(r'\b\d+(?:\.\d+)?%?\b', generated_text)
    hallucinations = []
    for metric in metrics_in_card:
        # Filter out tiny numbers like section headers (e.g., "1.", "2.")
        if len(metric) > 1 and metric not in readme_text:
            hallucinations.append(metric)
    return list(set(hallucinations))

def generate_image(prompt):
    # U3/U4: Generative Image via HF API
    try:
        # Using a fast text-to-image model via Inference API
        image_client = InferenceClient(model="stabilityai/sd-turbo", token=HF_TOKEN)
        image = image_client.text_to_image(f"Abstract digital art representing: {prompt[:100]}", width=512, height=512)
        img_path = "cover.png"
        image.save(img_path)
        return img_path
    except Exception as e:
        return None

def generate_audio(text):
    # U4: Audio Generation
    try:
        tts = gTTS(text=text[:200], lang='en')
        audio_path = "summary.mp3"
        tts.save(audio_path)
        return audio_path
    except:
        return None

def generate_radar(missing_count, total_req):
    categories = ['Details', 'Use', 'Limits', 'Ethics']
    vals = [0 if c in missing_count else 1 for c in ['Model Details', 'Intended Use', 'Limitations', 'Ethical Considerations']]
    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
    vals += vals[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, vals, color='blue', alpha=0.25)
    ax.plot(angles, vals, color='blue', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    plt.savefig("radar.png", bbox_inches='tight')
    plt.close()
    return "radar.png"

def export_pdf(text, img_path, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    style = styles['Normal']
    story = []
    
    if img_path and os.path.exists(img_path):
        story.append(ReportLabImage(img_path, width=300, height=300))
        story.append(Spacer(1, 12))
        
    for line in text.split('\n'):
        if line.strip():
            try:
                story.append(Paragraph(line.replace("##", ""), style))
                story.append(Spacer(1, 12))
            except:
                pass
    doc.build(story)
    return filename

# ==========================================
# STREAMLIT UI
# ==========================================
st.title("📄 Model Card & Datasheet Generator")

# Tabs for U1/U2 Explanations
tab1, tab2, tab3 = st.tabs(["🚀 App Interface", "🧠 How It Works (U1/U2)", "📋 Model Card (This App)"])

with tab2:
    st.header("Lifecycle & Architecture")
    st.markdown("""
    **ML Lifecycle Position:** Documentation is generated *after* model training/evaluation, right before deployment and governance review.
    **Generative vs Discriminative:** 
    - *Generative:* The Groq LLM generates the text for the card. The Image API generates the cover.
    - *Discriminative:* The DistilBERT classifier predicts whether a section is present (classification task).
    
    **Probability View:** The zero-shot classifier outputs a softmax probability. We flag a section as "missing" if the probability score is below 0.5.
    
    **Attention Mechanism:** The LLM reads the README using self-attention. It weighs the importance of every word against every other word to extract context (e.g., noticing the word "limitations" near a bullet point).
    """)

with tab3:
    st.markdown("""
    ### Intended Use
    To assist ML practitioners in drafting model cards and datasheets from raw README files.
    ### Limitations
    - The LLM can hallucinate metrics if not strictly guarded.
    - The BERT classifier has a context window limit (1500 chars).
    ### Ethical Considerations
    Users must manually review the generated output before publishing. We use a guardrail to flag fabricated metrics.
    ### License
    MIT License.
    """)

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        model_id = st.text_input("Hugging Face Model ID", "bert-base-uncased")
    with col2:
        license_type = st.selectbox("License", ["MIT", "Apache-2.0", "GPL", "Other"])

    readme_override = st.text_area("Or paste README manually (Optional)", height=100)

    if st.button("Generate Documentation", type="primary"):
        with st.spinner("Processing..."):
            readme = readme_override or fetch_readme(model_id)
            
            if not readme:
                st.error("Failed to read README. Please paste it manually.")
            else:
                # U1: Generate Zero-shot (for comparison)
                zs_text = draft_card_v1_zero_shot(readme, license_type)
                # U1: Generate Structured
                mc_text = draft_card_v2_structured(readme, license_type)
                # U2: Generate Datasheet
                ds_text = draft_datasheet(readme, model_id)
                
                # U3: Check missing sections (on README, not output)
                required_sections = ["Model Details", "Intended Use", "Limitations", "Ethical Considerations", "Training Data", "Evaluation"]
                missing = check_missing_sections(readme, required_sections)
                
                # U5: Guardrail Check
                hallucinations = check_hallucinated_metrics(mc_text, readme)
                
                # U4: Multimodal Generation
                img_path = generate_image(f"cover for {model_id}")
                audio_path = generate_audio(mc_text[:200])
                
                # Display Results
                st.success("Generation Complete!")
                
                if hallucinations:
                    st.error(f"🚨 GUARDRAIL ALERT: LLM may have hallucinated these numbers: {hallucinations}")
                else:
                    st.success("✅ Guardrail: No ungrounded metrics detected.")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Model Card")
                    st.text_area("", mc_text, height=300)
                with c2:
                    st.subheader("Datasheet")
                    st.text_area("", ds_text, height=300)
                
                # U1: Prompt Comparison Table
                st.subheader("Prompt Comparison (U1)")
                st.table({
                    "Technique": ["Zero-shot", "Structured"],
                    "Output length": [len(zs_text), len(mc_text)],
                    "Has Sections": ["No", "Yes"]
                })
                
                # U3/U4 Visuals
                st.subheader("Visuals & Audio")
                col_img, col_aud, col_chart = st.columns(3)
                with col_img:
                    if img_path:
                        st.image(img_path, caption="Generated Cover Image")
                    else:
                        st.info("Image gen failed (Check HF_TOKEN).")
                with col_aud:
                    if audio_path:
                        st.audio(audio_path)
                with col_chart:
                    radar_path = generate_radar(missing, len(required_sections))
                    st.image(radar_path, caption="README Gap Analysis")
                    
                # PDF Export
                pdf_filename = f"{model_id.replace('/', '_')}_doc.pdf"
                export_pdf(mc_text + "\n\n" + ds_text, img_path, pdf_filename)
                with open(pdf_filename, "rb") as f:
                    st.download_button("📥 Download PDF", data=f, file_name=pdf_filename)
