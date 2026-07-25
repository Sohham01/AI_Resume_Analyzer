import re

CID_PATTERN = re.compile(r"\(cid:\d+\)")

def _sanitize(text: str) -> str:
    return CID_PATTERN.sub("", text).strip()

def _try_pymupdf(pdf_file) -> str | None:
    try:
        import pymupdf
        doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        pdf_file.seek(0)
        return text
    except Exception:
        pdf_file.seek(0)
        return None

def _try_pdfplumber(pdf_file) -> str:
    import pdfplumber
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        if not pdf.pages:
            raise ValueError("PDF file contains no pages.")
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text(pdf_file):
    text = _try_pymupdf(pdf_file)
    if text is None:
        text = _try_pdfplumber(pdf_file)

    text = _sanitize(text)

    if not text:
        raise ValueError(
            "No extractable text found in the PDF. "
            "It may be a scanned or image-based document."
        )
    return text