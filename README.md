# 24CS2506 – Building Applications using GPT-4
## Experiment 5 – Automated Legal Document Analyzer using GPT-4

**Student Registration No:** URK23CS1174  
**Course Code:** 24CS2506  
**Department:** Computer Science and Engineering  
**Institution:** Karunya Institute of Technology and Sciences  

---

## 📌 Problem Statement
Design and develop an automated legal document analyzer using GPT-4. The application should accept a legal contract or legal text, analyze its content and generate a concise summary. It should additionally identify:
- Important clauses
- Obligations
- Parties involved
- Payment terms
- Termination conditions
- Important dates

The system presents the analysis in a structured format and saves the generated report to disk (`outputs/legal_analysis.txt`).

---

## 🏗️ System Architecture & Workflow

```
[Legal Document Input]
 (.txt / .pdf / Keyboard)
           │
           ▼
[Part A: Document Input & Metadata Display] (Q1, Q2)
           │
           ▼
[Part B: Document Preprocessing] (Q3)
 - Remove unnecessary spaces
 - Remove unwanted / non-printable characters
 - Typography & character normalization
 - Section & clause identification
 - Intelligent chunking with overlap for long contracts
           │
           ▼
[Part C: Prompt Construction] (Q4)
 - Role: Legal Document Analysis Assistant
 - Task & Constraints: "Do not invent information. If not available, state 'Not mentioned in the document.'"
 - Target structured schema
           │
           ▼
[Part D: GPT-4 / Ollama LLM Processing] (Q5)
 - Full Structured Legal Analysis
 - Concise Legal Document Summary
           │
           ▼
[Part E: Save Analysis Report] (Q6)
 - Saved to outputs/legal_analysis.txt
           │
           ▼
[Part F: Integrated Complete Application] (Q7)
 - Interactive Console Application (app.py)
 - Interactive Streamlit Web UI (frontend.py)
```

---

## 📂 Project Directory Structure

```
C:\Users\Shajin\OneDrive\Vscode\exp_5_gpt\
│
├── app.py                     # Main Console Application (Interactive 5-option Menu)
├── frontend.py                # Modern Streamlit Web Application (UI)
├── test_analyzer.py           # Automated Test Suite for all Questions (Q1-Q7)
├── requirements.txt           # Python dependencies
├── README.md                  # Complete Lab Documentation & Guide
│
├── utils/                     # Modular Core Engine
│   ├── __init__.py
│   ├── document_reader.py     # Part A (Q1, Q2): Text, PDF parsing & neat info display
│   ├── preprocessor.py        # Part B (Q3): Cleaning, normalization, sections, chunking
│   ├── prompts.py             # Part C (Q4) & Part D (Q5): Exact GPT-4 prompt templates
│   ├── llm_client.py          # Unified client (OpenAI GPT-4 + Local Ollama Llama 3.2 fallback)
│   └── report_generator.py    # Part E (Q6): Saving & managing output reports
│
├── data/                      # Test Contracts & Sample Legal Documents
│   ├── sample_service_agreement.txt     # Service agreement matching syllabus sample
│   ├── sample_employment_agreement.txt  # Employment contract matching Page 5 format
│   ├── sample_nda.txt                   # Non-disclosure agreement
│   └── sample_contract.pdf              # Generated PDF contract for testing PDF extraction
│
└── outputs/                   # Generated Analysis Reports
    ├── legal_analysis.txt               # Primary output required by syllabus
    └── legal_analysis_[timestamp].txt   # Preserved timestamped reports
```

---

## 🚀 How to Run in Visual Studio Code

### Step 1: Open the Project in VS Code
1. Open **Visual Studio Code**.
2. Click **File** > **Open Folder...**
3. Select:
   ```
   C:\Users\Shajin\OneDrive\Vscode\exp_5_gpt
   ```
4. Open the integrated terminal (`Ctrl + ~` or **Terminal** > **New Terminal**).

### Step 2: (Optional) Set your OpenAI API Key (if using GPT-4 cloud)
If you have an OpenAI API key, set it in your terminal:
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```
> **Note:** If no OpenAI key is set, the project automatically uses your local **Ollama (`llama3.2`)** model with zero cost and 100% offline support!

### Step 3: Run the Complete Interactive Console Application (Q7)
```powershell
python app.py
```
**Menu Options:**
```
=================================================================
    AUTOMATED LEGAL DOCUMENT ANALYZER USING GPT-4 / OLLAMA
          Course: 24CS2506 - Laboratory Experiment 5
