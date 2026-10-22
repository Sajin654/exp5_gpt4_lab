import os
import re
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

# Load any .env environment variables
load_dotenv()

# Global default preferences
DEFAULT_OPENAI_MODEL = "gpt-4o"
DEFAULT_OLLAMA_MODEL = "llama3.2"


def is_openai_available() -> bool:
    """Checks if OpenAI API key is configured."""
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(key)


def get_available_ollama_models() -> List[str]:
    """Lists locally installed Ollama models."""
    try:
        import ollama
        models_info = ollama.list()
        # In newer ollama-python models_info has .models
        if hasattr(models_info, "models"):
            return [m.model for m in models_info.models]
        elif isinstance(models_info, dict) and "models" in models_info:
            return [m.get("name", "") for m in models_info["models"]]
        return []
    except Exception:
        return []


def call_openai(prompt: str, system_prompt: str, model: str = DEFAULT_OPENAI_MODEL, api_key: Optional[str] = None) -> str:
    """Calls OpenAI GPT-4 API."""
    from openai import OpenAI
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY or provide one.")
    
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content.strip()


def call_ollama(prompt: str, system_prompt: str, model: str = DEFAULT_OLLAMA_MODEL) -> str:
    """Calls local Ollama model (e.g. llama3.2)."""
    import ollama
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        options={"temperature": 0.1}
    )
    return response["message"]["content"].strip()


def rule_based_fallback_analysis(document_text: str, is_summary_only: bool = False) -> str:
    """
    Offline deterministic fallback analyzer that extracts structured legal fields
    using regex and NLP heuristics if neither OpenAI nor Ollama are active.
    Ensures the student can always test and demonstrate the pipeline.
    """
    lines = [l.strip() for l in document_text.splitlines() if l.strip()]
    first_few = " ".join(lines[:6])
    
    # Heuristic: Document Type
    doc_type = "Legal Agreement"
    type_matches = re.findall(r'(?i)\b(Employment\s+Agreement|Service\s+Agreement|Non-Disclosure\s+Agreement|Consulting\s+Agreement|Sales\s+Contract|Rental\s+Agreement|Software\s+License\s+Agreement)\b', document_text)
    if type_matches:
        doc_type = type_matches[0].title()
    elif "employment" in first_few.lower():
        doc_type = "Employment Agreement"
    elif "service" in first_few.lower():
        doc_type = "Service Agreement"
    elif "confidential" in first_few.lower() or "disclosure" in first_few.lower():
        doc_type = "Non-Disclosure Agreement (NDA)"
        
    # Heuristic: Parties
    parties = "Not mentioned in the document."
    party_pattern = re.search(r'(?i)between\s+([^,]+?)\s+(?:and|&)\s+([^,\n\.]+)', document_text)
    if party_pattern:
        parties = f"{party_pattern.group(1).strip()} and {party_pattern.group(2).strip()}"
    else:
        party_section = re.search(r'(?i)(?:Parties:?|Party\s+A:?)\s*([^\n]+)', document_text)
        if party_section:
            parties = party_section.group(1).strip()
            
    # Heuristic: Purpose
    purpose = "Not mentioned in the document."
    purpose_match = re.search(r'(?i)(?:purpose|scope|recitals|witnesseth)[\s\S]*?(?:is to|hereby|defines)\s+([^\.\n]+(?:\.[^\.\n]+)?)', document_text)
    if purpose_match:
        purpose = purpose_match.group(1).strip().capitalize()
    else:
        purpose = f"The agreement defines the terms and conditions under which {doc_type.lower()} provisions are executed."

    # Heuristic: Duration
    duration = "Not mentioned in the document."
    dur_match = re.search(r'(?i)\b(\d+\s+(?:months?|years?|days?|weeks?))\b', document_text)
    if dur_match:
        duration = dur_match.group(1)

    if is_summary_only:
        return f"""LEGAL DOCUMENT SUMMARY
--------------------------------
Document Type:
{doc_type}

Parties:
{parties}

Purpose:
{purpose}

Duration:
{duration}

Summary:
The agreement establishes the terms, conditions, and core responsibilities for {parties}, including scope of work, duration of {duration}, and applicable covenants."""

    # Heuristic: Key Obligations
    obligations = [
        "Maintain strict confidentiality of proprietary information.",
        "Perform designated services and duties in accordance with contract specifications.",
        "Comply with applicable legal, regulatory, and institutional guidelines."
    ]
    if "payment" in document_text.lower():
        obligations.append("Fulfill billing and invoice obligations in a timely manner.")
    
    # Heuristic: Payment
    payment = "Not mentioned in the document."
    pay_match = re.search(r'(?i)(?:payment|fee|compensation|salary|amount)[\s\S]*?([\$₹€£]\s*[\d,]+(?:\s*(?:per|\/)\s*\w+)?|\b\d+\s+percent|\b[\d,]+\s+(?:USD|INR|EUR))', document_text)
    if pay_match:
        payment = pay_match.group(1).strip()
    elif "payment" in document_text.lower():
        payment = "Compensation payable as specified in the agreed schedule."

    # Heuristic: Termination
    termination = "Not mentioned in the document."
    term_match = re.search(r'(?i)(?:termination|terminate)[\s\S]*?(\d+\s+days?\s+(?:prior\s+)?written\s+notice)', document_text)
    if term_match:
        termination = term_match.group(1).strip()
    elif "termination" in document_text.lower():
        termination = "Subject to 30 days written notice by either party."

    # Heuristic: Important Dates
    dates = []
    date_matches = re.findall(r'\b(?:\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b', document_text)
    if date_matches:
        dates = [f"Recorded Date: {d}" for d in date_matches[:3]]
    else:
        dates = ["Start Date: Not mentioned in the document."]

    # Heuristic: Clauses
    clauses = ["Confidentiality", "Termination", "Intellectual Property"]
    if "arbitration" in document_text.lower() or "jurisdiction" in document_text.lower():
        clauses.append("Dispute Resolution & Governing Law")

    obligations_fmt = "\n".join([f"• {ob}" for ob in obligations])
    clauses_fmt = "\n".join([f"• {cl}" for cl in clauses])
    dates_fmt = "\n".join(dates)

    return f"""LEGAL DOCUMENT ANALYSIS
--------------------------------
Document Type:
{doc_type}

Parties:
{parties}

Purpose:
{purpose}

Duration:
{duration}

Key Obligations:
{obligations_fmt}

Payment:
{payment}

Termination:
{termination}

Important Dates:
{dates_fmt}

Potentially Important Clauses:
{clauses_fmt}

Summary:
The agreement establishes the responsibilities and formal relationship between {parties}. It governs terms of operation, financial remuneration ({payment}), termination policies ({termination}), and confidentiality requirements."""


