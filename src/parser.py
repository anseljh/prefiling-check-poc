import os
from typing import Optional
import docx
from liteparse import LiteParse

def extract_text(filepath: str) -> str:
    """
    Extract text from a PDF or DOCX file.
    Saves the extracted text to a temporary .txt file alongside it, and returns the string.
    """
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    text = ""
    
    if ext == ".docx":
        text = _extract_from_docx(filepath)
    elif ext == ".pdf":
        text = _extract_from_pdf(filepath)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
        
    # Save the extracted text to disk as required by step 1
    output_txt = f"{filepath}.extracted.txt"
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(text)
        
    return text

def _extract_from_docx(filepath: str) -> str:
    doc = docx.Document(filepath)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)

def _extract_from_pdf(filepath: str) -> str:
    parser = LiteParse()
    # LiteParse shells out to the npm liteparse CLI
    try:
        result = parser.parse(filepath)
        if hasattr(result, "text"):
            return result.text
        elif hasattr(result, "pages"):
            return "\n\n".join(getattr(page, "text", str(page)) for page in result.pages)
        else:
            return str(result)
    except Exception as e:
        print(f"Error parsing PDF with LiteParse: {e}")
        return ""
