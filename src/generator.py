import os
import re
import requests
import urllib.parse
from io import BytesIO
from PIL import Image
from huggingface_hub import hf_hub_download
from transformers import pipeline
import matplotlib.pyplot as plt
import numpy as np
from groq import Groq
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from gtts import gTTS
import warnings
warnings.filterwarnings('ignore')

# --- INITIALIZATION ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)

try:
    classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")
except:
    classifier = None

# --- CORE FUNCTIONS ---
def fetch_readme(model_id):
    try:
        path = hf_hub_download(repo_id=model_id, filename="README.md")
        with open(path, "r") as f:
            return f.read()[:4000] 
    except:
        return None

def generate_llm_text(prompt):
    if not client: return "Error: GROQ_API_KEY missing."
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="openai/gpt-oss-20b",
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
    if not classifier: return ["Model Error"]
    missing = []
    text_to_check = readme_text[:1500]
    for section in target_sections:
        res = classifier(text_to_check, candidate_labels=[section, "other"], multi_label=True)
        idx = res['labels'].index(section)
        if res['scores'][idx] < 0.5: 
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

def generate_radar(missing_count):
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
