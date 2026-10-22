import os
import sys

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure local modules are discoverable
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

from utils.document_reader import (
    read_from_txt,
    read_from_pdf,
    get_document_metrics,
    display_document_info
)
from utils.preprocessor import (
    preprocess_document,
    remove_unnecessary_spaces,
    remove_unwanted_characters,
    normalize_text,
    identify_sections,
    divide_into_chunks
)
from utils.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
    build_summary_prompt
)
from utils.llm_client import generate_legal_response
from utils.report_generator import save_analysis_report, read_saved_report


def test_pipeline():
    print("=" * 60)
    print("RUNNING AUTOMATED TEST SUITE FOR LEGAL DOCUMENT ANALYZER")
    print("=" * 60)

    # 1. Test Part A: Reading .txt and .pdf
    txt_path = os.path.join(base_dir, "data", "sample_service_agreement.txt")
    pdf_path = os.path.join(base_dir, "data", "sample_contract.pdf")

    assert os.path.exists(txt_path), f"TXT sample missing: {txt_path}"
    assert os.path.exists(pdf_path), f"PDF sample missing: {pdf_path}"

    txt_content = read_from_txt(txt_path)
    assert len(txt_content) > 100, "TXT content too short!"
    print(f"[PASS] Part A (Q1): Loaded TXT file ({len(txt_content)} characters)")

    pdf_content, pdf_pages = read_from_pdf(pdf_path)
    assert len(pdf_content) > 50 and pdf_pages >= 1, "PDF content extraction failed!"
    print(f"[PASS] Part A (Q1): Extracted PDF content ({len(pdf_content)} characters across {pdf_pages} page(s))")

    # Test Q2: Display neatly
    metrics = get_document_metrics(txt_content, source_name="sample_service_agreement.txt")
    assert metrics["total_words"] > 50, "Metrics word count calculation failed!"
    print(f"[PASS] Part A (Q2): Calculated document metrics (Words: {metrics['total_words']}, Chars: {metrics['total_characters']})")

    # 2. Test Part B: Preprocessing
    messy_text = "  SERVICE   AGREEMENT\x00\x08  \n\n\n\nSection 1: “Payment”  —  ₹50,000  \t  \n• Obligation 1"
    prep = preprocess_document(messy_text)
    assert "\x00" not in prep["cleaned_text"], "Unwanted character removal failed!"
    assert '“' not in prep["cleaned_text"], "Text normalization failed!"
    assert "\n\n\n" not in prep["cleaned_text"], "Space removal failed!"
    print(f"[PASS] Part B (Q3): Cleaning & normalization verified.")

    # Section identification
    sections = identify_sections(txt_content)
    assert len(sections) >= 3, f"Expected at least 3 sections, found {len(sections)}"
    print(f"[PASS] Part B (Q3): Identified {len(sections)} sections in sample contract.")

    # Chunking test
    chunks = divide_into_chunks(txt_content, chunk_size=500, overlap=50)
    assert len(chunks) > 1, "Chunking failed to split document!"
    print(f"[PASS] Part B (Q3): Document chunking verified ({len(chunks)} chunks).")

    # 3. Test Part C & D: Prompt Generation and LLM Analysis
    analysis_prompt = build_analysis_prompt(txt_content)
    assert "LEGAL DOCUMENT ANALYSIS" in analysis_prompt
    assert "Do not invent information" in analysis_prompt
    print(f"[PASS] Part C (Q4): Constructed GPT-4 legal analysis prompt.")

    summary_prompt = build_summary_prompt(txt_content)
    assert "LEGAL DOCUMENT SUMMARY" in summary_prompt
    print(f"[PASS] Part D (Q5): Constructed GPT-4 legal summary prompt.")

    # Test LLM response (using Ollama llama3.2 or fallback)
    print("\nCalling LLM client for structured analysis...")
    analysis_result, engine = generate_legal_response(
        analysis_prompt, SYSTEM_PROMPT, engine="auto"
    )
    print(f"[PASS] Part D (Q5): Analysis generated using [{engine}]!")
    print("\n--- SAMPLE EXTRACTED ANALYSIS SNIPPET ---")
    print("\n".join(analysis_result.splitlines()[:15]))
    print("...")

    # 4. Test Part E: Save Report (Q6)
    out_dir = os.path.join(base_dir, "outputs")
    saved_file = save_analysis_report(analysis_result, output_dir=out_dir, filename="legal_analysis.txt")
    assert os.path.exists(saved_file), "Saved report not found!"
    saved_text = read_saved_report(saved_file)
    assert len(saved_text) > 50, "Saved file is empty!"
    print(f"[PASS] Part E (Q6): Report saved successfully to {saved_file} ({len(saved_text)} bytes).")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! (100% Complete)")
    print("=" * 60)


if __name__ == "__main__":
    test_pipeline()
