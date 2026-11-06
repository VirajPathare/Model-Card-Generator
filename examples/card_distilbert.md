# Model Card: distilbert-base-uncased-finetuned-sst-2-english

## Model Details
**Model name**: `distilbert-base-uncased-finetuned-sst-2-english`  
**Architecture**: DistilBERT (a distilled version of BERT) fine-tuned for binary sentiment classification.  
**Pre-training data**: Wikipedia + BookCorpus (standard DistilBERT pre-training).  
**Fine-tuning data**: Stanford Sentiment Treebank 2 (SST-2) – English sentences labeled as positive or negative.  
**Task**: Text classification (binary sentiment).  

**Evaluation**  
| Metric | Value | Dataset | Split | Verified |
|--------|-------|---------|-------|----------|
| Accuracy | 0.9106 | GLUE (SST-2) | validation | ✅ |
| Precision | 0.8978 | GLUE (SST-2) | validation | ✅ |
| Recall | 0.9302 | GLUE (SST-2) | validation | ✅ |
| AUC | 0.9717 | GLUE (SST-2) | validation | ✅ |
| F1 | 0.9137 | GLUE (SST-2) | validation | ✅ |
| Loss | 0.3901 | GLUE (SST-2) | validation | ✅ |
| Accuracy | 0.9886 | SST-2 | train | ✅ |
| Precision (Macro) | 0.9882 | SST-2 | train | ✅ |
| Precision (Micro) | 0.9886 | SST-2 | train | ✅ |
| Precision (Weighted) | 0.9886 | SST-2 | train | ✅ |

**License**: MIT

---

## Intended Use
This model is designed for **sentiment analysis of English text**. Typical applications include:
- Classifying customer reviews, social media posts, or product feedback as positive or negative.
- Pre-processing step for downstream NLP pipelines that require sentiment labels.
- Rapid prototyping of sentiment-aware chatbots or recommendation systems.

The model should be used only on English language inputs and is not intended for multilingual or domain-specific sentiment tasks without further fine-tuning.

---

## Limitations
- **Language**: Only English text is supported; performance on other languages is unknown.  
- **Domain**: Trained on general sentiment data; may under-perform on highly technical, legal, or medical text.  
- **Context**: The model does not capture sarcasm, irony, or nuanced sentiment that relies on broader context.  
- **Bias**: As with many sentiment models, it may reflect biases present in the training data (e.g., gender or cultural stereotypes).  
- **Interpretability**: The model is a black-box transformer; it does not provide explanations for its predictions.  
- **Resource usage**: Requires a GPU or CPU with sufficient memory for inference; not optimized for extremely low-latency environments.

---

## Ethical Considerations
- **Bias & Fairness**: The model may exhibit bias toward certain demographic groups or linguistic styles. Users should evaluate fairness on their specific data before deployment.  
- **Misuse**: Sentiment predictions could be used to manipulate opinions or target specific audiences. Deployers should implement safeguards against such misuse.  
- **Privacy**: The model does not store or transmit user data; however, any data fed to the model should be handled in compliance with privacy regulations.  
- **Transparency**: Provide clear documentation to end-users that the model is a statistical classifier and not a definitive judgment of sentiment.  
- **Responsible Deployment**: Consider human-in-the-loop review for high-stakes decisions (e.g., content moderation, hiring).  

---

# Dataset Datasheet: SST-2 (Stanford Sentiment Treebank 2)

*(Information derived solely from the provided README; where details are absent, "Not specified in README" is indicated.)*

### 1. Motivation  
**Why was this dataset created?**  
Not specified in README.  

### 2. Composition  
**What are the instances? Do they represent specific demographics?**  
Not specified in README.  

### 3. Collection Process  
**How was data acquired?**  
Not specified in README.  

### 4. Uses  
**What tasks is it suitable for?**  
- Text classification  
- Sentiment analysis (binary sentiment – positive vs. negative) on movie reviews  

These uses are inferred from the model-index entry, which lists the dataset as "sst2" and the task type as "text-classification."  

### 5. Limitations  
**What should users do with it?**  
Not specified in README.  

---

## 🚨 Guardrail Alert (Proof of U5 Layer)
When testing this model, the app successfully triggered the guardrail warning: 
*LLM may have hallucinated these numbers: ['0.9302', '0.9106', '0.9717', '0.9882', '0.9886']*
This proves the responsible AI feature is functioning correctly.
