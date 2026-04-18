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
    print("Enhanced Multi-Agent AI System")
    print("=" * 50)

    files = {
        "email": "samples/sample_email.txt",
        "json": "samples/sample_invoice.json",
        "pdf": "samples/Underwater_Optical_Wireless_Communication.pdf",
    }

    for key, path in files.items():
        print(f"\n[PROCESS] {path}")
        try:
            content = read_pdf(path) if key == "pdf" else load_file(path)

            doc_id = path
            fmt = detect_format(content)
            intent = detect_intent(content)

            print(f"[DETECT] Format: {fmt}")
            print(f"[DETECT] Intent: {intent}")

            context = {"format": fmt, "intent": intent}

            if fmt == "Email":
                email_result = process_email(content)
                context.update(email_result)
                print(
                    f"[EMAIL] {email_result.get('sender', 'N/A')} - "
                    f"{email_result.get('urgency', 'N/A')}"
                )
            elif fmt == "JSON":
                json_result = process_json(content)
                context.update(json_result)
                print(f"[JSON] {json_result.get('document_type', 'N/A')}")
            elif fmt == "PDF":
                try:
                    pdf_result = process_pdf(content)
                    context.update(pdf_result)
                    print(f"[PDF] {pdf_result.get('document_type', 'N/A')}")
                except Exception as e:
                    context["note"] = f"PDF processing error: {e}"
                    print(f"[WARN] PDF processing failed: {e}")
            else:
                context["note"] = "No specific agent assigned"
                print("[INFO] No specific agent assigned")

            saved_context = save_context(doc_id, context)
            print(f"[MEMORY] Saved at: {saved_context.get('saved_at', 'N/A')}")
        except Exception as e:
            print(f"[ERROR] Processing {path}: {e}")

    print("\n[DONE] Processing complete")
    print("=" * 50)

    from memory.shared_memory import get_analytics

    analytics = get_analytics()
    print(f"Total documents processed: {analytics['total_documents']}")
    print(f"Formats: {', '.join(analytics.get('formats', {}).keys())}")
    print(f"Intents: {', '.join(analytics.get('intents', {}).keys())}")


if __name__ == "__main__":
    main()
