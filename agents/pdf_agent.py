import re
from datetime import datetime

def process_pdf(content):
    """Enhanced PDF processing with text analysis and structure detection"""
    try:
        cleaned_content = clean_pdf_text(content)
        structure = analyze_document_structure(cleaned_content)
        metadata = extract_pdf_metadata(cleaned_content)
        doc_type = detect_pdf_document_type(cleaned_content)
        key_info = extract_key_information(cleaned_content, doc_type)
        readability = analyze_readability(cleaned_content)
        summary = generate_summary(cleaned_content)
        
        return {
            "document_type": doc_type,
            "structure": structure,
            "metadata": metadata,
            "key_information": key_info,
            "readability": readability,
            "summary": summary,
            "word_count": len(cleaned_content.split()),
            "page_count": estimate_page_count(content),
            "processed_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"PDF processing error: {e}"}

def clean_pdf_text(content):
    """Clean PDF extracted text"""
    content = content.replace('\f', '\n')
    content = re.sub(r'([a-z])([A-Z])', r'\1 \2', content)
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'^\s*\d+\s*$', '', content, flags=re.MULTILINE)
    return content.strip()

def analyze_document_structure(content):
    """Analyze the structure of the PDF document"""
    lines = content.split('\n')
    structure = {
        "total_lines": len(lines),
        "paragraphs": len([line for line in lines if line.strip() and not line.strip().isdigit()]),
        "headings": 0,
        "lists": 0,
        "tables": 0
    }
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.isupper() and len(line) < 100:
            structure["headings"] += 1
        if re.match(r'^\s*[-•*]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
            structure["lists"] += 1
        if len(re.findall(r'\t|\s{3,}', line)) >= 2:
            structure["tables"] += 1
    
    return structure

def extract_pdf_metadata(content):
    """Extract metadata from PDF content"""
    metadata = {}
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
    ]
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, content, re.IGNORECASE))
    metadata["dates_found"] = list(set(dates))[:5]
    metadata["emails"] = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
    metadata["phones"] = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)
    metadata["amounts"] = re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', content)
    return metadata

def detect_pdf_document_type(content):
    """Detect the type of PDF document"""
    content_lower = content.lower()
    type_indicators = {
        "Invoice": ["invoice", "bill", "payment due", "amount due", "total"],
        "Contract": ["agreement", "contract", "terms and conditions", "party"],
        "Report": ["executive summary", "findings", "conclusion", "analysis", "report"],
        "Manual": ["instructions", "manual", "guide", "how to", "step by step"],
        "Resume": ["experience", "education", "skills", "resume", "curriculum vitae"],
        "Legal": ["legal", "court", "plaintiff", "defendant", "jurisdiction"],
        "Financial": ["financial", "balance sheet", "income statement", "profit", "loss"],
        "Academic": ["abstract", "introduction", "methodology", "references", "bibliography"]
    }
    
    scores = {}
    for doc_type, keywords in type_indicators.items():
        score = sum(1 for keyword in keywords if keyword in content_lower)
        if score > 0:
            scores[doc_type] = score
    
    return max(scores, key=scores.get) if scores else "General Document"

def extract_key_information(content, doc_type):
    """Extract key information based on document type"""
    info = {}
    if doc_type == "Invoice":
        info.update({
            "invoice_numbers": re.findall(r'invoice\s*#?\s*(\w+)', content, re.IGNORECASE),
            "amounts": re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', content),
            "due_dates": re.findall(r'due\s+(?:date\s*:?\s*)?(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', content, re.IGNORECASE)
        })
    elif doc_type == "Resume":
        info.update({
            "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content),
            "phones": re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)
        })
    return {k: v for k, v in info.items() if v}

def analyze_readability(content):
    """Analyze document readability"""
    words = content.split()
    sentences = re.split(r'[.!?]+', content)
    
    if not words or not sentences:
        return {"error": "Insufficient content for analysis"}
    
    avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
    avg_chars_per_word = sum(len(word) for word in words) / len(words) if words else 0
    readability_score = (avg_words_per_sentence * 1.015) + (avg_chars_per_word * 84.6) - 206.835
    
    if readability_score < 50:
        level = "Easy"
    elif readability_score < 70:
        level = "Standard"
    else:
        level = "Difficult"
    
    return {
        "score": round(readability_score, 2),
        "level": level,
        "avg_words_per_sentence": round(avg_words_per_sentence, 1),
        "avg_chars_per_word": round(avg_chars_per_word, 1)
    }

def generate_summary(content):
    """Generate a simple extractive summary"""
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if len(sentences) <= 3:
        return " ".join(sentences)
    
    return " ".join(sentences[:3])

def estimate_page_count(content):
    """Estimate page count based on content length"""
    word_count = len(content.split())
    return max(1, round(word_count / 250))