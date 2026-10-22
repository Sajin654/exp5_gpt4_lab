import re
import unicodedata
from typing import List, Dict, Any, Tuple


def remove_unwanted_characters(text: str) -> str:
    """
    Removes unwanted control characters, non-printable characters,
    and obscure Unicode artifacts while preserving standard newlines and tabs.
    """
    if not text:
        return ""
    # Remove control characters except \n, \r, \t
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    # Remove zero-width characters (ZWSP, ZWNJ, ZWJ, BOM)
    cleaned = re.sub(r'[\u200B-\u200D\uFEFF]', '', cleaned)
    return cleaned


def remove_unnecessary_spaces(text: str) -> str:
    """
    Removes excess spaces, tabs, and trims redundant blank lines.
    - Replaces multiple spaces or tabs on a line with a single space.
    - Strips leading/trailing whitespace per line.
    - Reduces 3+ consecutive newlines down to a standard double newline.
    """
    if not text:
        return ""
    # Process line by line
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.splitlines()]
    joined = "\n".join(lines)
    # Reduce consecutive newlines to maximum 2
    joined = re.sub(r'\n{3,}', '\n\n', joined)
    return joined.strip()


def normalize_text(text: str) -> str:
    """
    Normalizes typography and symbols commonly found in legal documents:
    - Smart quotes (single and double) to straight ASCII quotes
    - En-dashes and em-dashes to standard hyphens
    - Unicode normalization (NFKC)
    - Standardizes bullet points
    """
    if not text:
        return ""
    
    # Unicode NFKC normalization
    normalized = unicodedata.normalize('NFKC', text)
    
    # Normalize quotes
    normalized = re.sub(r'[“”„«»]', '"', normalized)
    normalized = re.sub(r"[‘’`´]", "'", normalized)
    
    # Normalize dashes
    normalized = re.sub(r'[–—―]', '-', normalized)
    
    # Normalize bullet points to clean dash or bullet
    normalized = re.sub(r'^[ \t]*[•*▪►]\s*', '- ', normalized, flags=re.MULTILINE)
    
    return normalized


# Common legal document section header patterns
LEGAL_SECTION_PATTERNS = [
    (r'(?i)\b(contract\s+title|agreement\s+title|title)\b', 'Document Title'),
    (r'(?i)\b(parties|parties\s+involved|by\s+and\s+between)\b', 'Parties'),
    (r'(?i)\b(recitals|background|preamble|witnesseth)\b', 'Recitals / Background'),
    (r'(?i)\b(purpose|scope\s+of\s+(work|services)|objectives?)\b', 'Purpose & Scope'),
    (r'(?i)\b(obligations?|responsibilities|covenants|duties)\b', 'Obligations'),
    (r'(?i)\b(payment|compensation|fees?|billing|remuneration)\b', 'Payment Terms'),
    (r'(?i)\b(term|duration|period\s+of\s+agreement|commencement)\b', 'Duration & Term'),
    (r'(?i)\b(termination|cancellation|severability)\b', 'Termination Conditions'),
    (r'(?i)\b(confidentiality|non-disclosure|proprietary\s+information)\b', 'Confidentiality'),
    (r'(?i)\b(intellectual\s+property|ip\s+rights|ownership\s+of\s+work)\b', 'Intellectual Property'),
    (r'(?i)\b(liability|indemnification|warranty|disclaimer)\b', 'Liability & Warranties'),
    (r'(?i)\b(dispute\s+resolution|arbitration|governing\s+law|jurisdiction)\b', 'Dispute Resolution & Law'),
    (r'(?i)\b(important\s+dates?|effective\s+date|timeline)\b', 'Important Dates'),
    (r'(?i)\b(signatures?|in\s+witness\s+whereof)\b', 'Signatures')
]


def identify_sections(text: str) -> List[Dict[str, Any]]:
    """
    Part B: Identifies sections in the legal document using heading patterns.
    Returns a list of detected sections with their heading and excerpt.
    """
    detected_sections = []
    lines = text.splitlines()
    
    for idx, line in enumerate(lines):
        line_clean = line.strip()
        if not line_clean or len(line_clean) > 90:
            continue
            
        for pattern, section_name in LEGAL_SECTION_PATTERNS:
            if re.search(pattern, line_clean):
                # Extract up to 3 following lines as a sample snippet
                snippet_lines = [l.strip() for l in lines[idx+1:idx+4] if l.strip()]
                snippet = " ".join(snippet_lines)[:120]
                detected_sections.append({
                    "line_number": idx + 1,
                    "section_type": section_name,
                    "header_text": line_clean,
                    "snippet": snippet or "(Beginning of section)"
                })
                break
                
    return detected_sections


def divide_into_chunks(text: str, chunk_size: int = 3000, overlap: int = 300) -> List[Dict[str, Any]]:
    """
    Part B: Divides long documents into overlapping chunks where necessary.
    Avoids cutting in the middle of sentences or paragraphs.
    """
    if len(text) <= chunk_size:
        return [{
            "chunk_id": 1,
            "total_chunks": 1,
            "text": text,
            "start_char": 0,
            "end_char": len(text)
        }]
    
    chunks = []
    start = 0
    text_len = len(text)
    chunk_id = 1
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        
        # If not at the end of the document, try to find a paragraph break or newline
        if end < text_len:
            split_idx = text.rfind("\n\n", start, end)
            if split_idx == -1 or split_idx < start + (chunk_size // 2):
                split_idx = text.rfind("\n", start, end)
            if split_idx == -1 or split_idx < start + (chunk_size // 2):
                split_idx = text.rfind(". ", start, end)
                if split_idx != -1:
                    split_idx += 1  # include the period
            if split_idx != -1 and split_idx > start:
                end = split_idx
        
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "start_char": start,
                "end_char": end
            })
            chunk_id += 1
        
        # Advance with overlap
        if end >= text_len:
            break
        start = max(end - overlap, start + 1)
        
    for chunk in chunks:
        chunk["total_chunks"] = len(chunks)
        
    return chunks


def preprocess_document(raw_text: str, chunk_size: int = 3000, overlap: int = 300) -> Dict[str, Any]:
    """
    Unified Part B Preprocessing Pipeline:
    1. Removes unwanted characters
    2. Removes unnecessary spaces
    3. Normalizes text
    4. Identifies legal sections
    5. Divides long documents into chunks
    """
    # Step 1: Remove unwanted characters
    step1 = remove_unwanted_characters(raw_text)
    
    # Step 2: Normalize text
    step2 = normalize_text(step1)
    
    # Step 3: Remove unnecessary spaces
    cleaned_text = remove_unnecessary_spaces(step2)
    
    # Step 4: Identify sections
    sections = identify_sections(cleaned_text)
    
    # Step 5: Chunk long documents
    chunks = divide_into_chunks(cleaned_text, chunk_size=chunk_size, overlap=overlap)
    
    return {
        "raw_character_count": len(raw_text),
        "cleaned_character_count": len(cleaned_text),
        "characters_saved": len(raw_text) - len(cleaned_text),
        "cleaned_text": cleaned_text,
        "sections_identified": sections,
        "section_count": len(sections),
        "chunks": chunks,
        "chunk_count": len(chunks)
    }
