import streamlit as st
from huggingface_hub import hf_hub_download
from transformers import pipeline
import matplotlib.pyplot as plt
import numpy as np
import os
import re
import requests
import urllib.parse
from io import BytesIO
from PIL import Image
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
except:
    st.error("⚠️ Missing API Key in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# --- CACHED MODELS ---
@st.cache_resource
def load_bert_model():
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
    prompt = f"Write a model card for this README. License: {license_type}. README: {readme_text}"
    return generate_llm_text(prompt)

def draft_card_v2_structured(readme_text, license_type):
    prompt = f"""You are a responsible AI assistant. Draft a model card based on the README.
Requirements:
1. Must include these sections exactly: ## Model Details, ## Intended Use, ## Limitations, ## Ethical Considerations.
2. If the README does not mention evaluation metrics, write "Not specified" — do not fabricate.
3. License: {license_type}

README: {readme_text}
Model card draft:"""
    return generate_llm_text(prompt)

def draft_datasheet(readme_text, model_id):
    prompt = f"""You are an AI auditor. Create a Dataset Datasheet for the dataset used to train or evaluate the model {model_id}.
Based on the README, fill in these sections:
## Motivation
## Composition
## Collection Process
## Uses
## Limitations
If info is missing, write "Not specified in README".
README: {readme_text}"""
    return generate_llm_text(prompt)

def check_missing_sections(readme_text, target_sections):
    missing = []
    text_to_check = readme_text[:1500]
    for section in target_sections:
        res = classifier(text_to_check, candidate_labels=[section, "other"], multi_label=True)
        idx = res['labels'].index(section)
        score = res['scores'][idx]
        if score < 0.5: 
            missing.append(section)
    return missing

def check_hallucinated_metrics(generated_text, readme_text):
    metrics_in_card = re.findall(r'\b\d+(?:\.\d+)?%?\b', generated_text)
    hallucinations = []
    clean_readme = readme_text.replace(" ", "").replace("\n", "")
    for metric in metrics_in_card:
        if len(metric) > 1 and metric not in readme_text and metric not in clean_readme:
            hallucinations.append(metric)
    return list(set(hallucinations))

def generate_image(prompt):
    try:
        safe_prompt = urllib.parse.quote(f"Abstract digital art representing AI model: {prompt[:50]}")
        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=512&height=512&nologo=true"
        response = requests.get(url, timeout=15)
        img = Image.open(BytesIO(response.content))
        img_path = "cover.png"
        img.save(img_path)
        return img_path
    except Exception as e:
        print(f"Image error: {e}")
        return None

def generate_audio(text):
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
    
    **Attention Mechanism:** The LLM reads the README using self-attention. It weighs the importance of every word against every other word to extract context.
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
                zs_text = draft_card_v1_zero_shot(readme, license_type)
                mc_text = draft_card_v2_structured(readme, license_type)
                ds_text = draft_datasheet(readme, model_id)
                
                required_sections = ["Model Details", "Intended Use", "Limitations", "Ethical Considerations", "Training Data", "Evaluation"]
                missing = check_missing_sections(readme, required_sections)
                hallucinations = check_hallucinated_metrics(mc_text, readme)
                
                img_path = generate_image(f"cover for {model_id}")
                audio_path = generate_audio(mc_text[:200])
                
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
                
                st.subheader("Prompt Comparison (U1)")
                st.table({
                    "Technique": ["Zero-shot", "Structured"],
                    "Output length": [len(zs_text), len(mc_text)],
                    "Has Sections": ["No", "Yes"]
                })
                
                st.subheader("Visuals & Audio")
                col_img, col_aud, col_chart = st.columns(3)
                with col_img:
                    if img_path:
                        st.image(img_path, caption="Generated Cover Image")
                    else:
                        st.info("Image generation failed. Try again in a moment.")
                with col_aud:
                    if audio_path:
                        st.audio(audio_path)
                with col_chart:
                    radar_path = generate_radar(missing, len(required_sections))
                    st.image(radar_path, caption="README Gap Analysis")
                    
                pdf_filename = f"{model_id.replace('/', '_')}_doc.pdf"
                export_pdf(mc_text + "\n\n" + ds_text, img_path, pdf_filename)
                with open(pdf_filename, "rb") as f:
                    st.download_button("📥 Download PDF", data=f, file_name=pdf_filename)
