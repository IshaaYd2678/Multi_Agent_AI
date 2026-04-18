# utils/intent_detector.py
import os
from dotenv import load_dotenv

load_dotenv()

# Load the Hugging Face model (you can replace this with a more suitable model)
model_name = os.getenv("HF_INTENT_MODEL", "SkolkovoInstitute/roberta-intent-classification")

intent_classifier = None
_classifier_load_attempted = False


def _get_intent_classifier():
    global intent_classifier, _classifier_load_attempted

    if _classifier_load_attempted:
        return intent_classifier

    _classifier_load_attempted = True
    try:
        from transformers import pipeline
    except Exception:
        intent_classifier = None
        return None

    try:
        intent_classifier = pipeline("text-classification", model=model_name)
    except Exception:
        intent_classifier = None
    return intent_classifier

def detect_intent_llm(text):
    classifier = _get_intent_classifier()
    if not classifier:
        return "Unknown"
    
    try:
        results = classifier(text[:1000])
        return results[0]['label']  # Return the label (intent)
    except Exception:
        return "Unknown"
