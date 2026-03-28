from agents.classifier_agent import detect_format, detect_intent
from agents.email_agent import process_email
from agents.json_agent import process_json
from agents.pdf_agent import process_pdf
from memory.shared_memory import save_context
from utils.file_loader import read_pdf

def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    print("🚀 Enhanced Multi-Agent AI System")
    print("=" * 50)
    
    # Define sample files to process
    files = {
        "email": "samples/sample_email.txt",
        "json": "samples/sample_invoice.json",
        "pdf": "samples/sample_complaint.pdf",
    }

    for key, path in files.items():
        print(f"\n📂 Processing {path}")
        try:
            content = read_pdf(path) if key == "pdf" else load_file(path)

            doc_id = path
            fmt = detect_format(content)
            intent = detect_intent(content)

            print(f"🔍 Detected Format: {fmt}")
            print(f"🎯 Detected Intent: {intent}")

            context = {"format": fmt, "intent": intent}

            if fmt == "Email":
                email_result = process_email(content)
                context.update(email_result)
                print(f"📧 Email processed: {email_result.get('sender', 'N/A')} - {email_result.get('urgency', 'N/A')}")
                
            elif fmt == "JSON":
                json_result = process_json(content)
                context.update(json_result)
                print(f"🔧 JSON processed: {json_result.get('document_type', 'N/A')}")
                
            elif fmt == "PDF":
                try:
                    pdf_result = process_pdf(content)
                    context.update(pdf_result)
                    print(f"📜 PDF processed: {pdf_result.get('document_type', 'N/A')}")
                except Exception as e:
                    context["note"] = f"PDF processing error: {e}"
                    print(f"⚠️ PDF processing failed: {e}")
            else:
                context["note"] = "No specific agent assigned"
                print("ℹ️ No specific agent assigned")

            # Save to enhanced memory system
            saved_context = save_context(doc_id, context)
            print(f"🧠 Saved to memory with timestamp: {saved_context.get('saved_at', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error processing {path}: {e}")
    
    # Display analytics
    print(f"\n📊 Processing Complete!")
    print("=" * 50)
    
    from memory.shared_memory import get_analytics
    analytics = get_analytics()
    
    print(f"Total documents processed: {analytics['total_documents']}")
    print(f"Formats: {', '.join(analytics.get('formats', {}).keys())}")
    print(f"Intents: {', '.join(analytics.get('intents', {}).keys())}")

if __name__ == "__main__":
    main()
