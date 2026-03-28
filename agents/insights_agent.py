"""
agents/insights_agent.py
Advanced AI insights: action items, smart replies, intelligence scoring,
sentiment arc, auto-tagging, keyword extraction, and risk assessment.
"""
import re
from datetime import datetime
from collections import Counter


# ──────────────────────────── Action Items ────────────────────────────────

def extract_action_items(content):
    """Extract actionable tasks from document content using pattern matching."""
    action_patterns = [
        r'(?:please|kindly)\s+(?:ensure|make sure|note|confirm|review|send|submit|complete|schedule|approve|check|update|forward|reply|respond)[\s,]+([^.!?\n]{10,120})',
        r'(?:need[ s]* to|must|should|required to|have to)\s+([^.!?\n]{10,120})',
        r'(?:action (?:required|needed|item)|follow[\s-]up|todo|to-do)[:\s]+([^.!?\n]{5,120})',
        r'(?:deadline|due|by|before)\s+(?:is |:)?\s*([^.!?\n]{5,80})',
        r'(?:send|submit|review|complete|finish|prepare|schedule|confirm|approve|check|update)\s+(?:the|a|your|our|this|that|these|those)\s+([^.!?\n]{5,100})',
    ]

    action_items = []
    seen = set()

    for pattern in action_patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            item = match.group(0).strip()
            # Clean up the item
            item = re.sub(r'\s+', ' ', item)
            normalized = item.lower()[:60]
            if len(item) > 15 and normalized not in seen:
                seen.add(normalized)
                action_items.append(item[:150])

    # Also detect bullet/numbered list items
    for line in content.splitlines():
        stripped = line.strip()
        for pat in [r'^\s*[-•*·]\s+(.{10,120})$', r'^\s*\d+[.)]\s+(.{10,120})$']:
            m = re.match(pat, stripped)
            if m:
                item = m.group(1).strip()
                normalized = item.lower()[:60]
                if normalized not in seen:
                    seen.add(normalized)
                    action_items.append(f"• {item}")

    return action_items[:10]


# ──────────────────────────── Smart Reply Generator ───────────────────────

def generate_smart_reply(email_content, urgency="Normal", email_type="General"):
    """Generate contextual email reply templates based on email analysis."""
    subject_m = re.search(r'Subject:\s*(.*)', email_content, re.IGNORECASE)
    sender_m  = re.search(r'From:\s*([\w._%+\-]+@[\w.\-]+\.[A-Za-z]{2,})', email_content, re.IGNORECASE)

    subject = subject_m.group(1).strip() if subject_m else "your email"
    if sender_m:
        name_part = sender_m.group(1).split('@')[0]
        sender_name = re.sub(r'[._\-]', ' ', name_part).title()
    else:
        sender_name = "there"

    replies = []

    # Urgency-driven immediate response
    if urgency in ["Critical", "High"]:
        replies.append({
            "style": "⚡ Immediate Response",
            "template": f"""Subject: Re: {subject}

Dear {sender_name},

I have received your message and fully understand the urgency. I am prioritising this immediately and will provide a full update within the hour.

Please let me know if you need any clarification or interim assistance.

Best regards,
[Your Name]"""
        })

    # Type-specific templates
    if email_type == "Meeting Request":
        replies.append({
            "style": "✅ Accept Meeting",
            "template": f"""Subject: Re: {subject}

Dear {sender_name},

Thank you for reaching out. The proposed time works perfectly for me.

Please send a calendar invite at your convenience — I look forward to our discussion.

Best regards,
[Your Name]"""
        })
        replies.append({
            "style": "🔄 Reschedule Meeting",
            "template": f"""Subject: Re: {subject}

Dear {sender_name},

Thank you for your email. Unfortunately I have a prior commitment at the proposed time.

Could we reschedule to [Alternative Date/Time]? I am available on [Day] between [Time Range]. Please let me know if that works.

Best regards,
[Your Name]"""
        })

    if email_type == "Invoice/Billing":
        replies.append({
            "style": "💳 Payment Acknowledgment",
            "template": f"""Subject: Re: {subject}

Dear {sender_name},

Thank you for sending the invoice. I confirm receipt and will process payment by the due date.

Please do not hesitate to contact me if you have any further queries.

Best regards,
[Your Name]"""
        })

    if email_type == "Support Request":
        replies.append({
            "style": "🛠️ Support Acknowledgment",
            "template": f"""Subject: Re: {subject} — Ticket Received

Dear {sender_name},

Thank you for contacting our support team. We have logged your request and assigned it Ticket #[AUTO-ID].

Our team will investigate and respond within 24 business hours. If your issue is critical, please reply with 'URGENT' in the subject line.

Best regards,
Support Team"""
        })

    if email_type == "Sales Inquiry":
        replies.append({
            "style": "📋 Quote Response",
            "template": f"""Subject: Re: {subject} — Quotation

Dear {sender_name},

Thank you for your inquiry. We appreciate your interest in our services.

I have attached a detailed quotation for your review. Please feel free to reach out with any questions or to discuss customisation options.

We look forward to working with you.

Best regards,
[Your Name]
[Company Name]"""
        })

    # Universal fallback
    replies.append({
        "style": "📩 General Acknowledgment",
        "template": f"""Subject: Re: {subject}

Dear {sender_name},

Thank you for your email regarding "{subject}". I have carefully reviewed your message and will respond in full detail shortly.

Best regards,
[Your Name]"""
    })

    return replies


