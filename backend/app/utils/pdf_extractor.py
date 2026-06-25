import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_data: bytes) -> str | None:
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=file_data, filetype="pdf")
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()

        text = "\n".join(text_parts).strip()
        if len(text) < 20:
            return None
        return text

    except Exception as e:
        logger.warning("PDF text extraction failed: %s", e)
        return None