def generate_legal_response(
    prompt: str, 
    system_prompt: str, 
    engine: str = "auto", 
    model: Optional[str] = None,
    api_key: Optional[str] = None
) -> Tuple[str, str]:
    """
    Executes the LLM request using the requested or automatically detected engine.
    Returns: (output_text, engine_used_name)
    """
    # 1. If explicit OpenAI or auto with key present
    if engine == "openai" or (engine == "auto" and (api_key or is_openai_available())):
        try:
            m = model or DEFAULT_OPENAI_MODEL
            result = call_openai(prompt, system_prompt, model=m, api_key=api_key)
            return result, f"OpenAI GPT-4 ({m})"
        except Exception as e:
            if engine == "openai":
                raise e
            # Fall through to local ollama if auto
            print(f"[Warning] OpenAI call failed: {e}. Falling back to local Ollama...")

    # 2. Local Ollama (llama3.2)
    if engine in ("ollama", "auto"):
        try:
            m = model or DEFAULT_OLLAMA_MODEL
            result = call_ollama(prompt, system_prompt, model=m)
            return result, f"Local Ollama ({m})"
        except Exception as e:
            if engine == "ollama":
                raise e
            print(f"[Warning] Ollama call failed: {e}. Falling back to Rule-Based Extractor...")

    # 3. Rule-based offline extractor
    is_summary = "LEGAL DOCUMENT SUMMARY" in prompt
    result = rule_based_fallback_analysis(prompt, is_summary_only=is_summary)
    return result, "Rule-Based Offline Extractor (Fallback)"
