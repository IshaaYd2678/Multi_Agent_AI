from pathlib import Path

import fitz  # PyMuPDF


def read_pdf(source):
    """Extract text from a PDF path or uploaded PDF bytes."""
    text = ""

    try:
        if isinstance(source, (bytes, bytearray)):
            doc = fitz.open(stream=source, filetype="pdf")
        else:
            doc = fitz.open(Path(source))

        with doc:
            for page in doc:
                text += page.get_text()
    except Exception as exc:
        raise ValueError(f"Unable to read PDF: {exc}") from exc

    return text
