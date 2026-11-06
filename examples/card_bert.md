# Model Card: bert-base-uncased

## Model Details
- **Model name**: `bert-base-uncased`  
- **Architecture**: Transformer encoder (BERT)  
- **Parameters**: 110 M  
- **Training data**: BookCorpus and Wikipedia (English)  
- **Pre-training objectives**:  
  - Masked Language Modeling (MLM) – 15 % of tokens are masked and predicted.  
  - Next Sentence Prediction (NSP) – model predicts whether two sentences are consecutive.  
- **Tokenization**: WordPiece with an uncased vocabulary (case-insensitive).  
- **License**: MIT  

## Intended Use
The model is primarily intended to be fine-tuned on downstream natural language processing tasks that benefit from contextual sentence representations, such as text classification, named entity recognition, question answering, and sentiment analysis.

## Limitations
- **Evaluation metrics**: Not specified.  
- **Biases**: Trained on large English corpora that may contain cultural, gender, and other societal biases.  
- **Domain coverage**: Optimized for general English text; performance may degrade on specialized or low-resource domains.  
- **Resource requirements**: Requires significant GPU memory for fine-tuning and inference (≈110 M parameters).  

## Ethical Considerations
- **Potential misuse**: The model can generate plausible but potentially misleading or harmful text if used without careful filtering.  
- **Bias amplification**: Fine-tuning on biased datasets can amplify existing biases present in the pre-training data.  
- **Privacy**: The model was trained on publicly available text; it does not store personal data but may inadvertently reproduce sensitive content seen during training.  
- **Responsible deployment**: Users should evaluate the model’s outputs for fairness, safety, and compliance with applicable regulations before deployment.

---

# Dataset Datasheet: BookCorpus + Wikipedia

| Section | Content |
|---------|---------|
| **Dataset name** | BookCorpus + Wikipedia (English) |
| **Version** | The corpus used in the original BERT release (2018) |
| **License** | Apache-2.0 (as listed in the README) |
| **Sources** | `bookcorpus`, `wikipedia` |

### 1. Motivation (Why was this dataset created?)
The corpus was assembled to provide a large, diverse, and publicly available English text collection for self-supervised pre-training of the BERT model. 

### 2. Composition (What are the instances? Do they represent specific demographics?)
- **Instances**: Raw, unlabelled English text extracted from two sources: BookCorpus and Wikipedia.
- **Demographics**: Not specified in the README. 

### 3. Collection Process (How was data acquired?)
The README states that the model was pretrained on “raw texts only, with no humans labeling them.” The data were collected from the publicly available BookCorpus and Wikipedia datasets.

### 4. Uses (What tasks is it suitable for?)
- **Pre-training**: Masked Language Modeling (MLM) and Next Sentence Prediction (NSP) objectives.
- **Fine-tuning**: Adaptable to text classification, named entity recognition, and question answering.

### 5. Limitations (What should users not do with it?)
Not specified in the README. Users should be aware that the corpus may contain copyrighted material and potential biases.
