"""
Prompt Generation Module for Legal Document Analyzer
Implements Part C - Q4 and Part D - Q5 requirements.
"""

SYSTEM_PROMPT = """You are an expert legal document analysis assistant.
Your task is to analyze legal contracts, agreements, and texts accurately and objectively.

CRITICAL INSTRUCTIONS & CONSTRAINTS:
1. Use only the information explicitly present in the provided legal document.
2. Do not invent, assume, or extrapolate information.
3. If any requested information is not available or not explicitly stated in the document, you MUST state: "Not mentioned in the document."
4. Present the analysis neatly following the requested structured format exactly."""


def build_analysis_prompt(document_text: str, chunk_info: str = "") -> str:
    """
    Part C - Q4: Constructs the structured analysis prompt for GPT-4.
    Instructs the model to extract:
    - Document Type
    - Parties
    - Purpose
    - Duration
    - Key Obligations
    - Payment terms
    - Termination conditions
    - Important dates
    - Key clauses
    - Summary
    """
    prompt = f"""You are a legal document analysis assistant.
Analyze the following legal document and extract all key information into the exact structured format shown below.

{f"Context: {chunk_info}" if chunk_info else ""}

LEGAL DOCUMENT TEXT:
\"\"\"
{document_text}
\"\"\"

INSTRUCTIONS:
1. Extract all the specified fields accurately.
2. Do not invent information. If information is not available, state "Not mentioned in the document."
3. Follow the exact output format below with identical headers and bullet points.

REQUIRED OUTPUT FORMAT:
LEGAL DOCUMENT ANALYSIS
--------------------------------
Document Type:
[Specify the contract/agreement type, e.g. Employment Agreement, Service Agreement, NDA, etc.]

Parties:
[List the full names of all parties involved in the agreement]

Purpose:
[Concise explanation of the objective and purpose of the agreement]

Duration:
[Term or duration of the contract, including validity period]

Key Obligations:
• [Key obligation / responsibility 1]
• [Key obligation / responsibility 2]
• [Key obligation / responsibility 3]

Payment:
[Payment terms, compensation, rates, milestones, invoice schedules]

Termination:
[Termination conditions, notice period, and causes for termination]

Important Dates:
[All relevant dates: Effective Date, Start Date, End Date, Renewal, Deadlines]

Potentially Important Clauses:
• [Important clause 1, e.g., Confidentiality]
• [Important clause 2, e.g., Intellectual Property]
• [Important clause 3, e.g., Liability / Indemnification]

Summary:
[A comprehensive abstractive summary explaining the core terms, responsibilities, and key conditions]
"""
    return prompt.strip()


def build_summary_prompt(document_text: str) -> str:
    """
    Part D - Q5: Constructs prompt specifically for Legal Document Summarization
    matching the exact sample output format specified in the syllabus.
    """
    prompt = f"""You are a legal document analysis assistant.
Generate a concise summary of the provided legal document.

LEGAL DOCUMENT TEXT:
\"\"\"
{document_text}
\"\"\"

INSTRUCTIONS:
1. Do not invent information. If information is not available, state "Not mentioned in the document."
2. Output ONLY the following format:

LEGAL DOCUMENT SUMMARY
--------------------------------
Document Type:
[Document Type]

Parties:
[Parties involved]

Purpose:
[Purpose of the agreement]

Duration:
[Duration / Term]

Summary:
[Concise 2-4 sentence summary of the agreement establishing core responsibilities, payment, and key conditions]
"""
    return prompt.strip()


def build_chunk_combination_prompt(partial_analyses: list) -> str:
    """
    For long documents divided into chunks:
    Combines the partial analyses from all chunks into a unified final structured analysis.
    """
    combined_texts = "\n\n--- NEXT CHUNK ANALYSIS ---\n\n".join(partial_analyses)
    prompt = f"""You are a legal document analysis assistant.
Below are intermediate analyses extracted from separate sections of a long legal document.
Combine and harmonize them into a single, cohesive, comprehensive final analysis without duplicates.

INTERMEDIATE ANALYSES:
\"\"\"
{combined_texts}
\"\"\"

INSTRUCTIONS:
1. Merge the information logically.
2. Eliminate redundant points in obligations and clauses.
3. If information is not available in any chunk, state "Not mentioned in the document."
4. Output the result using the exact recommended format:

LEGAL DOCUMENT ANALYSIS
--------------------------------
Document Type:
[Document Type]

Parties:
[Parties]

Purpose:
[Purpose]

Duration:
[Duration]

Key Obligations:
• [Obligations]

Payment:
[Payment terms]

Termination:
[Termination conditions]

Important Dates:
[Important Dates]

Potentially Important Clauses:
• [Key clauses]

Summary:
[Unified comprehensive summary]
"""
    return prompt.strip()


