# LABORATORY RECORD

| **Ex. No.: 5** | **AUTOMATED LEGAL DOCUMENT ANALYZER USING GPT-4** | **URK23CS1174** |
|:--- |:--- |:--- |
| **Date:** 22.10.2026 | **Course:** 24CS2506 – Building Applications using GPT-4 | **Semester:** Odd 2026 |

---

### Aim:
To design and develop an automated legal document analyzer using GPT-4 (and local LLM) that reads legal contracts, preprocesses legal text, constructs structured prompts, extracts key legal clauses, obligations, parties, payment terms, termination conditions, and dates, generates concise summaries, and saves the structured report to disk.

---

### Problem Statement:
Design and develop an automated legal document analyzer using GPT-4. The application should accept a legal contract or legal text, analyze its content, and generate a concise summary. It should additionally identify important clauses, obligations, parties, payment terms, termination conditions, and important dates. The system should present the analysis in a structured format and save the generated report.

---

### Software Requirements:
| Software / Library | Version / Details |
|:--- |:--- |
| Operating System | Windows 11 |
| Language | Python 3.12.2 |
| LLM Models | OpenAI GPT-4 / GPT-4o / Local Ollama (Llama 3.2) |
| IDE | Visual Studio Code (VS Code) |
| PDF Extraction | `pypdf` 6.21.2 |
| PDF Generation | `reportlab` 5.0.1 |
| Web Interface | `streamlit` 1.30+ |
| Environment Manager | `python-dotenv` |

---

### Input Parameters & Modules:
| Module | Responsibility |
|:--- |:--- |
| **Part A: Input Module** | Accepts legal text from Keyboard, `.txt` files, and `.pdf` files. Extracts text and calculates metadata (word count, character count, page count, estimated reading time). |
| **Part B: Preprocessing Module** | Cleans unwanted/control characters, removes excess spaces, normalizes typography (quotes, dashes, Unicode), identifies legal sections, and divides long documents into chunks. |
| **Part C: Prompt Generation Module** | Constructs strict GPT-4 prompts with instructions: *"Do not invent information. If information is not available, state 'Not mentioned in the document.'"* and enforces standard output schema. |
| **Part D: Summarization & Analysis Module**| Directs prompt to GPT-4 / Ollama Llama 3.2, extracts structured analysis, and generates concise abstractive summaries. |
| **Part E: Save Module** | Automatically persists generated analyses to `outputs/legal_analysis.txt` with timestamped backup options. |
| **Part F: Complete Application** | Integrates all sub-modules into an interactive CLI (`app.py`) and a modern Streamlit web frontend (`frontend.py`). |

---

### System Architecture Workflow (Flask Web Application):
```
                  User (Web Browser)
                          │
                          ▼  1. Upload Document / Enter Text
  ┌────────────────────────────────────────────────────────┐
  │         Flask Web Application (Backend + Frontend)     │
  │                                                        │
  │  Frontend (HTML5, CSS3, JavaScript):                   │
  │   - Brand: LegalAI                                     │
  │   - File Upload / Drag & Drop Dropzone                 │
  │   - Quick Sample Selector (Service, NDA, Contract PDF) │
  │   - Feature Insight Cards & Real-time Progress         │
  │   - Structured Analysis Viewer with Section Badges     │
  │   - Download Report Button                             │
  │                                                        │
  │  Backend (Python + Flask):                             │
  │   - Route Handling & File Processing                   │
  │   - Text Preprocessing & Cleaning                      │
  │   - Strict Zero-Hallucination Prompt Construction      │
  │   - Local Ollama AI Runtime (Llama 3.2) / OpenAI GPT-4 │
  │   - Parse 10 Structured Sections                       │
  │   - Generate & Serve outputs/legal_analysis.txt        │
  └───────────────────────────┬────────────────────────────┘
                              │
                              ▼
            AI Engine: Ollama Llama 3.2 / GPT-4
                              │
                              ▼
    Structured Analysis (10 Sections: Type, Summary, Parties,
    Obligations, Payment, Dates, Clauses, Risk Analysis,
    Missing Terms, Recommendations & Disclaimer)
                              │
                              ▼
        Save & Serve outputs/legal_analysis.txt
```

---

### Output Format (Matching Experiment 5 Record):
```
=== 1. DOCUMENT TYPE ===
The document type is a Service Agreement.

=== 2. SUMMARY ===
The purpose of this agreement is to provide software development and maintenance services to XYZ Solutions Pvt. Ltd. The main terms include the development of software according to requirements, provision of technical support and maintenance, and payment of a total amount of Rs. 6,00,000 in monthly installments.

=== 3. PARTIES ===
- ABC Technologies Pvt. Ltd. (service provider)
- XYZ Solutions Pvt. Ltd. (client)

=== 4. KEY OBLIGATIONS ===
- ABC Technologies: Develop software according to requirements, provide technical support and maintenance.
- XYZ Solutions: Provide required information, make scheduled payments on time.

=== 5. PAYMENT TERMS ===
- Amount: Rs. 6,00,000
- Frequency: Monthly
- Due dates: Specified
- Penalties: Not specified
- Detailed terms: Payment to be made on monthly basis upon invoice submission.

=== 6. DURATION AND IMPORTANT DATES ===
- Start date: 1 January 2026
- End date: 31 December 2026

=== 7. KEY CLAUSES ===
- Confidentiality: Both parties shall preserve confidentiality of business and technical information.
- Termination: Either party can terminate by providing 30 days written notice.
- Liability: Not specified
- Dispute resolution: Not specified
- Intellectual property: Not specified

=== 8. RISK ANALYSIS ===
- Issue: Lack of clear payment terms and potential late fees.
  Why it matters: Uncertainty in payment schedules could lead to disputes.
  Potential impact: Delays in payment or disputes between parties.
- Issue: Insufficient information on liability and dispute resolution.
  Why it matters: Uncertainty in resolving disputes could lead to legal issues.
  Potential impact: Increased costs and time for resolving disputes.
- Issue: Limited information on intellectual property rights.
  Why it matters: Uncertainty in ownership and usage rights of developed software.
  Potential impact: Potential for disputes over software ownership and source code.

=== 9. MISSING OR UNCLEAR TERMS ===
- Liability and dispute resolution clauses
- Intellectual property rights and ownership
- Potential late fees and payment penalties

=== 10. RECOMMENDATIONS ===
- Clearly define payment terms and potential late fees to avoid disputes.
- Include liability and dispute resolution clauses to protect both parties and prevent misunderstandings.
- Clarify intellectual property rights and ownership to prevent disputes over software development.

=== DISCLAIMER ===
This report is generated by AI for informational purposes only and does not constitute formal legal advice.
```

---

### Result:
Thus, an automated legal document analyzer using GPT-4 was successfully designed, developed, and evaluated. The system successfully extracts text from multiple formats, cleans and preprocesses legal text, constructs structured prompts, performs abstractive summarization, identifies key obligations and clauses, and saves the analysis report to a file.
