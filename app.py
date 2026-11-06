import streamlit as st
from huggingface_hub import hf_hub_download
from transformers import pipeline
import matplotlib.pyplot as plt
import numpy as np
import os
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
import warnings
warnings.filterwarnings('ignore')

# Page setup
st.set_page_config(page_title="P57 Model Card Generator", layout="wide")
st.title("P57 Model Card & Datasheet Generator")

# Load API key from Streamlit secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Missing API Key. Please add GROQ_API_KEY to Streamlit secrets.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# CACHED MODELS (So it doesn't reload every time)
# ==========================================
@st.cache_resource
def load_bert_model():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

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

def draft_card(readme_text, form_data):
    prompt = f"""You are a responsible AI documentation assistant. Draft a model card based on the README and form below. Requirements:
1. Must include these sections exactly: ## Model Details, ## Intended Use, ## Limitations, ## Ethical Considerations.
2. If the README does not mention evaluation metrics, write "Not specified" — do not fabricate.
3. Form info: {form_data}

README: {readme_text}
Model card draft:"""
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-20b", # Updated working Groq model
        temperature=0.1
    )
    return chat_completion.choices[0].message.content

def check_missing_sections(card_text):
    required = ["Model Details", "Intended Use", "Limitations", "Ethical Considerations"]
    missing = []
    for section in required:
        if section.lower() not in card_text.lower():
            res = classifier(card_text[:1000], candidate_labels=[section, "other"], multi_label=True)
            if res['scores'][0] < 0.6: 
                missing.append(section)
    return missing

def generate_radar(missing_count):
    categories = ['Details', 'Use', 'Limits', 'Ethics']
    values = [0 if c in missing_count else 1 for c in ['Model Details', 'Intended Use', 'Limitations', 'Ethical Considerations']]
    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
    values += values[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='blue', alpha=0.25)
    ax.plot(angles, values, color='blue', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    plt.savefig("radar.png", bbox_inches='tight')
    plt.close()
    return "radar.png"

def export_pdf(md_text, filename="model_card.pdf"):
    clean_text = md_text.replace("**", "").replace("*", "").replace("##", "")
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    style = styles['Normal']
    style.alignment = TA_LEFT
    story = []
    for line in clean_text.split('\n'):
        if line.strip():
            try:
                story.append(Paragraph(line, style))
                story.append(Spacer(1, 12))
            except:
                pass
    doc.build(story)
    return filename

# ==========================================
# STREAMLIT UI
# ==========================================
col1, col2 = st.columns([3, 1])
with col1:
    model_id = st.text_input("Hugging Face Model ID", "bert-base-uncased")
with col2:
    license_type = st.selectbox("License", ["MIT", "Apache-2.0", "GPL", "Other"])

readme_override = st.text_area("Or paste README manually (Optional)", height=100)

if st.button("Generate Card", type="primary"):
    with st.spinner("Generating card and analyzing sections..."):
        readme = readme_override or fetch_readme(model_id)
        
        if not readme:
            st.error("Failed to read README. Please paste it manually.")
        else:
            try:
                card_text = draft_card(readme, f"License: {license_type}")
                
                if not card_text:
                    st.error("LLM returned empty text. Check API key.")
                else:
                    missing = check_missing_sections(card_text)
                    
                    st.subheader("Generated Model Card")
                    st.text_area("", card_text, height=300)
                    
                    if missing:
                        st.warning(f"Missing sections detected: {', '.join(missing)}")
                    else:
                        st.success("All sections present.")
                    
                    col_img, col_pdf = st.columns(2)
                    
                    with col_img:
                        radar_path = generate_radar(missing)
                        st.image(radar_path, caption="Completeness Radar")
                    
                    with col_pdf:
                        pdf_path = export_pdf(card_text)
                        with open(pdf_path, "rb") as f:
                            st.download_button(
                                label="📥 Download Model Card PDF",
                                data=f,
                                file_name=f"{model_id.replace('/', '_')}_card.pdf",
                                mime="application/pdf"
                            )
            except Exception as e:
                st.error(f"System Error: {str(e)}")
