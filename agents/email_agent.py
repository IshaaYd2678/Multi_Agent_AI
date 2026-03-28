import re
from datetime import datetime
import hashlib

def process_email(content):
    try:
        # Enhanced email parsing with multiple patterns
        sender_patterns = [
            r"From:\s*([\w._%+\-]+@[\w.\-]+\.[A-Za-z]{2,})",
            r"from:\s*([\w._%+\-]+@[\w.\-]+\.[A-Za-z]{2,})",
            r"sender:\s*([\w._%+\-]+@[\w.\-]+\.[A-Za-z]{2,})",
            r"<([\w._%+\-]+@[\w.\-]+\.[A-Za-z]{2,})>"
        ]
        
        subject_patterns = [
            r"Subject:\s*(.*)",
            r"subject:\s*(.*)",
            r"Re:\s*(.*)",
            r"Fwd:\s*(.*)"
        ]
        
        # Extract sender
        sender = None
        for pattern in sender_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                sender = match.group(1).strip()
                break
        
        if not sender:
            sender = "Unknown"
        
        # Extract subject
        subject = "No Subject"
        for pattern in subject_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                subject = match.group(1).strip()
                break
        
        # Enhanced urgency detection
        urgency_keywords = {
            "Critical": [r"\bcritical\b", r"\bemergency\b", r"\bcrisis\b"],
            "High": [r"\burgent\b", r"\basap\b", r"\bimmediate\b", r"\bpriority\b", r"\brushed\b"],
            "Medium": [r"\bsoon\b", r"\bquickly\b", r"\btimely\b"],
            "Low": [r"\bwhen possible\b", r"\bno rush\b", r"\bconvenience\b"]
        }
        
        urgency = "Normal"
        for level, keywords in urgency_keywords.items():
            for keyword in keywords:
                if re.search(keyword, content, re.IGNORECASE):
                    urgency = level
                    break
            if urgency != "Normal":
                break
        
        # Extract additional metadata
        date_match = re.search(r"Date:\s*(.*)", content, re.IGNORECASE)
        email_date = date_match.group(1).strip() if date_match else None
        
        # Count attachments
        attachment_count = len(re.findall(r"attachment|attached|file", content, re.IGNORECASE))
        
        # Detect email type
        email_type = detect_email_type(content)
        
        # Generate unique ID
        email_id = hashlib.md5(f"{sender}{subject}{email_date}".encode()).hexdigest()[:8]
        
        # Extract key phrases
        key_phrases = extract_key_phrases(content)
        
        return {
            "email_id": email_id,
            "sender": sender,
            "subject": subject,
            "urgency": urgency,
            "date": email_date,
            "type": email_type,
            "attachment_count": attachment_count,
            "key_phrases": key_phrases,
            "word_count": len(content.split()),
            "processed_at": datetime.now().isoformat()
        }

    except Exception as e:
        return {"error": str(e)}

def detect_email_type(content):
    """Detect the type of email based on content patterns"""
    content_lower = content.lower()
    
    type_patterns = {
        "Meeting Request": [r"meeting", r"schedule", r"calendar", r"appointment"],
        "Invoice/Billing": [r"invoice", r"bill", r"payment", r"amount due"],
        "Support Request": [r"help", r"support", r"issue", r"problem"],
        "Sales Inquiry": [r"quote", r"price", r"cost", r"purchase"],
        "Newsletter": [r"unsubscribe", r"newsletter", r"update"],
        "Notification": [r"notification", r"alert", r"reminder"]
    }
    
    for email_type, patterns in type_patterns.items():
        if any(re.search(pattern, content_lower) for pattern in patterns):
            return email_type
    
    return "General"

def extract_key_phrases(content):
    """Extract important phrases from email content"""
    # Remove email headers and signatures
    content = re.sub(r"From:.*?Subject:.*?\n", "", content, flags=re.DOTALL)
    content = re.sub(r"--.*", "", content, flags=re.DOTALL)
    
    # Extract sentences with important keywords
    important_keywords = [
        "deadline", "due date", "meeting", "call", "urgent", "important",
        "please", "request", "need", "require", "asap", "immediately"
    ]
    
    sentences = re.split(r'[.!?]+', content)
    key_phrases = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if any(keyword in sentence.lower() for keyword in important_keywords):
            if len(sentence) > 10 and len(sentence) < 200:  # Filter reasonable length
                key_phrases.append(sentence)
    
    return key_phrases[:3]  # Return top 3 key phrases
