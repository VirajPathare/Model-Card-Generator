import streamlit as st
import os

# Import all our backend functions from the src folder
from src.generator import (
    fetch_readme, draft_card_v1_zero_shot, draft_card_v2_structured,
    draft_datasheet, check_missing_sections, check_hallucinated_metrics,
    generate_image, generate_audio, generate_radar, export_pdf
)

st.set_page_config(page_title="Model Card Generator", layout="wide", page_icon="📄")
st.title("📄 Model Card & Datasheet Generator")

# Tabs for U1/U2 Explanations
tab1, tab2, tab3 = st.tabs(["🚀 App Interface", "🧠 How It Works (U1/U2)", "📋 Model Card (This App)"])

with tab2:
    st.header("Lifecycle & Architecture")
    st.markdown("""
    **ML Lifecycle Position:** Documentation is generated *after* model training/evaluation, right before deployment and governance review.
    **Generative vs Discriminative:** 
    - *Generative:* The Groq LLM generates the text for the card. The Image API generates the cover.
    - *Discriminative:* The DistilBERT classifier predicts whether a section is present.
    
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
                        st.info("Image gen failed.")
                with col_aud:
                    if audio_path:
                        st.audio(audio_path)
                with col_chart:
                    radar_path = generate_radar(missing)
                    st.image(radar_path, caption="README Gap Analysis")
                    
                pdf_filename = f"{model_id.replace('/', '_')}_doc.pdf"
                export_pdf(mc_text + "\n\n" + ds_text, img_path, pdf_filename)
                with open(pdf_filename, "rb") as f:
                    st.download_button("📥 Download PDF", data=f, file_name=pdf_filename)