=================================================================
MAIN MENU:
  1. Upload / Enter Legal Document
  2. Analyze Document
  3. Generate Summary
  4. Save Report
  5. Exit
-----------------------------------------------------------------
```

### Step 4: Run the Streamlit Web Application (UI)
```powershell
streamlit run frontend.py
```
This will open the web interface in your browser at `http://localhost:8501`.
Features:
- **Engine Selection:** Toggle between OpenAI GPT-4 and Local Ollama Llama 3.2.
- **One-Click Samples:** Quickly load built-in Service Agreement, Employment Contract, NDA, or PDF.
- **Preprocessing Tab:** Inspect characters cleaned, identified sections, and chunks.
- **Analysis & Summary Tabs:** View formatted extraction cards and summaries.
- **Save & Export Tab:** Save to `outputs/legal_analysis.txt` or download directly.

### Step 5: Run Automated Tests
```powershell
python test_analyzer.py
```

---

## 📋 Syllabus Questions Mapping

| Part | Question | Implementation File | Key Function |
| :--- | :--- | :--- | :--- |
| **Part A** | **Q1.** Read legal document (.txt, .pdf, keyboard) | `utils/document_reader.py` | `read_from_keyboard()`, `read_from_txt()`, `read_from_pdf()` |
| **Part A** | **Q2.** Display document information neatly | `utils/document_reader.py` | `display_document_info()`, `get_document_metrics()` |
| **Part B** | **Q3.** Document Preprocessing (clean, normalize, sections, chunks) | `utils/preprocessor.py` | `preprocess_document()`, `identify_sections()`, `divide_into_chunks()` |
| **Part C** | **Q4.** Construct GPT-4 prompt with strict constraints | `utils/prompts.py` | `build_analysis_prompt()` |
| **Part D** | **Q5.** Generate concise legal summary | `utils/prompts.py`, `utils/llm_client.py` | `build_summary_prompt()`, `generate_legal_response()` |
| **Part E** | **Q6.** Save generated analysis to `outputs/legal_analysis.txt` | `utils/report_generator.py` | `save_analysis_report()` |
| **Part F** | **Q7.** Complete Integrated Application | `app.py` & `frontend.py` | Main event loop & Streamlit app |

---

## 📄 Sample Output Format (As specified on Page 5 of Syllabus)

```
LEGAL DOCUMENT ANALYSIS
--------------------------------
Document Type:
Service Agreement

Parties:
• ABC Technologies (Client)
• XYZ Solutions (Service Provider)

Purpose:
The agreement defines the terms under which software development services will be provided, specifically for the design, development, testing, and deployment of a custom enterprise inventory tracking application.

Duration:
This Agreement shall be effective from February 01, 2026, and shall continue in full force and effect for a duration of 12 months, expiring on January 31, 2027, unless terminated earlier in accordance with the terms herein.

Key Obligations:
• The Service Provider shall deliver software development milestones in accordance with the agreed technical specifications.
• The Service Provider shall assign qualified personnel and ensure code quality and unit testing.
• The Client shall provide necessary system access, documentation, and prompt approvals.
• Both parties shall cooperate in good faith to resolve technical roadblocks.

Payment:
The Client shall pay the Service Provider a total consideration of ₹600,000 payable in monthly installments of ₹50,000 per month. Invoices shall be submitted on the 1st of each calendar month and paid within 15 days of receipt.

Termination:
Either party may terminate this Agreement without cause by providing 30 days written notice to the other party. Either party may terminate immediately for material breach if the breaching party fails to cure such breach within 15 days of written notice.

Important Dates:
• Effective Date: January 15, 2026
• Start Date: February 01, 2026
• End Date: January 31, 2027
• Renewal: Not mentioned in the document
• Deadlines: January 31, 2027 (expiration date)

Potentially Important Clauses:
• Confidentiality (Clause 5)
• Intellectual Property (Clause 6)
• Liability / Indemnification: Not mentioned in the document

Summary:
This Service Agreement outlines the terms and conditions for software development services provided by XYZ Solutions to ABC Technologies. The agreement includes key obligations, payment terms, termination conditions, and important clauses such as confidentiality and intellectual property. The duration of the agreement is 12 months, expiring on January 31, 2027.
```