# ──────────────────────────── Intelligence Score ──────────────────────────

def calculate_document_score(content, format_detected, urgency=None,
                              email_result=None, json_result=None):
    """
    Calculate a 0-100 Document Intelligence Score across 5 dimensions:
    Richness, Structure, Urgency, Actionability, Completeness.
    """
    scores = {}

    # 1. Content Richness (0-20)
    wc = len(content.split())
    scores['richness'] = 20 if wc > 300 else (16 if wc > 150 else (11 if wc > 60 else 5))

    # 2. Structure Score (0-20)
    indicators = 0
    if re.search(r'Subject:', content, re.I): indicators += 1
    if re.search(r'From:', content, re.I):    indicators += 1
    if re.search(r'Date:', content, re.I):    indicators += 1
    if re.search(r'[\w._%+\-]+@[\w.\-]+\.[A-Za-z]{2,}', content): indicators += 1
    if content.strip().startswith('{') or content.strip().startswith('['): indicators += 3
    if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', content): indicators += 1
    if re.search(r'\$[\d,]+', content): indicators += 1
    scores['structure'] = min(20, indicators * 3)

    # 3. Urgency/Priority Score (0-20)
    urgency_map = {"Critical": 20, "High": 16, "Medium": 12, "Normal": 8, "Low": 4}
    scores['urgency'] = urgency_map.get(urgency, 8)

    # 4. Actionability Score (0-20)
    action_kws = ['please', 'urgently', 'required', 'deadline', 'action', 'must',
                  'submit', 'review', 'approve', 'confirm', 'complete', 'follow up']
    a_count = sum(1 for kw in action_kws if kw in content.lower())
    scores['actionability'] = min(20, a_count * 2 + (2 if extract_action_items(content) else 0))

    # 5. Completeness Score (0-20)
    completeness = 10
    if format_detected == "Email" and email_result:
        if email_result.get('sender'):      completeness += 2
        if email_result.get('subject'):     completeness += 2
        if email_result.get('date'):        completeness += 2
        if email_result.get('key_phrases'): completeness += 2
        if email_result.get('urgency') != 'Normal': completeness += 2
    elif format_detected == "JSON" and json_result:
        validation = json_result.get('validation', {})
        completeness += 10 if validation.get('is_valid') else -3
    elif format_detected == "PDF":
        completeness += 5
    scores['completeness'] = max(0, min(20, completeness))

    total = min(100, sum(scores.values()))
    return {
        "total": total,
        "breakdown": scores,
        "grade": "A" if total >= 85 else "B" if total >= 70 else "C" if total >= 55 else "D" if total >= 40 else "F",
        "rating": ("Excellent" if total >= 85 else "Good" if total >= 70 else
                   "Average" if total >= 55 else "Below Average" if total >= 40 else "Poor")
    }


# ──────────────────────────── Sentiment Arc ───────────────────────────────

POSITIVE_WORDS = set([
    'good', 'great', 'excellent', 'happy', 'pleased', 'satisfied', 'approve',
    'appreciate', 'thank', 'wonderful', 'perfect', 'success', 'helpful', 'agree',
    'love', 'fantastic', 'amazing', 'brilliant', 'outstanding', 'positive'
])
NEGATIVE_WORDS = set([
    'bad', 'terrible', 'awful', 'unhappy', 'disappointed', 'frustrated', 'issue',
    'problem', 'fail', 'wrong', 'error', 'concern', 'complaint', 'reject', 'deny',
    'poor', 'worst', 'horrible', 'unacceptable', 'negative', 'broken', 'delayed'
])

def analyze_sentiment_arc(content):
    """Return per-sentence sentiment scores for the document, ideal for line charts."""
    sentences = re.split(r'[.!?\n]+', content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 12]

    arc = []
    for i, sentence in enumerate(sentences[:15]):
        words = set(re.findall(r'\b\w+\b', sentence.lower()))
        pos = len(words & POSITIVE_WORDS)
        neg = len(words & NEGATIVE_WORDS)

        if pos > neg:
            score = min(1.0, round(0.4 + (pos - neg) * 0.25, 2))
            label = "Positive"
            color = "#10b981"
        elif neg > pos:
            score = max(-1.0, round(-0.4 - (neg - pos) * 0.25, 2))
            label = "Negative"
            color = "#ef4444"
        else:
            score = 0.0
            label = "Neutral"
            color = "#6b7280"

        arc.append({
            "position": i + 1,
            "text": (sentence[:90] + "…") if len(sentence) > 90 else sentence,
            "score": score,
            "sentiment": label,
            "color": color,
        })

    return arc


# ──────────────────────────── Smart Tags ──────────────────────────────────

