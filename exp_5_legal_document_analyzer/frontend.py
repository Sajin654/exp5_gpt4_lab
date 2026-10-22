import os
import streamlit as st
from utils.document_reader import (
    read_from_txt,
    read_from_pdf,
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
    get_available_ollama_models,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_OLLAMA_MODEL
)
from utils.report_generator import (
    save_analysis_report,
    list_saved_reports,
    read_saved_report
)

# Page configuration
st.set_page_config(
    page_title="Automated Legal Document Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App Title & Subtitle
st.title("⚖️ Automated Legal Document Analyzer")
st.caption("24CS2506 – Building Applications using GPT-4 | Experiment 5")
st.markdown(
    "Automate the extraction, summarization, and structured analysis of legal contracts, "
    "identifying key clauses, obligations, parties, payment terms, and critical dates."
)

st.divider()

# ----------------- SIDEBAR CONFIGURATION -----------------
with st.sidebar:
    st.header("⚙️ Model Configuration")
    
    ollama_models = get_available_ollama_models()
    default_engine = "OpenAI GPT-4" if is_openai_available() else "Local Ollama (Llama 3.2)"
    
    engine_choice = st.radio(
        "Select LLM Engine:",
        ["Local Ollama (Llama 3.2)", "OpenAI GPT-4", "Rule-Based Fallback"],
        index=0 if "Local" in default_engine else 1
    )
    
    api_key = None
    selected_model = None
    
    if engine_choice == "OpenAI GPT-4":
        api_key = st.text_input(
            "OpenAI API Key:",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key or set OPENAI_API_KEY environment variable."
        )
        selected_model = st.selectbox(
            "OpenAI Model:",
            ["gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
            index=0
        )
    elif engine_choice == "Local Ollama (Llama 3.2)":
        model_options = ollama_models if ollama_models else ["llama3.2"]
        selected_model = st.selectbox(
            "Ollama Model:",
            model_options,
            index=0
        )
        st.info("Running locally via Ollama with zero API cost.")

    st.divider()
    st.header("📁 Load Sample Documents")
    st.write("Click a sample to load directly:")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_col1, sample_col2 = st.columns(2)
    
    with sample_col1:
        if st.button("📄 Service Agreement", use_container_width=True):
            p = os.path.join(base_dir, "data", "sample_service_agreement.txt")
            if os.path.exists(p):
                st.session_state["doc_text"] = read_from_txt(p)
                st.session_state["doc_name"] = "sample_service_agreement.txt"
                st.session_state["doc_pages"] = 1
                st.rerun()

    with sample_col2:
        if st.button("📑 Employment Contract", use_container_width=True):
            p = os.path.join(base_dir, "data", "sample_employment_agreement.txt")
            if os.path.exists(p):
                st.session_state["doc_text"] = read_from_txt(p)
                st.session_state["doc_name"] = "sample_employment_agreement.txt"
                st.session_state["doc_pages"] = 1
                st.rerun()

    sample_col3, sample_col4 = st.columns(2)
    with sample_col3:
        if st.button("🔒 Non-Disclosure (NDA)", use_container_width=True):
            p = os.path.join(base_dir, "data", "sample_nda.txt")
            if os.path.exists(p):
                st.session_state["doc_text"] = read_from_txt(p)
                st.session_state["doc_name"] = "sample_nda.txt"
                st.session_state["doc_pages"] = 1
                st.rerun()

    with sample_col4:
        if st.button("📕 Sample PDF Contract", use_container_width=True):
            p = os.path.join(base_dir, "data", "sample_contract.pdf")
            if os.path.exists(p):
                text, pages = read_from_pdf(p)
                st.session_state["doc_text"] = text
                st.session_state["doc_name"] = "sample_contract.pdf"
                st.session_state["doc_pages"] = pages
                st.rerun()

# Initialize session state variables
if "doc_text" not in st.session_state:
    st.session_state["doc_text"] = ""
if "doc_name" not in st.session_state:
    st.session_state["doc_name"] = "No document loaded"
if "doc_pages" not in st.session_state:
    st.session_state["doc_pages"] = 1
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = ""
if "summary_result" not in st.session_state:
    st.session_state["summary_result"] = ""

# ----------------- MAIN TABS -----------------
tab_input, tab_preprocess, tab_analyze, tab_summary, tab_save = st.tabs([
    "📥 1. Document Input",
    "🧹 2. Preprocessing",
    "🔍 3. Structured Analysis",
    "📋 4. Document Summary",
    "💾 5. Save & Export"
])

# ----------------- TAB 1: DOCUMENT INPUT -----------------
with tab_input:
    st.subheader("Part A – Legal Document Input (Q1 & Q2)")
    
    input_method = st.radio(
        "Choose Input Method:",
        ["File Upload (.txt or .pdf)", "Direct Text Entry / Keyboard Paste"],
        horizontal=True
    )
    
    if input_method == "File Upload (.txt or .pdf)":
        uploaded_file = st.file_uploader(
            "Upload Legal Document",
            type=["txt", "pdf"],
            help="Select a .txt contract or .pdf agreement to extract text."
        )
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".pdf"):
                text, pages = read_from_pdf(uploaded_file)
                st.session_state["doc_text"] = text
                st.session_state["doc_name"] = uploaded_file.name
                st.session_state["doc_pages"] = pages
            else:
                raw_bytes = uploaded_file.read()
                st.session_state["doc_text"] = raw_bytes.decode("utf-8", errors="replace")
                st.session_state["doc_name"] = uploaded_file.name
                st.session_state["doc_pages"] = 1
            st.success(f"Loaded '{uploaded_file.name}' successfully!")
    else:
        typed_text = st.text_area(
            "Paste or Type Legal Document Text:",
            value=st.session_state["doc_text"],
            height=250,
            placeholder="Enter agreement terms, clauses, obligations, parties here..."
        )
        if st.button("Load Typed Text"):
            st.session_state["doc_text"] = typed_text
            st.session_state["doc_name"] = "Direct Keyboard Input"
            st.session_state["doc_pages"] = 1
            st.success("Document text updated successfully!")

    # Display document info neatly (Part A - Q2)
    if st.session_state["doc_text"].strip():
        metrics = get_document_metrics(
            st.session_state["doc_text"],
            source_name=st.session_state["doc_name"],
            page_count=st.session_state["doc_pages"]
        )
        
        st.markdown("### 📊 Document Information (Part A - Q2)")
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        col_m1.metric("Source", metrics["source"][:18])
        col_m2.metric("Total Words", f"{metrics['total_words']:,}")
        col_m3.metric("Characters", f"{metrics['total_characters']:,}")
        col_m4.metric("Line Count", metrics["total_lines"])
        col_m5.metric("Est. Reading Time", f"{metrics['estimated_reading_time_min']} min")
        
        with st.expander("📄 View Full Document Text", expanded=False):
            st.text_area("Document Content", st.session_state["doc_text"], height=300, disabled=True)
    else:
        st.info("No document loaded yet. Upload a file, enter text, or pick a sample from the sidebar.")

# ----------------- TAB 2: PREPROCESSING -----------------
with tab_preprocess:
    st.subheader("Part B – Document Preprocessing (Q3)")
    st.write(
        "Performs cleaning operations before sending to GPT-4: "
        "removing unwanted characters, excess spaces, normalizing typography, detecting sections, and chunking."
    )
    
    if st.session_state["doc_text"].strip():
        prep_data = preprocess_document(st.session_state["doc_text"])
        
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Raw Characters", f"{prep_data['raw_character_count']:,}")
        col_p2.metric("Cleaned Characters", f"{prep_data['cleaned_character_count']:,}")
        col_p3.metric("Characters Cleaned", f"{prep_data['characters_saved']:,}")
        
        col_sec, col_chunk = st.columns(2)
        with col_sec:
            st.markdown(f"#### 📑 Identified Sections ({prep_data['section_count']})")
            if prep_data["sections_identified"]:
                for s in prep_data["sections_identified"]:
                    st.write(f"• **{s['section_type']}** (Line {s['line_number']}) — *\"{s['header_text']}\"*")
            else:
                st.write("No standard section headers detected. Whole document treated as continuous text.")
                
        with col_chunk:
            st.markdown(f"#### 🧩 Document Chunks ({prep_data['chunk_count']})")
            if prep_data["chunk_count"] > 1:
                st.warning(f"Document is long: Divided into {prep_data['chunk_count']} chunks for safe LLM processing.")
            else:
                st.success("Document fits within single context window (1 chunk).")
                
            for c in prep_data["chunks"]:
                with st.expander(f"Chunk {c['chunk_id']} ({len(c['text']):,} chars)"):
                    st.text(c["text"][:300] + "...")
                    
        with st.expander("✨ View Normalized & Cleaned Text"):
            st.text_area("Cleaned Content", prep_data["cleaned_text"], height=250, disabled=True)
    else:
        st.info("Please load a document in Tab 1 to see preprocessing results.")

# ----------------- TAB 3: STRUCTURED ANALYSIS -----------------
with tab_analyze:
    st.subheader("Part C & D – Structured Legal Analysis (Q4 & Q7)")
    st.write("Generates the complete structured extraction matching the syllabus specification.")
    
    if st.button("🚀 Analyze Document with GPT-4 / Ollama", type="primary", use_container_width=True):
        if not st.session_state["doc_text"].strip():
            st.warning("Please load a document first in Tab 1!")
        else:
            prep_data = preprocess_document(st.session_state["doc_text"])
            cleaned = prep_data["cleaned_text"]
            chunks = prep_data["chunks"]
            
            engine_arg = "openai" if engine_choice == "OpenAI GPT-4" else ("ollama" if "Ollama" in engine_choice else "rule_based")
            
            with st.spinner("🤖 Analyzing legal document..."):
                if len(chunks) > 1:
                    partial_analyses = []
                    for c in chunks:
                        cp = build_analysis_prompt(c["text"], chunk_info=f"Chunk {c['chunk_id']} of {c['total_chunks']}")
                        part_res, _ = generate_legal_response(
                            cp, SYSTEM_PROMPT, engine=engine_arg, model=selected_model, api_key=api_key
                        )
                        partial_analyses.append(part_res)
                    comb_prompt = build_chunk_combination_prompt(partial_analyses)
                    report, eng_used = generate_legal_response(
                        comb_prompt, SYSTEM_PROMPT, engine=engine_arg, model=selected_model, api_key=api_key
                    )
                else:
                    prompt = build_analysis_prompt(cleaned)
                    report, eng_used = generate_legal_response(
                        prompt, SYSTEM_PROMPT, engine=engine_arg, model=selected_model, api_key=api_key
                    )
                    
            st.session_state["analysis_result"] = report
            st.session_state["engine_used"] = eng_used
            st.success(f"Analysis completed successfully using {eng_used}!")
            
    if st.session_state["analysis_result"]:
        st.markdown("### 📋 Analysis Output")
        st.text_area(
            "Structured Legal Analysis",
            st.session_state["analysis_result"],
            height=450
        )

# ----------------- TAB 4: CONCISE SUMMARY -----------------
with tab_summary:
    st.subheader("Part D – Legal Document Summarization (Q5)")
    st.write("Generates a concise abstractive summary matching the syllabus sample output.")
    
    if st.button("📝 Generate Concise Summary", type="primary", use_container_width=True):
        if not st.session_state["doc_text"].strip():
            st.warning("Please load a document first in Tab 1!")
        else:
            prep_data = preprocess_document(st.session_state["doc_text"])
            cleaned = prep_data["cleaned_text"][:4000]
            prompt = build_summary_prompt(cleaned)
            
            engine_arg = "openai" if engine_choice == "OpenAI GPT-4" else ("ollama" if "Ollama" in engine_choice else "rule_based")
            with st.spinner("🤖 Generating concise summary..."):
                summary_res, eng_used = generate_legal_response(
                    prompt, SYSTEM_PROMPT, engine=engine_arg, model=selected_model, api_key=api_key
                )
                
            st.session_state["summary_result"] = summary_res
            st.success(f"Summary generated successfully using {eng_used}!")
            
    if st.session_state["summary_result"]:
        st.markdown("### 📄 Legal Document Summary")
        st.text_area(
            "Concise Summary Output",
            st.session_state["summary_result"],
            height=300
        )

# ----------------- TAB 5: SAVE & EXPORT -----------------
with tab_save:
    st.subheader("Part E – Save Analysis to File (Q6)")
    st.write("Saves the analysis or summary directly to `outputs/legal_analysis.txt`.")
    
    current_content = ""
    if st.session_state["analysis_result"] and st.session_state["summary_result"]:
        current_content = f"{st.session_state['analysis_result']}\n\n{'=' * 50}\n\n{st.session_state['summary_result']}"
    elif st.session_state["analysis_result"]:
        current_content = st.session_state["analysis_result"]
    elif st.session_state["summary_result"]:
        current_content = st.session_state["summary_result"]
        
    if current_content:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("💾 Save to outputs/legal_analysis.txt", type="primary", use_container_width=True):
                output_dir = os.path.join(base_dir, "outputs")
                path = save_analysis_report(current_content, output_dir=output_dir, filename="legal_analysis.txt")
                st.success(f"Report successfully saved to `{path}`!")
                
        with col_s2:
            st.download_button(
                label="📥 Download legal_analysis.txt",
                data=current_content,
                file_name="legal_analysis.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        st.markdown("#### Preview of Content to Save:")
        st.text_area("Report Preview", current_content, height=250, disabled=True)
    else:
        st.info("No analysis or summary generated yet. Please run Analysis (Tab 3) or Summary (Tab 4) first.")

    st.divider()
    st.markdown("### 📂 Saved Reports in `outputs/`")
    out_dir = os.path.join(base_dir, "outputs")
    reports = list_saved_reports(out_dir)
    if reports:
        selected_rep = st.selectbox("Select a previously saved report:", reports)
        if selected_rep:
            rep_path = os.path.join(out_dir, selected_rep)
            rep_text = read_saved_report(rep_path)
            with st.expander(f"View content of {selected_rep}", expanded=False):
                st.text(rep_text)
    else:
        st.write("No saved reports found in `outputs/` yet.")
