import os
import sys

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from utils.document_reader import (
    read_from_keyboard,
    read_from_txt,
    read_from_pdf,
    display_document_info,
    get_document_metrics
)
from utils.preprocessor import preprocess_document
from utils.prompts import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
    build_summary_prompt,
    build_chunk_combination_prompt
)
from utils.llm_client import (
    generate_legal_response,
    is_openai_available,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_OLLAMA_MODEL
)
from utils.report_generator import save_analysis_report


class LegalDocumentAnalyzerApp:
    def __init__(self):
        self.raw_document_text = ""
        self.document_source = "None"
        self.page_count = 1
        self.preprocessed_data = None
        self.analysis_report = ""
        self.summary_report = ""
        
        # Engine setup
        if is_openai_available():
            self.engine = "openai"
            self.model_name = DEFAULT_OPENAI_MODEL
        else:
            self.engine = "ollama"
            self.model_name = DEFAULT_OLLAMA_MODEL

    def print_header(self):
        print("\n" + "=" * 65)
        print("    AUTOMATED LEGAL DOCUMENT ANALYZER USING GPT-4 / OLLAMA")
        print("          Course: 24CS2506 - Laboratory Experiment 5")
        print("=" * 65)
        print(f"  Current Engine : {self.engine.upper()} (Model: {self.model_name})")
        doc_status = f"Loaded ({len(self.raw_document_text.split())} words)" if self.raw_document_text else "None"
        print(f"  Active Document: {doc_status} | Source: {self.document_source}")
        print("=" * 65)

    def print_menu(self):
        print("\nMAIN MENU:")
        print("  1. Upload / Enter Legal Document")
        print("  2. Analyze Document")
        print("  3. Generate Summary")
        print("  4. Save Report")
        print("  5. Exit")
        print("-" * 65)

    def option_1_input_document(self):
        """Part A - Q1 & Q2: Read a legal document from the user and display neatly."""
        print("\n--- OPTION 1: UPLOAD / ENTER LEGAL DOCUMENT ---")
        print("Choose input method:")
        print("  [1] Keyboard Input (Type or Paste)")
        print("  [2] Load Plain Text File (.txt)")
        print("  [3] Load PDF File (.pdf)")
        print("  [4] Load Built-in Sample Service Agreement (.txt)")
        print("  [5] Load Built-in Sample Employment Agreement (.txt)")
        print("  [6] Load Built-in Sample Contract (.pdf)")
        print("  [0] Back to Main Menu")
        
        choice = input("\nEnter choice (0-6): ").strip()
        text = ""
        source = ""
        pages = 1

        if choice == "1":
            text = read_from_keyboard()
            source = "Keyboard Direct Input"
        elif choice == "2":
            path = input("Enter path to .txt file: ").strip().strip('"')
            if not os.path.exists(path):
                print(f"[Error] File not found: {path}")
                return
            text = read_from_txt(path)
            source = os.path.basename(path)
        elif choice == "3":
            path = input("Enter path to .pdf file: ").strip().strip('"')
            if not os.path.exists(path):
                print(f"[Error] File not found: {path}")
                return
            text, pages = read_from_pdf(path)
            source = os.path.basename(path)
        elif choice == "4":
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, "data", "sample_service_agreement.txt")
            text = read_from_txt(path)
            source = "sample_service_agreement.txt"
        elif choice == "5":
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, "data", "sample_employment_agreement.txt")
            text = read_from_txt(path)
            source = "sample_employment_agreement.txt"
        elif choice == "6":
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_dir, "data", "sample_contract.pdf")
            text, pages = read_from_pdf(path)
            source = "sample_contract.pdf"
        elif choice == "0":
            return
        else:
            print("[Warning] Invalid choice.")
            return

        if not text.strip():
            print("[Warning] Document text is empty!")
            return

        self.raw_document_text = text
        self.document_source = source
        self.page_count = pages
        self.analysis_report = ""
        self.summary_report = ""

        # Preprocess immediately for metadata
        self.preprocessed_data = preprocess_document(self.raw_document_text)

        # Part A - Q2: Display neatly
        display_document_info(self.raw_document_text, source_name=source, page_count=pages)

        # Show detected sections (Part B)
        sec_count = self.preprocessed_data["section_count"]
        chunk_count = self.preprocessed_data["chunk_count"]
        print(f"Preprocessed: {sec_count} sections detected | Document split into {chunk_count} chunk(s).")

    def option_2_analyze_document(self):
        """Part B, C, D: Preprocess, construct prompt, and run full structured analysis."""
        if not self.raw_document_text.strip():
            print("\n[Warning] No document loaded yet! Please select Option 1 first.")
            return

        print("\n--- OPTION 2: ANALYZE LEGAL DOCUMENT ---")
        print("Preprocessing document (removing unwanted chars, spaces, normalizing)...")
        if not self.preprocessed_data:
            self.preprocessed_data = preprocess_document(self.raw_document_text)

        cleaned_text = self.preprocessed_data["cleaned_text"]
        chunks = self.preprocessed_data["chunks"]

        print(f"Cleaned Text Characters: {len(cleaned_text):,} (Saved {self.preprocessed_data['characters_saved']} chars)")
        print(f"Sections Identified    : {self.preprocessed_data['section_count']}")
        for s in self.preprocessed_data["sections_identified"][:5]:
            print(f"  • {s['section_type']} (Line {s['line_number']})")
        if self.preprocessed_data["section_count"] > 5:
            print(f"  ... and {self.preprocessed_data['section_count'] - 5} more sections.")

        print(f"\nSending analysis request using {self.engine.upper()} ({self.model_name})...")
        
        # If multi-chunk long document, analyze each chunk and combine (Workflow Page 5 & 6)
        if len(chunks) > 1:
            print(f"Document is long: Analyzing {len(chunks)} chunks sequentially...")
            partial_analyses = []
            for c in chunks:
                chunk_prompt = build_analysis_prompt(
                    c["text"], 
                    chunk_info=f"Chunk {c['chunk_id']} of {c['total_chunks']}"
                )
                part_res, _ = generate_legal_response(
                    chunk_prompt, 
                    SYSTEM_PROMPT, 
                    engine=self.engine, 
                    model=self.model_name
                )
                partial_analyses.append(part_res)
            
            print("Combining chunk results into unified legal analysis...")
            combination_prompt = build_chunk_combination_prompt(partial_analyses)
            final_report, engine_used = generate_legal_response(
                combination_prompt, 
                SYSTEM_PROMPT, 
                engine=self.engine, 
                model=self.model_name
            )
        else:
            # Single chunk prompt
            prompt = build_analysis_prompt(cleaned_text)
            final_report, engine_used = generate_legal_response(
                prompt, 
                SYSTEM_PROMPT, 
                engine=self.engine, 
                model=self.model_name
            )

        self.analysis_report = final_report

        print("\n" + "=" * 65)
        print(f"   STRUCTURED LEGAL ANALYSIS RESULT (Engine: {engine_used})")
        print("=" * 65)
        print(self.analysis_report)
        print("=" * 65)
        print("Analysis completed successfully. Use Option 4 to save this report.")

    def option_3_generate_summary(self):
        """Part D - Q5: Generate concise Legal Document Summary."""
        if not self.raw_document_text.strip():
            print("\n[Warning] No document loaded yet! Please select Option 1 first.")
            return

        print("\n--- OPTION 3: GENERATE LEGAL DOCUMENT SUMMARY ---")
        cleaned_text = self.preprocessed_data["cleaned_text"] if self.preprocessed_data else self.raw_document_text
        # Truncate text if sending to summary prompt to keep concise
        sample_text = cleaned_text[:4000]

        prompt = build_summary_prompt(sample_text)
        print(f"Generating concise summary using {self.engine.upper()} ({self.model_name})...")
        
        summary_result, engine_used = generate_legal_response(
            prompt, 
            SYSTEM_PROMPT, 
            engine=self.engine, 
            model=self.model_name
        )
        self.summary_report = summary_result

        print("\n" + "=" * 65)
        print(f"   CONCISE LEGAL DOCUMENT SUMMARY (Engine: {engine_used})")
        print("=" * 65)
        print(self.summary_report)
        print("=" * 65)
        print("Summary generated successfully. Use Option 4 to save to file.")

    def option_4_save_report(self):
        """Part E - Q6: Save generated analysis or summary to file."""
        print("\n--- OPTION 4: SAVE REPORT ---")
        if not self.analysis_report and not self.summary_report:
            print("[Warning] No analysis or summary generated yet to save!")
            print("Please run Option 2 (Analyze Document) or Option 3 (Generate Summary) first.")
            return

        content_to_save = ""
        if self.analysis_report and self.summary_report:
            content_to_save = f"{self.analysis_report}\n\n{'=' * 50}\n\n{self.summary_report}"
        elif self.analysis_report:
            content_to_save = self.analysis_report
        else:
            content_to_save = self.summary_report

        base_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_dir, "outputs")
        
        saved_file = save_analysis_report(
            content_to_save, 
            output_dir=output_dir, 
            filename="legal_analysis.txt"
        )
        
        print("\n" + "=" * 65)
        print("   REPORT SAVED SUCCESSFULLY!")
        print("=" * 65)
        print(f"File Location : {saved_file}")
        print(f"File Size     : {os.path.getsize(saved_file):,} bytes")
        print("-" * 65)

    def run(self):
        while True:
            self.print_header()
            self.print_menu()
            choice = input("Enter choice (1-5): ").strip()
            
            if choice == "1":
                self.option_1_input_document()
            elif choice == "2":
                self.option_2_analyze_document()
            elif choice == "3":
                self.option_3_generate_summary()
            elif choice == "4":
                self.option_4_save_report()
            elif choice == "5":
                print("\nThank you for using the Automated Legal Document Analyzer. Exiting...\n")
                sys.exit(0)
            else:
                print("\n[Error] Invalid choice! Please select a number between 1 and 5.")


def main():
    app = LegalDocumentAnalyzerApp()
    app.run()


if __name__ == "__main__":
    main()