TAG_PATTERNS = {
    "💰 Financial":      (["\\$[\\d,]+", "invoice", "payment", "billing", "amount", "revenue", "budget"], "#f59e0b"),
    "📅 Time-Sensitive": (["deadline", "due date", "asap", "urgent", "immediately", "expires", "by eod"], "#ef4444"),
    "🤝 Meeting":        (["meeting", "calendar", "schedule", "appointment", "discuss", "conference call"], "#10b981"),
    "📊 Data/JSON":      (["\\bjson\\b", "dataset", "records", "database", "schema", "api", "payload"], "#3b82f6"),
    "⚖️ Legal":          (["contract", "agreement", "terms", "compliance", "legal", "liability", "clause"], "#8b5cf6"),
    "🎯 Action Required":(["please", "required", "must", "action needed", "need to"], "#f97316"),
    "🔒 Confidential":   (["confidential", "private", "sensitive", "restricted", "do not share"], "#6b7280"),
    "📦 Order/Purchase": (["order", "purchase", "quantity", "product", "delivery", "sku", "shipment"], "#06b6d4"),
    "🧾 Report":         (["summary", "findings", "recommendation", "conclusion", "analysis", "results"], "#84cc16"),
    "🔧 Technical":      (["error", "bug", "fix", "server", "deploy", "code", "exception", "stack trace"], "#ec4899"),
}

def generate_smart_tags(content, format_detected, intent):
    """Auto-generate semantic tags from content with matching colors."""
    tags = []
    fmt_colors = {"Email": "#667eea", "JSON": "#764ba2", "PDF": "#f59e0b"}
    tags.append({"tag": format_detected, "color": fmt_colors.get(format_detected, "#6b7280")})

    if intent and intent not in ("Unknown", ""):
        clean_intent = re.sub(r'^(Likely |Possible )', '', intent)
        tags.append({"tag": clean_intent, "color": "#764ba2"})

    content_lower = content.lower()
    for tag_name, (patterns, color) in TAG_PATTERNS.items():
        if any(re.search(p, content_lower) for p in patterns):
            tags.append({"tag": tag_name, "color": color})

    return tags[:8]


# ──────────────────────────── Keyword Extractor ───────────────────────────

STOPWORDS = set([
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'shall', 'can', 'this', 'that', 'these',
    'those', 'i', 'we', 'you', 'he', 'she', 'it', 'they', 'from', 'as',
    'by', 'not', 'no', 'if', 'so', 'up', 'my', 'your', 'our', 'their',
    'me', 'us', 'him', 'her', 'its', 'am', 'all', 'also', 'dear',
])

def extract_keywords(content, top_n=20):
    """Extract top keywords by frequency (excluding stopwords)."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    counter = Counter(filtered)
    return counter.most_common(top_n)


# ──────────────────────────── Risk Assessment ─────────────────────────────

def assess_risk(content, format_detected, urgency=None):
    """
    Assess document risk level across four dimensions:
    Urgency Risk, Data Sensitivity Risk, Compliance Risk, Operational Risk.
    Returns overall level: Low / Medium / High / Critical.
    """
    risks = {}

    # Urgency Risk
    urgency_risk = {"Critical": 4, "High": 3, "Medium": 2, "Normal": 1, "Low": 0}
    risks["Urgency Risk"] = urgency_risk.get(urgency, 1)

    # Data Sensitivity Risk
    sensitivity_score = 0
    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', content):         sensitivity_score += 3  # SSN pattern
    if re.search(r'\b\d{16}\b', content):                     sensitivity_score += 3  # Credit card
    if re.search(r'password|secret|token|api[_\s]?key', content, re.I): sensitivity_score += 2
    if re.search(r'confidential|private|sensitive|restricted', content, re.I): sensitivity_score += 2
    if re.search(r'[\w._%+\-]+@[\w.\-]+\.[A-Za-z]{2,}', content): sensitivity_score += 1
    risks["Data Sensitivity"] = min(4, sensitivity_score)

    # Compliance Risk
    compliance_score = 0
    if re.search(r'gdpr|ccpa|hipaa|pci|sox|compliance|regulation|audit', content, re.I):
        compliance_score += 3
    if re.search(r'legal|liability|clause|contract|terms', content, re.I):
        compliance_score += 2
    risks["Compliance Risk"] = min(4, compliance_score)

    # Operational Risk
    ops_score = 0
    if re.search(r'server|outage|down|failure|incident|critical|production', content, re.I):
        ops_score += 3
    if re.search(r'breach|hack|attack|vulnerability|exploit', content, re.I):
        ops_score += 4
    if re.search(r'deadline|late|overdue|miss', content, re.I):
        ops_score += 2
    risks["Operational Risk"] = min(4, ops_score)

    total_risk = sum(risks.values())
    if total_risk >= 10:
        level, color = "🔴 Critical", "#dc2626"
    elif total_risk >= 6:
        level, color = "🟠 High", "#f97316"
    elif total_risk >= 3:
        level, color = "🟡 Medium", "#f59e0b"
    else:
        level, color = "🟢 Low", "#10b981"

    return {"risks": risks, "total": total_risk, "level": level, "color": color}
