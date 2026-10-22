import os
import io
from typing import Dict, Any, Tuple
from pypdf import PdfReader


def read_from_keyboard() -> str:
    """
    Reads legal document text directly from user keyboard input.
    Accepts multiline input until the user enters 'END' on a new line or sends EOF.
    """
    print("\n" + "=" * 60)
    print("ENTER LEGAL DOCUMENT TEXT")
    print("(Paste or type your text below. When done, type 'END' on a new line and press Enter)")
    print("=" * 60)
    
    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
    except EOFError:
        pass
    
    return "\n".join(lines).strip()


def read_from_txt(file_path: str) -> str:
    """
    Reads legal document from a plain text (.txt) file with encoding fallback.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read().strip()
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"Unable to decode text file: {file_path}")


def read_from_pdf(file_source: Any) -> Tuple[str, int]:
    """
    Extracts text from a .pdf file (file path or file-like binary stream).
    Returns (extracted_text, num_pages).
    """
    if isinstance(file_source, str):
        if not os.path.exists(file_source):
            raise FileNotFoundError(f"PDF file not found: {file_source}")
        reader = PdfReader(file_source)
    elif hasattr(file_source, "read"):
        reader = PdfReader(file_source)
    else:
        raise ValueError("Invalid PDF file source provided.")

    extracted_pages = []
    total_pages = len(reader.pages)
    
    for page_idx, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        if page_text.strip():
            extracted_pages.append(page_text)
            
    full_text = "\n\n".join(extracted_pages).strip()
    return full_text, total_pages


def get_document_metrics(text: str, source_name: str = "Direct Input", page_count: int = 1) -> Dict[str, Any]:
    """
    Calculates metadata and metrics for the document (Q2).
    """
    lines = [line for line in text.splitlines() if line.strip()]
    words = text.split()
    chars = len(text)
    
    # Try to detect an initial title from the first non-empty line
    first_line = lines[0] if lines else "Untitled Document"
    title_candidate = first_line[:80].strip()
    
    return {
        "source": source_name,
        "title_candidate": title_candidate,
        "total_characters": chars,
        "total_words": len(words),
        "total_lines": len(lines),
        "total_pages": page_count,
        "estimated_reading_time_min": round(len(words) / 200, 1)
    }


def display_document_info(text: str, source_name: str = "Direct Input", page_count: int = 1, preview_length: int = 400) -> None:
    """
    Part A - Q2: Neatly displays document information and metadata.
    """
    metrics = get_document_metrics(text, source_name, page_count)
    
    print("\n" + "=" * 60)
    print("           LEGAL DOCUMENT INFORMATION (Part A - Q2)")
    print("=" * 60)
    print(f"Source         : {metrics['source']}")
    print(f"Detected Title : {metrics['title_candidate']}")
    print(f"Total Words    : {metrics['total_words']:,}")
    print(f"Total Chars    : {metrics['total_characters']:,}")
    print(f"Line Count     : {metrics['total_lines']}")
    if metrics['total_pages'] > 1:
        print(f"Page Count     : {metrics['total_pages']}")
    print(f"Reading Time   : ~{metrics['estimated_reading_time_min']} min")
    print("-" * 60)
    print("DOCUMENT PREVIEW:")
    print("-" * 60)
    
    preview = text[:preview_length].strip()
    print(preview)
    if len(text) > preview_length:
        print(f"\n... [Remaining {len(text) - preview_length:,} characters truncated in preview] ...")
    print("=" * 60 + "\n")
