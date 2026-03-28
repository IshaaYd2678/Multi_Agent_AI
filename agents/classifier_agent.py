import re
from collections import Counter
import hashlib
from datetime import datetime

def clean_text(text):
    """Enhanced text cleaning with better preprocessing"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove email headers and signatures
    text = re.sub(r'from:.*?subject:.*?\n', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'--.*', '', text, flags=re.DOTALL)
    text = re.sub(r'sent from my.*', '', text, flags=re.IGNORECASE)
    
    # Remove URLs and email addresses
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters but keep important punctuation
    text = re.sub(r'[^\w\s.!?,-]', ' ', text)
    
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove signature lines
    text = re.sub(r'[-_*]{3,}', '', text)
    
    return text.strip()

def detect_format(content):
    """Enhanced format detection with confidence scoring"""
    content_lower = content.lower().strip()
    
    # Email detection patterns
    email_patterns = [
        r"from:\s*.*@",
        r"to:\s*.*@",
        r"subject:\s*",
        r"date:\s*",
        r"reply-to:",
        r"cc:\s*",
        r"bcc:\s*"
    ]
    
    # JSON detection
    json_indicators = [
        content.strip().startswith('{') and content.strip().endswith('}'),
        content.strip().startswith('[') and content.strip().endswith(']'),
        '"' in content and ':' in content
    ]
    
    # PDF text indicators
    pdf_indicators = [
        len(content.split('\n')) > 20,  # Many lines
        re.search(r'\f', content),  # Form feed characters
        re.search(r'page \d+ of \d+', content_lower)
    ]
    
    # Calculate confidence scores
    email_score = sum(1 for pattern in email_patterns if re.search(pattern, content_lower))
    json_score = sum(1 for indicator in json_indicators if indicator)
    pdf_score = sum(1 for indicator in pdf_indicators if indicator)
    
    # Determine format with confidence
    if email_score >= 2:
        return "Email"
    elif json_score >= 2:
        return "JSON"
    elif pdf_score >= 1:
        return "PDF"
    elif "invoice" in content_lower or "billing" in content_lower:
        return "Invoice"
    else:
        return "Unknown"

def detect_intent(content):
    """Enhanced intent detection with weighted scoring and context analysis"""
    content = clean_text(content)
    
    # Enhanced keyword groups with weights
    intent_keywords = {
        "Invoice": {
            "high": ["invoice", "billing", "payment due", "amount due", "total amount"],
            "medium": ["payment", "bill", "charge", "fee", "cost"],
            "low": ["tax", "receipt", "transaction"]
        },
        "RFQ": {
            "high": ["request for quote", "rfq", "quotation", "price quote"],
            "medium": ["pricing", "cost estimate", "quote", "proposal"],
            "low": ["budget", "estimate", "rates"]
        },
        "Complaint": {
            "high": ["complaint", "dissatisfied", "poor service", "not working"],
            "medium": ["issue", "problem", "damaged", "defective"],
            "low": ["concern", "disappointed", "unhappy"]
        },
        "Support": {
            "high": ["help needed", "support request", "technical issue"],
            "medium": ["help", "support", "assistance", "guidance"],
            "low": ["question", "inquiry", "how to"]
        },
        "Meeting": {
            "high": ["meeting request", "schedule meeting", "calendar invite"],
            "medium": ["meeting", "appointment", "call", "conference"],
            "low": ["discuss", "talk", "catch up"]
        },
        "Urgent": {
            "high": ["urgent", "emergency", "critical", "asap"],
            "medium": ["priority", "immediate", "rush"],
            "low": ["soon", "quickly", "timely"]
        }
    }
    
    # Calculate weighted scores
    scores = {}
    for intent, weight_groups in intent_keywords.items():
        score = 0
        for weight, keywords in weight_groups.items():
            multiplier = {"high": 3, "medium": 2, "low": 1}[weight]
            for keyword in keywords:
                matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', content))
                score += matches * multiplier
        scores[intent] = score
    
    # Context analysis
    context_boost = analyze_context(content)
    for intent, boost in context_boost.items():
        if intent in scores:
            scores[intent] += boost
    
    # Find top intent
    if not scores or max(scores.values()) == 0:
        return "Unknown"
    
    top_intent = max(scores, key=scores.get)
    confidence = scores[top_intent]
    
    # Apply confidence thresholds
    if confidence >= 5:
        return top_intent
    elif confidence >= 2:
        return f"Likely {top_intent}"
    elif confidence >= 1:
        return f"Possible {top_intent}"
    else:
        return "Unknown"

def analyze_context(content):
    """Analyze context for additional intent clues"""
    context_boost = {}
    
    # Time-sensitive language
    if re.search(r'\b(deadline|due date|expires|urgent|asap)\b', content):
        context_boost["Urgent"] = 2
    
    # Financial language
    if re.search(r'\$|€|£|\d+\.\d{2}|payment|invoice|bill', content):
        context_boost["Invoice"] = 1
    
    # Question patterns
    if re.search(r'\?|how to|can you|could you|would you', content):
        context_boost["Support"] = 1
    
    # Meeting language
    if re.search(r'\b(tomorrow|next week|schedule|calendar|available)\b', content):
        context_boost["Meeting"] = 1
    
    return context_boost

def extract_entities(content):
    """Extract named entities from content"""
    entities = {
        "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content),
        "phones": re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content),
        "dates": re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', content),
        "amounts": re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', content),
        "urls": re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
    }
    
    # Remove empty lists
    return {k: v for k, v in entities.items() if v}

def generate_content_hash(content):
    """Generate a unique hash for content deduplication"""
    cleaned = clean_text(content)
    return hashlib.md5(cleaned.encode()).hexdigest()[:12]

def analyze_sentiment(content):
    """Basic sentiment analysis using keyword matching"""
    positive_words = ["good", "great", "excellent", "satisfied", "happy", "pleased", "thank"]
    negative_words = ["bad", "terrible", "awful", "dissatisfied", "angry", "frustrated", "complaint"]
    
    content_lower = content.lower()
    positive_count = sum(1 for word in positive_words if word in content_lower)
    negative_count = sum(1 for word in negative_words if word in content_lower)
    
    if positive_count > negative_count:
        return "Positive"
    elif negative_count > positive_count:
        return "Negative"
    else:
        return "Neutral"
