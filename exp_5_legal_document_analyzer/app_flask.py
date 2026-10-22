import os
import sys
import io

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from flask import Flask, render_template, request, jsonify, send_file
from utils.document_reader import (
    read_from_txt,
    read_from_pdf,
    get_document_metrics
)
from utils.preprocessor import preprocess_document
from utils.prompts import (
    SYSTEM_PROMPT,
    build_enhanced_analysis_prompt,
    build_analysis_prompt,
    build_summary_prompt
)
from utils.llm_client import (
    generate_legal_response,
    is_openai_available,
    get_available_ollama_models,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_OLLAMA_MODEL
)
from utils.report_generator import save_analysis_report

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")


@app.route("/")
def index():
    """Renders the main LegalAI dashboard."""
    ollama_models = get_available_ollama_models()
    default_model = ollama_models[0] if ollama_models else "llama3.2"
    openai_ready = is_openai_available()
    return render_template(
        "index.html",
        ollama_models=ollama_models,
        default_model=default_model,
        openai_ready=openai_ready
    )


@app.route("/sample/<name>")
def get_sample(name):
    """Loads a built-in sample document for instant analysis."""
    sample_map = {
        "service": "sample_service_agreement.txt",
        "employment": "sample_employment_agreement.txt",
        "nda": "sample_nda.txt",
        "pdf": "sample_contract.pdf"
    }
    
    filename = sample_map.get(name.lower())
    if not filename:
        return jsonify({"error": "Unknown sample name"}), 404
        
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Sample file not found on disk"}), 404
        
    if filename.endswith(".pdf"):
        text, pages = read_from_pdf(filepath)
    else:
        text = read_from_txt(filepath)
        pages = 1
        
    metrics = get_document_metrics(text, source_name=filename, page_count=pages)
    
    return jsonify({
        "status": "success",
        "filename": filename,
        "content": text,
        "metrics": metrics
    })


@app.route("/analyze", methods=["POST"])
def analyze_document():
    """
    Main analysis endpoint: accepts text or uploaded file,
    preprocesses, runs LLM analysis, saves report, and returns JSON.
    """
    try:
        raw_text = ""
        doc_name = "Direct Text Input"
        pages = 1
        
        # Check if file was uploaded
        if "file" in request.files and request.files["file"].filename != "":
            uploaded = request.files["file"]
            doc_name = uploaded.filename
            if doc_name.lower().endswith(".pdf"):
                raw_text, pages = read_from_pdf(uploaded.stream)
            else:
                raw_bytes = uploaded.read()
                raw_text = raw_bytes.decode("utf-8", errors="replace")
        else:
            raw_text = request.form.get("content", "").strip()
            
        if not raw_text.strip():
            return jsonify({"status": "error", "message": "No document content provided."}), 400

        # Step 1: Preprocess Document (Part B - Q3)
        prep = preprocess_document(raw_text)
        cleaned_text = prep["cleaned_text"]
        
        # Calculate neat metadata metrics (Part A - Q2)
        metrics = get_document_metrics(cleaned_text, source_name=doc_name, page_count=pages)
        
        # Step 2: Prompt Generation (Part C - Q4)
        engine_type = request.form.get("engine", "ollama").lower()
        model_name = request.form.get("model", "").strip() or (
            DEFAULT_OPENAI_MODEL if engine_type == "openai" else DEFAULT_OLLAMA_MODEL
        )
        api_key = request.form.get("api_key", "").strip() or None

        prompt = build_enhanced_analysis_prompt(cleaned_text)

        # Step 3: LLM Inference (Part D - Q5)
        analysis_report, engine_used = generate_legal_response(
            prompt,
            SYSTEM_PROMPT,
            engine=engine_type,
            model=model_name,
            api_key=api_key
        )

        # Step 4: Save Report to outputs/legal_analysis.txt (Part E - Q6)
        saved_path = save_analysis_report(
            analysis_report,
            output_dir=OUTPUTS_DIR,
            filename="legal_analysis.txt"
        )

        return jsonify({
            "status": "success",
            "document_name": doc_name,
            "metrics": metrics,
            "sections_detected": prep["section_count"],
            "chunks_count": prep["chunk_count"],
            "cleaned_chars": prep["cleaned_character_count"],
            "chars_saved": prep["characters_saved"],
            "engine_used": engine_used,
            "analysis": analysis_report,
            "saved_file": os.path.basename(saved_path)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/download")
def download_report():
    """Serves the generated legal_analysis.txt for download."""
    path = os.path.join(OUTPUTS_DIR, "legal_analysis.txt")
    if not os.path.exists(path):
        return "No analysis report generated yet.", 404
    return send_file(
        path,
        as_attachment=True,
        download_name="legal_analysis.txt",
        mimetype="text/plain"
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n========================================================")
    print(f"  ⚖️  LegalAI Flask Web Application")
    print(f"  Running on: http://127.0.0.1:{port}")
    print(f"  Press Ctrl+C to stop the server.")
    print(f"========================================================\n")
    app.run(host="127.0.0.1", port=port, debug=False)