def build_enhanced_analysis_prompt(document_text: str) -> str:
    """
    Constructs the 10-section structured analysis prompt matching
    the exact format shown in the reference frontend screenshots:
    1. Document Type
    2. Summary
    3. Parties
    4. Key Obligations
    5. Payment Terms
    6. Duration and Important Dates
    7. Key Clauses
    8. Risk Analysis (Issues, Why it matters, Potential impact)
    9. Missing or Unclear Terms
    10. Recommendations
    + Disclaimer
    """
    prompt = f"""You are a legal document analysis assistant.
Analyze the provided legal document thoroughly and generate a comprehensive structured analysis report matching the exact format and headers below.

LEGAL DOCUMENT TEXT:
\"\"\"
{document_text}
\"\"\"

CRITICAL INSTRUCTIONS:
1. Do not invent facts. If any specific detail is not present in the document, explicitly write "Not specified" or "Not mentioned in the document."
2. Analyze risks, missing terms, and practical recommendations based strictly on what is present or omitted from the contract.
3. Use the exact uppercase headers with triple equals below:

=== 1. DOCUMENT TYPE ===
[Specify the exact contract/agreement type, e.g., Service Agreement, Employment Contract, Non-Disclosure Agreement]

=== 2. SUMMARY ===
[A clear 2-4 sentence executive summary describing the purpose, scope, and key relationship defined in this agreement]

=== 3. PARTIES ===
- [Party 1 name and role, e.g., Client / Employer]
- [Party 2 name and role, e.g., Service Provider / Employee]

=== 4. KEY OBLIGATIONS ===
- [Party 1]: [Obligation details]
- [Party 2]: [Obligation details]

=== 5. PAYMENT TERMS ===
- Amount: [Fee, compensation or total amount]
- Frequency: [Monthly, one-time, milestone-based]
- Due dates: [Specific due dates, payment schedule]
- Penalties: [Late payment penalties or interest, or "Not specified"]
- Detailed terms: [Invoice submission and payment process]

=== 6. DURATION AND IMPORTANT DATES ===
- Start date: [Effective/start date]
- End date: [Expiration/completion date]
- Renewal: [Renewal provisions or "Not specified"]
- Key Milestones: [Important deadlines or dates mentioned]

=== 7. KEY CLAUSES ===
- Confidentiality: [Details of confidentiality obligations]
- Termination: [Notice period and termination conditions]
- Liability: [Liability caps, indemnities or "Not specified"]
- Dispute resolution: [Jurisdiction, arbitration or governing law]
- Intellectual property: [Ownership of work product / deliverables]

=== 8. RISK ANALYSIS ===
- Issue: [Identified contractual risk or vulnerability 1]
  Why it matters: [Explanation of why this is a concern]
  Potential impact: [Consequence on parties, operations or finances]
- Issue: [Identified contractual risk 2, e.g., liability ambiguity or late fees]
  Why it matters: [Explanation]
  Potential impact: [Consequence]
- Issue: [Identified contractual risk 3, e.g., termination notice or IP ownership]
  Why it matters: [Explanation]
  Potential impact: [Consequence]

=== 9. MISSING OR UNCLEAR TERMS ===
- [Missing term 1, e.g. Dispute resolution or governing law details]
- [Missing term 2, e.g. Indemnification and limitation of liability]
- [Missing term 3, e.g. Explicit penalty clauses for delays]

=== 10. RECOMMENDATIONS ===
- [Actionable recommendation 1 to clarify or strengthen the contract]
- [Actionable recommendation 2 to protect both parties and prevent disputes]
- [Actionable recommendation 3 for compliance and operational clarity]

=== DISCLAIMER ===
This report is generated by AI for informational purposes only and does not constitute formal legal advice.
"""
    return prompt.strip()

