import pdfplumber

def extract_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        if not pdf.pages:
            raise ValueError("PDF file contains no pages.")
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    if not text.strip():
        raise ValueError("No extractable text found in the PDF. It may be a scanned or image-based document.")
    return text