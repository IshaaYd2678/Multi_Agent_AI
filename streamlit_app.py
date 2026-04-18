import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# Try to import plotly for charts
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(
    page_title="Multi-Agent AI System", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Advanced Multi-Agent AI Document Processing System"
    }
)

from agents.email_agent import process_email
from agents.json_agent import process_json
from classifier import classify_file
from agents.classifier_agent import detect_intent as detect_intent_advanced
from memory.shared_memory import get_analytics, search_contexts, memory_store_instance, save_context
from agents.insights_agent import (
    extract_action_items, generate_smart_reply, calculate_document_score,
    analyze_sentiment_arc, generate_smart_tags, extract_keywords, assess_risk
)
import os
import hashlib
import math

# Try to import PDF functionality
try:
    from utils.file_loader import read_pdf
    from agents.pdf_agent import process_pdf
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# ── Rich CSS styling ──────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 60%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1.5rem;
        letter-spacing: -1px;
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 14px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(102,126,234,0.35);
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); }

    .insight-banner {
        background: linear-gradient(135deg, #667eea18, #764ba218);
        border: 1px solid #667eea44;
        border-left: 4px solid #667eea;
        border-radius: 10px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 1.2rem;
    }

    .tag-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        margin: 3px;
        font-size: 0.82rem;
        font-weight: 500;
        color: white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }

    .risk-badge {
        font-size: 1.1rem;
        font-weight: 700;
        padding: 6px 18px;
        border-radius: 30px;
        display: inline-block;
    }

    .action-item {
        background: #f8f9ff;
        border-left: 3px solid #667eea;
        padding: 8px 14px;
        margin: 5px 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
    }

    .reply-box {
        background: #fafafe;
        border: 1px solid #e0e4f7;
        border-radius: 10px;
        padding: 1rem;
        font-family: monospace;
        font-size: 0.88rem;
        white-space: pre-wrap;
    }

    .score-ring {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    div[data-testid="stSidebarContent"] .stMetric {
        background: linear-gradient(135deg,#667eea18,#764ba218);
        border-radius: 10px;
        padding: 6px 10px;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='text-align:center; padding:6px 0 12px;'>
    <span style='font-size:2rem'>🤖</span><br>
    <span style='font-weight:700; font-size:1.1rem; background:linear-gradient(135deg,#667eea,#764ba2);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>AI Agent System</span>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.selectbox(
    "Navigate to:",
    ["📄 Document Processor", "🧠 AI Insights Engine",
     "📊 Analytics Dashboard", "🌐 Document Network",
     "🔍 Search & History", "⚙️ System Status"]
)

# Sidebar live stats
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Live Stats**")
_analytics_sidebar = get_analytics()
col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    st.metric("Total Docs", _analytics_sidebar['total_documents'])
with col_s2:
    st.metric("This Week", len(_analytics_sidebar.get('recent_activity', [])))
if _analytics_sidebar.get('formats'):
    top_fmt = max(_analytics_sidebar['formats'], key=_analytics_sidebar['formats'].get)
    st.sidebar.caption(f"Top format: **{top_fmt}**")
st.sidebar.markdown("---")

if page == "📄 Document Processor":
    st.markdown('<h1 class="main-header">🤖 Multi-Agent AI Processor</h1>', unsafe_allow_html=True)
    
    # File upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Upload Document")
        
        # Dynamic file types based on PDF support
        file_types = ["json", "txt"]
        if PDF_SUPPORT:
            file_types.insert(0, "pdf")
        else:
            st.warning("⚠️ PDF support not available. Install PyMuPDF for PDF processing.")
        
        uploaded_file = st.file_uploader(
            "Choose a file to process",
            type=file_types,
            help="Supported formats: PDF, JSON, Email (TXT)"
        )
    
    with col2:
        st.subheader("📝 Quick Stats")
        analytics = get_analytics()
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>{analytics['total_documents']}</h3>
            <p>Total Processed</p>
        </div>
        """, unsafe_allow_html=True)
        
        if analytics['recent_activity']:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{len(analytics['recent_activity'])}</h3>
                <p>Recent (7 days)</p>
            </div>
            """, unsafe_allow_html=True)

    # Manual text input option
    st.subheader("✍️ Or Enter Text Manually")
    manual_input = st.text_area(
        "Paste email content or JSON data",
        height=150,
        placeholder="Paste your content here..."
    )
    
    input_text = ""
    file_type = None
    
    # Process uploaded file
    if uploaded_file:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        with st.spinner("Reading file..."):
            if file_ext == ".pdf" and PDF_SUPPORT:
                file_type = "PDF"
                bytes_data = uploaded_file.read()
                try:
                    input_text = read_pdf(bytes_data)
                except ValueError as exc:
                    st.error(f"Could not read PDF: {exc}")
                    input_text = ""
                
            elif file_ext == ".pdf" and not PDF_SUPPORT:
                st.error("❌ PDF support not available. Please install PyMuPDF.")
                
            elif file_ext == ".json":
                file_type = "JSON"
                input_text = uploaded_file.read().decode("utf-8")
                
            elif file_ext == ".txt":
                file_type = "Email"
                input_text = uploaded_file.read().decode("utf-8")
    
    # Process manual input
    elif manual_input.strip():
        input_text = manual_input
        # Auto-detect type
        if input_text.strip().startswith('{'):
            file_type = "JSON"
        else:
            file_type = "Email"
    
    # Display and process content
    if input_text:
        st.subheader("📄 Document Content")
        
        # Show content preview
        with st.expander("View Content", expanded=False):
            st.code(input_text[:1000] + "..." if len(input_text) > 1000 else input_text)
        
        # Processing button
        if st.button("🔍 Process Document", type="primary"):
            with st.spinner("Processing document..."):
                
                # Classify document
                format_detected, intent = classify_file(input_text, file_type)
                
                # Use the advanced intent detector for better results
                advanced_intent = detect_intent_advanced(input_text)
                if intent == "Unknown" or intent.startswith("Possible "):
                    intent = advanced_intent
                
                # Display classification results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.success(f"**Format:** {format_detected}")
                with col2:
                    st.info(f"**Intent:** {intent}")
                with col3:
                    st.metric("Word Count", len(input_text.split()))

                # Smart Tags
                smart_tags = generate_smart_tags(input_text, format_detected, intent)
                if smart_tags:
                    tags_html = "".join([
                        f'<span class="tag-pill" style="background:{t["color"]}">{t["tag"]}</span>'
                        for t in smart_tags
                    ])
                    st.markdown(f'<div style="margin:8px 0 4px">{tags_html}</div>',
                                unsafe_allow_html=True)

                # Risk badge
                risk_info = assess_risk(input_text, format_detected,
                                        urgency=None)
                st.markdown(
                    f'<div style="margin:4px 0 12px">Risk: '
                    f'<span class="risk-badge" style="background:{risk_info["color"]}22;'
                    f'color:{risk_info["color"]};border:1px solid {risk_info["color"]}44">'
                    f'{risk_info["level"]}</span></div>',
                    unsafe_allow_html=True
                )

                # Generate a unique doc_id for this document
                doc_source = (uploaded_file.name if uploaded_file else "manual_input")
                doc_id = doc_source + "_" + hashlib.md5(input_text[:200].encode()).hexdigest()[:8]
                
                # Process with appropriate agent
                if format_detected == "Email":
                    st.subheader("📧 Email Analysis")
                    email_result = process_email(input_text)
                    
                    if "error" in email_result:
                        st.error(f"❌ {email_result['error']}")
                    else:
                        # Save to memory
                        context = {"format": format_detected, "intent": intent, **email_result}
                        save_context(doc_id, context)
                        
                        # Display email results in organized format
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📬 Email Details**")
                            st.write(f"**From:** {email_result.get('sender', 'N/A')}")
                            st.write(f"**Subject:** {email_result.get('subject', 'N/A')}")
                            st.write(f"**Urgency:** {email_result.get('urgency', 'N/A')}")
                            st.write(f"**Type:** {email_result.get('type', 'N/A')}")
                        
                        with col2:
                            st.markdown("**📊 Metadata**")
                            st.write(f"**Word Count:** {email_result.get('word_count', 'N/A')}")
                            st.write(f"**Attachments:** {email_result.get('attachment_count', 0)}")
                            st.write(f"**Email ID:** {email_result.get('email_id', 'N/A')}")
                        
                        # Key phrases
                        if email_result.get('key_phrases'):
                            st.markdown("**🔑 Key Phrases**")
                            for phrase in email_result['key_phrases']:
                                st.write(f"• {phrase}")
                        
                        st.success("✅ Saved to memory")

                        # Action items
                        action_items = extract_action_items(input_text)
                        if action_items:
                            with st.expander(f"🎯 Action Items Detected ({len(action_items)})"):
                                for ai_item in action_items:
                                    st.markdown(
                                        f'<div class="action-item">{ai_item}</div>',
                                        unsafe_allow_html=True)

                        # One-click reply button
                        urgency_val = email_result.get('urgency', 'Normal')
                        email_type_val = email_result.get('type', 'General')
                        replies = generate_smart_reply(input_text, urgency_val, email_type_val)
                        with st.expander(f"✍️ Smart Reply Generator ({len(replies)} templates)"):
                            tabs_r = st.tabs([r['style'] for r in replies])
                            for tab_r, reply_r in zip(tabs_r, replies):
                                with tab_r:
                                    st.code(reply_r['template'], language=None)
                
                elif format_detected == "JSON":
                    st.subheader("🔧 JSON Analysis")
                    json_result = process_json(input_text)
                    
                    if "error" in json_result:
                        st.error(f"❌ {json_result['error']}")
                    else:
                        # Save to memory
                        context = {"format": format_detected, "intent": intent, **json_result}
                        save_context(doc_id, context)
                        
                        # Display JSON analysis
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📋 Document Info**")
                            st.write(f"**Type:** {json_result.get('document_type', 'N/A')}")
                            
                            if json_result.get('extracted_info'):
                                st.markdown("**🔍 Extracted Information**")
                                for key, value in json_result['extracted_info'].items():
                                    st.write(f"**{key.title()}:** {value}")
                        
                        with col2:
                            st.markdown("**📊 Structure Analysis**")
                            structure = json_result.get('structure_analysis', {})
                            st.write(f"**Type:** {structure.get('type', 'N/A')}")
                            st.write(f"**Keys:** {structure.get('keys', 'N/A')}")
                            st.write(f"**Nested Objects:** {structure.get('nested_objects', 'N/A')}")
                            st.write(f"**Arrays:** {structure.get('arrays', 'N/A')}")
                        
                        # Validation results
                        validation = json_result.get('validation', {})
                        if validation:
                            if validation.get('is_valid'):
                                st.success("✅ JSON structure is valid")
                            else:
                                st.warning("⚠️ JSON validation issues found")
                            
                            if validation.get('issues'):
                                st.error("**Issues:**")
                                for issue in validation['issues']:
                                    st.write(f"• {issue}")
                            
                            if validation.get('warnings'):
                                st.warning("**Warnings:**")
                                for warning in validation['warnings']:
                                    st.write(f"• {warning}")
                        
                        # Raw JSON data
                        with st.expander("View Raw JSON Data"):
                            st.json(json_result['json_data'])
                        
                        st.success("✅ Saved to memory")

                        # Action items for JSON
                        action_items_j = extract_action_items(input_text)
                        if action_items_j:
                            with st.expander(f"🎯 Action Items ({len(action_items_j)})"):
                                for ai_j in action_items_j:
                                    st.markdown(f'<div class="action-item">{ai_j}</div>',
                                                unsafe_allow_html=True)

                        # Keyword frequency
                        kws = extract_keywords(input_text, top_n=10)
                        if kws and PLOTLY_AVAILABLE:
                            with st.expander("🔤 Top Keywords"):
                                kw_df = pd.DataFrame(kws, columns=['Keyword', 'Count'])
                                fig_kw = px.bar(kw_df, x='Keyword', y='Count',
                                                color='Count', color_continuous_scale='Purples')
                                fig_kw.update_layout(height=220, margin=dict(t=10,b=0,l=0,r=0),
                                                     showlegend=False)
                                st.plotly_chart(fig_kw, use_container_width=True)
                
                elif format_detected == "PDF" and PDF_SUPPORT:
                    st.subheader("📜 PDF Analysis")
                    pdf_result = process_pdf(input_text)
                    
                    if "error" in pdf_result:
                        st.error(f"❌ {pdf_result['error']}")
                    else:
                        # Save to memory
                        context = {"format": format_detected, "intent": intent, **pdf_result}
                        save_context(doc_id, context)
                        
                        # Display PDF analysis
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Document Type", pdf_result.get('document_type', 'N/A'))
                            st.metric("Word Count", pdf_result.get('word_count', 0))
                        
                        with col2:
                            st.metric("Estimated Pages", pdf_result.get('page_count', 0))
                            readability = pdf_result.get('readability', {})
                            st.metric("Readability", readability.get('level', 'N/A'))
                        
                        with col3:
                            structure = pdf_result.get('structure', {})
                            st.metric("Paragraphs", structure.get('paragraphs', 0))
                            st.metric("Headings", structure.get('headings', 0))
                        
                        # Summary
                        if pdf_result.get('summary'):
                            st.markdown("**📝 Summary**")
                            st.write(pdf_result['summary'])
                        
                        # Key information
                        if pdf_result.get('key_information'):
                            st.markdown("**🔑 Key Information**")
                            for key, value in pdf_result['key_information'].items():
                                if value:  # Only show non-empty values
                                    st.write(f"**{key.title()}:** {', '.join(value) if isinstance(value, list) else value}")
                        
                        # Metadata
                        metadata = pdf_result.get('metadata', {})
                        if any(metadata.values()):
                            with st.expander("View Metadata"):
                                for key, value in metadata.items():
                                    if value:
                                        st.write(f"**{key.title()}:** {', '.join(value) if isinstance(value, list) else value}")
                        
                        st.success("✅ Saved to memory")
                
                else:
                    # Save generic document to memory
                    context = {"format": format_detected, "intent": intent}
                    save_context(doc_id, context)
                    st.info("📄 Document processed but no specific agent assigned.")
                    st.write(f"Format: {format_detected}, Intent: {intent}")
    
    else:
        st.info("👆 Upload a file or paste content to begin processing.")
elif page == "📊 Analytics Dashboard":
    st.markdown('<h1 class="main-header">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    analytics = get_analytics()
    
    if analytics['total_documents'] == 0:
        st.info("📈 No documents processed yet. Process some documents to see analytics.")
    else:
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Documents", analytics['total_documents'])
        
        with col2:
            recent_count = len(analytics.get('recent_activity', []))
            st.metric("Recent (7 days)", recent_count)
        
        with col3:
            format_count = len(analytics.get('formats', {}))
            st.metric("Format Types", format_count)
        
        with col4:
            intent_count = len(analytics.get('intents', {}))
            st.metric("Intent Types", intent_count)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Document Formats")
            if analytics.get('formats'):
                formats_df = pd.DataFrame(
                    list(analytics['formats'].items()),
                    columns=['Format', 'Count']
                )
                if PLOTLY_AVAILABLE:
                    fig = px.pie(formats_df, values='Count', names='Format', 
                               title="Distribution of Document Formats")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(formats_df.set_index('Format'))
            else:
                st.info("No format data available")
        
        with col2:
            st.subheader("🎯 Intent Distribution")
            if analytics.get('intents'):
                intents_df = pd.DataFrame(
                    list(analytics['intents'].items()),
                    columns=['Intent', 'Count']
                )
                if PLOTLY_AVAILABLE:
                    fig = px.bar(intents_df, x='Intent', y='Count',
                               title="Document Intents")
                    fig.update_xaxes(tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(intents_df.set_index('Intent'))
            else:
                st.info("No intent data available")
        
        # Recent activity timeline
        st.subheader("📅 Recent Activity")
        recent_activity = analytics.get('recent_activity', [])
        
        if recent_activity:
            # Convert to DataFrame for better display
            df = pd.DataFrame(recent_activity)
            df['saved_at'] = pd.to_datetime(df['saved_at'])
            df = df.sort_values('saved_at', ascending=False)
            
            # Display as table
            st.dataframe(
                df[['doc_id', 'format', 'intent', 'saved_at']].head(10),
                use_container_width=True
            )
            
            # Activity over time chart
            if len(df) > 1:
                df['date'] = df['saved_at'].dt.date
                daily_counts = df.groupby('date').size().reset_index(name='count')
                
                if PLOTLY_AVAILABLE:
                    fig = px.line(daily_counts, x='date', y='count',
                                title="Daily Processing Activity")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.line_chart(daily_counts.set_index('date'))
        else:
            st.info("No recent activity to display")
        
        # Urgency levels (if available)
        if analytics.get('urgency_levels'):
            st.subheader("⚡ Urgency Levels")
            urgency_df = pd.DataFrame(
                list(analytics['urgency_levels'].items()),
                columns=['Urgency', 'Count']
            )
            
            # Color mapping for urgency
            color_map = {
                'Critical': '#ff4444',
                'High': '#ff8800',
                'Medium': '#ffbb00',
                'Normal': '#00bb00',
                'Low': '#0088bb'
            }
            
            if PLOTLY_AVAILABLE:
                fig = px.bar(urgency_df, x='Urgency', y='Count',
                           title="Email Urgency Distribution",
                           color='Urgency',
                           color_discrete_map=color_map)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(urgency_df.set_index('Urgency'))

# ══════════════════════════════════════════════════════════════════════════
# PAGE: 🧠 AI Insights Engine
# ══════════════════════════════════════════════════════════════════════════
elif page == "🧠 AI Insights Engine":
    st.markdown('<h1 class="main-header">🧠 AI Insights Engine</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-banner">
    <b>Deep Document Intelligence</b> — Paste any email, JSON, contract, or report
    to unlock a full AI analysis: intelligence score, sentiment arc, risk assessment,
    action items, keyword extraction, and one-click smart reply generation.
    </div>
    """, unsafe_allow_html=True)

    analysis_text = st.text_area(
        "Paste any document for deep analysis",
        height=200,
        placeholder="Paste an email, JSON, contract, report, or any text here…"
    )
    fmt_hint = st.selectbox("Document type hint (optional)",
                             ["Auto-detect", "Email", "JSON", "PDF / Report"])

    if analysis_text.strip() and st.button("🚀 Run Deep Analysis", type="primary"):
        with st.spinner("Running AI analysis…"):
            hint = None if fmt_hint == "Auto-detect" else fmt_hint.split('/')[0].strip()
            detected_fmt, base_intent = classify_file(analysis_text, hint)
            adv_intent = detect_intent_advanced(analysis_text)
            intent_ai = adv_intent if (base_intent in ("Unknown", "") or
                                        base_intent.startswith("Possible")) else base_intent

            email_res, json_res = None, None
            urgency_ai, etype_ai = "Normal", "General"
            if detected_fmt == "Email":
                email_res = process_email(analysis_text)
                if "error" in email_res:
                    email_res = None
                else:
                    urgency_ai = email_res.get('urgency', 'Normal')
                    etype_ai   = email_res.get('type', 'General')
            if detected_fmt == "JSON":
                json_res = process_json(analysis_text)
                if "error" in json_res: json_res = None

            doc_score    = calculate_document_score(analysis_text, detected_fmt, urgency_ai, email_res, json_res)
            action_items = extract_action_items(analysis_text)
            smart_tags   = generate_smart_tags(analysis_text, detected_fmt, intent_ai)
            sent_arc     = analyze_sentiment_arc(analysis_text)
            risk_info    = assess_risk(analysis_text, detected_fmt, urgency_ai)
            keywords     = extract_keywords(analysis_text, top_n=15)

        # ── Row 1: Score | Tags | Risk ──────────────────────────────────────
        c1, c2, c3 = st.columns([1.2, 2, 1])

        with c1:
            st.subheader("📊 Intelligence Score")
            if PLOTLY_AVAILABLE:
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=doc_score['total'],
                    number={'suffix': '/100', 'font': {'size': 28}},
                    title={'text': f"Grade {doc_score['grade']} · {doc_score['rating']}",
                           'font': {'size': 13}},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#667eea"},
                        'steps': [
                            {'range': [0, 40],  'color': '#fee2e2'},
                            {'range': [40, 70], 'color': '#fef3c7'},
                            {'range': [70, 100],'color': '#d1fae5'},
                        ],
                        'threshold': {'line': {'color': '#764ba2', 'width': 4},
                                      'thickness': 0.75, 'value': doc_score['total']}
                    }
                ))
                fig_gauge.update_layout(height=240, margin=dict(t=30, b=0, l=10, r=10))
                st.plotly_chart(fig_gauge, use_container_width=True)
            else:
                st.markdown(f'<div class="score-ring">{doc_score["total"]}</div>',
                            unsafe_allow_html=True)
                st.caption(f"Grade {doc_score['grade']} · {doc_score['rating']}")

            with st.expander("Score breakdown"):
                for dim, val in doc_score['breakdown'].items():
                    st.progress(val / 20, text=f"{dim.title()}: {val}/20")

        with c2:
            st.subheader("🏷️ Smart Tags")
            tags_html = "".join([
                f'<span class="tag-pill" style="background:{t["color"]}">{t["tag"]}</span>'
                for t in smart_tags
            ])
            st.markdown(f'<div style="margin-bottom:12px">{tags_html}</div>',
                        unsafe_allow_html=True)

            st.subheader("🎯 Action Items")
            if action_items:
                for ai_idx, ai_item in enumerate(action_items):
                    st.checkbox(ai_item[:120], key=f"ai_act_{ai_idx}")
            else:
                st.info("No specific action items detected in this document.")

        with c3:
            st.subheader("⚠️ Risk Level")
            st.markdown(
                f'<div style="text-align:center; margin:12px 0">'
                f'<div style="font-size:2.2rem;font-weight:800;color:{risk_info["color"]};">'
                f'{risk_info["level"]}</div></div>',
                unsafe_allow_html=True
            )
            st.caption(f"Risk score: {risk_info['total']}")
            for risk_name, risk_val in risk_info['risks'].items():
                rv_color = "#dc2626" if risk_val >= 3 else "#f59e0b" if risk_val >= 2 else "#10b981"
                st.markdown(
                    f'<div style="font-size:0.8rem; margin:2px 0">{risk_name}: '
                    f'<b style="color:{rv_color}">{risk_val}/4</b></div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # ── Row 2: Sentiment Arc | Keywords ────────────────────────────────
        ca, cb = st.columns([3, 2])

        with ca:
            st.subheader("📈 Sentiment Arc")
            if len(sent_arc) > 1 and PLOTLY_AVAILABLE:
                arc_df = pd.DataFrame(sent_arc)
                fig_arc = go.Figure()
                fig_arc.add_hrect(y0=0, y1=1.2,  fillcolor="#10b981", opacity=0.04, line_width=0)
                fig_arc.add_hrect(y0=-1.2, y1=0, fillcolor="#ef4444", opacity=0.04, line_width=0)
                fig_arc.add_hline(y=0, line_dash="dash", line_color="#aaa", opacity=0.6)
                fig_arc.add_trace(go.Scatter(
                    x=arc_df['position'], y=arc_df['score'],
                    mode='lines+markers',
                    line=dict(color='#667eea', width=2.5, shape='spline'),
                    marker=dict(color=arc_df['color'], size=10,
                                line=dict(width=2, color='white')),
                    text=arc_df['text'],
                    hovertemplate='<b>Sentence %{x}</b><br>%{y:.2f}<br><i>%{text}</i><extra></extra>'
                ))
                fig_arc.update_layout(
                    xaxis_title="Sentence", yaxis_title="Sentiment Score",
                    yaxis=dict(range=[-1.3, 1.3]),
                    height=300, margin=dict(t=10, b=40, l=40, r=10),
                    plot_bgcolor='rgba(248,249,252,1)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_arc, use_container_width=True)
            elif len(sent_arc) <= 1:
                st.info("Not enough sentences to plot sentiment arc (need ≥ 2).")
            else:
                st.info("Install plotly for rich sentiment visualization.")

        with cb:
            st.subheader("🔤 Top Keywords")
            if keywords and PLOTLY_AVAILABLE:
                kw_df = pd.DataFrame(keywords, columns=['Keyword', 'Count'])
                fig_kw = px.bar(kw_df.head(12), x='Count', y='Keyword',
                                orientation='h',
                                color='Count', color_continuous_scale='Purples')
                fig_kw.update_layout(height=300, margin=dict(t=10,b=10,l=10,r=10),
                                     yaxis=dict(autorange='reversed'),
                                     showlegend=False,
                                     plot_bgcolor='rgba(248,249,252,1)')
                st.plotly_chart(fig_kw, use_container_width=True)
            elif keywords:
                for kw, cnt in keywords[:10]:
                    st.write(f"**{kw}** — {cnt}")

        # ── Row 3: Smart Reply (emails only) ───────────────────────────────
        if detected_fmt == "Email" and email_res:
            st.markdown("---")
            st.subheader("✍️ Smart Reply Generator")
            st.caption(
                f"Tone-matched templates based on: urgency=**{urgency_ai}**, type=**{etype_ai}**")
            replies_ai = generate_smart_reply(analysis_text, urgency_ai, etype_ai)
            reply_tabs = st.tabs([r['style'] for r in replies_ai])
            for r_tab, r_data in zip(reply_tabs, replies_ai):
                with r_tab:
                    st.code(r_data['template'], language=None)

    else:
        st.info("👆 Paste any document above and click **Run Deep Analysis** to begin.")

elif page == "🔍 Search & History":
    st.markdown('<h1 class="main-header">🔍 Search & History</h1>', unsafe_allow_html=True)
    
    # Search functionality
    st.subheader("🔎 Search Documents")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search in processed documents",
            placeholder="Enter keywords to search..."
        )
    
    with col2:
        search_limit = st.selectbox("Results limit", [5, 10, 20, 50], index=1)
    
    if search_query:
        with st.spinner("Searching..."):
            results = search_contexts(search_query, limit=search_limit)
        
        if results:
            st.success(f"Found {len(results)} matching documents")
            
            for i, (doc_id, context, score) in enumerate(results):
                with st.expander(f"📄 {doc_id} (Relevance: {score})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Format:** {context.get('format', 'N/A')}")
                        st.write(f"**Intent:** {context.get('intent', 'N/A')}")
                        if 'sender' in context:
                            st.write(f"**Sender:** {context['sender']}")
                        if 'subject' in context:
                            st.write(f"**Subject:** {context['subject']}")
                    
                    with col2:
                        if 'saved_at' in context:
                            st.write(f"**Processed:** {context['saved_at']}")
                        if 'urgency' in context:
                            st.write(f"**Urgency:** {context['urgency']}")
                        if 'document_type' in context:
                            st.write(f"**Type:** {context['document_type']}")
                    
                    # Show extracted info if available
                    if 'extracted_info' in context and context['extracted_info']:
                        st.write("**Extracted Information:**")
                        for key, value in context['extracted_info'].items():
                            st.write(f"• **{key}:** {value}")
        else:
            st.info("No matching documents found")
    
    # Document history
    st.subheader("📚 Document History")
    
    # Get all documents from memory
    all_docs = []
    for doc_id, context in memory_store_instance.memory_store.items():
        all_docs.append({
            'Document ID': doc_id,
            'Format': context.get('format', 'N/A'),
            'Intent': context.get('intent', 'N/A'),
            'Processed At': context.get('saved_at', 'N/A'),
            'Urgency': context.get('urgency', 'N/A')
        })
    
    if all_docs:
        df = pd.DataFrame(all_docs)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            format_filter = st.selectbox(
                "Filter by Format",
                ['All'] + list(df['Format'].unique())
            )
        
        with col2:
            intent_filter = st.selectbox(
                "Filter by Intent", 
                ['All'] + list(df['Intent'].unique())
            )
        
        with col3:
            urgency_filter = st.selectbox(
                "Filter by Urgency",
                ['All'] + list(df['Urgency'].unique())
            )
        
        # Apply filters
        filtered_df = df.copy()
        if format_filter != 'All':
            filtered_df = filtered_df[filtered_df['Format'] == format_filter]
        if intent_filter != 'All':
            filtered_df = filtered_df[filtered_df['Intent'] == intent_filter]
        if urgency_filter != 'All':
            filtered_df = filtered_df[filtered_df['Urgency'] == urgency_filter]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"document_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No documents in history yet")

elif page == "⚙️ System Status":
    st.markdown('<h1 class="main-header">⚙️ System Status</h1>', unsafe_allow_html=True)
    
    # System information
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 System Components")
        
        # Check component status
        components = {
            "Email Agent": True,
            "JSON Agent": True,
            "PDF Agent": PDF_SUPPORT,
            "Classifier": True,
            "Memory System": True
        }
        
        for component, status in components.items():
            if status:
                st.success(f"✅ {component}")
            else:
                st.error(f"❌ {component}")
        
        # Memory statistics
        st.subheader("💾 Memory Statistics")
        analytics = get_analytics()
        
        st.write(f"**Total Documents:** {analytics['total_documents']}")
        st.write(f"**Memory Usage:** {len(str(memory_store_instance.memory_store))} characters")
        
        # Cleanup option
        if st.button("🧹 Clear Old Entries (30+ days)"):
            cleared = memory_store_instance.clear_old_entries(30)
            if cleared > 0:
                st.success(f"Cleared {cleared} old entries")
            else:
                st.info("No old entries to clear")
    
    with col2:
        st.subheader("📊 Performance Metrics")
        
        # Processing statistics
        if analytics['total_documents'] > 0:
            formats = analytics.get('formats', {})
            most_common_format = max(formats, key=formats.get) if formats else "N/A"
            
            intents = analytics.get('intents', {})
            most_common_intent = max(intents, key=intents.get) if intents else "N/A"
            
            st.metric("Most Common Format", most_common_format)
            st.metric("Most Common Intent", most_common_intent)
            
            # Recent activity
            recent_activity = analytics.get('recent_activity', [])
            if recent_activity:
                st.metric("Last Processed", recent_activity[0]['saved_at'][:19])
        else:
            st.info("No performance data available yet")
        
        # System health
        st.subheader("🏥 System Health")
        
        health_checks = {
            "Memory Store": len(memory_store_instance.memory_store) < 10000,  # Less than 10k docs
            "Recent Activity": len(analytics.get('recent_activity', [])) > 0,
            "Error Rate": True  # Placeholder - could track actual errors
        }
        
        for check, status in health_checks.items():
            if status:
                st.success(f"✅ {check}: Healthy")
            else:
                st.warning(f"⚠️ {check}: Needs attention")
    
    # Configuration
    st.subheader("⚙️ Configuration")
    
    with st.expander("View Current Configuration"):
        config = {
            "PDF Support": PDF_SUPPORT,
            "Memory Persistence": True,
            "Analytics Enabled": True,
            "Search Enabled": True,
            "Auto-cleanup": "30 days",
            "Max Memory Entries": "1000"
        }
        
        for key, value in config.items():
            st.write(f"**{key}:** {value}")
    
    # About section
    st.subheader("ℹ️ About")
    st.info("""
    **Multi-Agent AI Document Processing System v2.0**
    
    This enhanced system provides intelligent document processing with:
    - Advanced email analysis with urgency detection
    - Comprehensive JSON validation and structure analysis  
    - PDF content extraction and document type detection
    - Persistent memory with search capabilities
    - Real-time analytics and performance monitoring
    
    Built with Streamlit, OpenAI, and advanced NLP techniques.
    """)

# ══════════════════════════════════════════════════════════════════════════
# PAGE: 🌐 Document Intelligence Network
# ══════════════════════════════════════════════════════════════════════════
elif page == "🌐 Document Network":
    st.markdown('<h1 class="main-header">🌐 Document Intelligence Network</h1>',
                unsafe_allow_html=True)
    st.caption("Interactive map of all processed documents — nodes connected by shared format, intent & semantic similarity.")

    all_contexts = list(memory_store_instance.memory_store.items())
    analytics_net = get_analytics()

    if not all_contexts:
        st.info("📭 No documents in memory yet. Process some documents in the Document Processor first.")
    else:
        # ── Network Graph ─────────────────────────────────────────────────
        st.subheader("🕸️ Document Relationship Network")
        if PLOTLY_AVAILABLE:
            n = len(all_contexts)
            nodes_net = []
            for i, (doc_id, ctx) in enumerate(all_contexts):
                angle = 2 * math.pi * i / n
                r = 1.8
                # Slight jitter so overlapping docs spread out
                jx = ((hash(doc_id) % 200) - 100) / 800
                jy = ((hash(doc_id[::-1]) % 200) - 100) / 800
                fmt  = ctx.get('format', 'Unknown')
                intent_n  = ctx.get('intent', 'Unknown')
                urgency_n = ctx.get('urgency', 'N/A')
                saved_n   = ctx.get('saved_at', 'N/A')[:19]
                color_map_n = {'Email': '#667eea', 'JSON': '#764ba2',
                               'PDF': '#f59e0b', 'Unknown': '#6b7280'}
                nodes_net.append({
                    'id': doc_id, 'x': r * math.cos(angle) + jx,
                    'y': r * math.sin(angle) + jy,
                    'fmt': fmt, 'intent': intent_n,
                    'urgency': urgency_n, 'saved': saved_n,
                    'color': color_map_n.get(fmt, '#6b7280'),
                    'label': doc_id[:18] + '…' if len(doc_id) > 18 else doc_id
                })

            fig_net = go.Figure()

            # Edges
            for i in range(len(nodes_net)):
                for j in range(i + 1, len(nodes_net)):
                    shared = 0
                    if nodes_net[i]['fmt'] == nodes_net[j]['fmt']:   shared += 1
                    wi = set(nodes_net[i]['intent'].lower().split())
                    wj = set(nodes_net[j]['intent'].lower().split())
                    overlap = wi & wj - {'a','the','to','of','unknown','likely','possible'}
                    if overlap: shared += 1
                    if shared:
                        fig_net.add_trace(go.Scatter(
                            x=[nodes_net[i]['x'], nodes_net[j]['x'], None],
                            y=[nodes_net[i]['y'], nodes_net[j]['y'], None],
                            mode='lines', hoverinfo='none',
                            line=dict(width=shared + 0.5, color='#c4c9f0'),
                            showlegend=False
                        ))

            # Nodes
            for nd in nodes_net:
                fig_net.add_trace(go.Scatter(
                    x=[nd['x']], y=[nd['y']],
                    mode='markers+text',
                    marker=dict(size=34, color=nd['color'],
                                line=dict(width=3, color='white'),
                                opacity=0.9),
                    text=[nd['label']], textposition='bottom center',
                    textfont=dict(size=8, color='#333'),
                    hovertemplate=(
                        f"<b>{nd['id']}</b><br>"
                        f"Format: {nd['fmt']}<br>"
                        f"Intent: {nd['intent']}<br>"
                        f"Urgency: {nd['urgency']}<br>"
                        f"Processed: {nd['saved']}"
                        "<extra></extra>"
                    ),
                    showlegend=False
                ))

            # Legend
            for lbl, clr in [('Email','#667eea'),('JSON','#764ba2'),
                              ('PDF','#f59e0b'),('Other','#6b7280')]:
                fig_net.add_trace(go.Scatter(
                    x=[None], y=[None], mode='markers',
                    marker=dict(size=12, color=clr), name=lbl
                ))

            fig_net.update_layout(
                showlegend=True, hovermode='closest', height=520,
                margin=dict(b=20, l=5, r=5, t=10),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='rgba(248,249,252,1)',
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation='h', yanchor='bottom', y=1.02,
                            xanchor='right', x=1)
            )
            st.plotly_chart(fig_net, use_container_width=True)
        else:
            st.warning("Install plotly for the network visualization.")

        st.markdown("---")

        # ── Treemap | Sunburst | Timeline ─────────────────────────────────
        c_t1, c_t2, c_t3 = st.columns(3)

        with c_t1:
            st.subheader("📂 Format Map")
            fmts = analytics_net.get('formats', {})
            if fmts and PLOTLY_AVAILABLE:
                fig_tree = px.treemap(
                    names=list(fmts.keys()),
                    parents=["" for _ in fmts],
                    values=list(fmts.values()),
                    color=list(fmts.values()),
                    color_continuous_scale='Purples',
                )
                fig_tree.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0))
                st.plotly_chart(fig_tree, use_container_width=True)
            elif fmts:
                for k, v in fmts.items(): st.write(f"**{k}**: {v}")

        with c_t2:
            st.subheader("🎯 Intent Sunburst")
            intents_net = analytics_net.get('intents', {})
            if intents_net and PLOTLY_AVAILABLE:
                fig_sun = px.sunburst(
                    names=['All Intents'] + list(intents_net.keys()),
                    parents=[''] + ['All Intents'] * len(intents_net),
                    values=[sum(intents_net.values())] + list(intents_net.values()),
                    color_discrete_sequence=px.colors.sequential.Purples_r
                )
                fig_sun.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0))
                st.plotly_chart(fig_sun, use_container_width=True)
            elif intents_net:
                for k, v in intents_net.items(): st.write(f"**{k}**: {v}")

        with c_t3:
            st.subheader("⚡ Urgency Spread")
            urgencies_net = analytics_net.get('urgency_levels', {})
            if urgencies_net and PLOTLY_AVAILABLE:
                u_colors = {'Critical':'#dc2626','High':'#f97316',
                            'Medium':'#f59e0b','Normal':'#10b981','Low':'#6b7280'}
                urg_df = pd.DataFrame(list(urgencies_net.items()),
                                      columns=['Urgency', 'Count'])
                fig_urg = px.bar(urg_df, x='Urgency', y='Count',
                                 color='Urgency',
                                 color_discrete_map=u_colors)
                fig_urg.update_layout(height=280, margin=dict(t=10, b=0, l=0, r=0),
                                      showlegend=False)
                st.plotly_chart(fig_urg, use_container_width=True)
            else:
                st.info("Process more documents to see urgency distribution.")

        # ── Full document details table ────────────────────────────────────
        st.markdown("---")
        st.subheader("📋 All Documents Detail")
        rows = []
        for doc_id, ctx in all_contexts:
            rows.append({
                'Document ID': doc_id,
                'Format':  ctx.get('format', '—'),
                'Intent':  ctx.get('intent', '—'),
                'Urgency': ctx.get('urgency', '—'),
                'Saved At': ctx.get('saved_at', '—')[:19],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════
# Footer
# ══════════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.85rem; padding:4px 0;'>"
    "🤖 Multi-Agent AI System &nbsp;·&nbsp; AI Insights Engine &nbsp;·&nbsp; Document Intelligence Network"
    "</div>",
    unsafe_allow_html=True
)
