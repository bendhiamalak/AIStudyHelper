import pdfplumber
import os

def extract_text(path_or_file):
    text = []
    with pdfplumber.open(path_or_file) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)