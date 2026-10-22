document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.getElementById("fileInput");
    const dropZone = document.getElementById("dropZone");
    const fileSelectedBadge = document.getElementById("fileSelectedBadge");
    const selectedFileName = document.getElementById("selectedFileName");
    const removeFileBtn = document.getElementById("removeFileBtn");
    const documentContent = document.getElementById("documentContent");
    const analyzeForm = document.getElementById("analyzeForm");
    const submitBtn = document.getElementById("submitBtn");
    const loadingBanner = document.getElementById("loadingBanner");
    const resultsSection = document.getElementById("resultsSection");
    const reportViewer = document.getElementById("reportViewer");
    const engineSelect = document.getElementById("engineSelect");
    const openaiKeyBox = document.getElementById("openaiKeyBox");
    const activeEngineText = document.getElementById("activeEngineText");

    // Engine switch handler
    engineSelect.addEventListener("change", (e) => {
        const selected = e.target.value;
        if (selected === "openai") {
            openaiKeyBox.style.display = "block";
            activeEngineText.textContent = "OpenAI GPT-4o";
        } else {
            openaiKeyBox.style.display = "none";
            activeEngineText.textContent = "Connected: Llama 3.2";
        }
    });

    // Dropzone drag & drop
    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add("drag-over");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove("drag-over");
        });
    });

    dropZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            fileInput.files = files;
            showFileSelected(files[0].name);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (fileInput.files.length > 0) {
            showFileSelected(fileInput.files[0].name);
        }
    });

    function showFileSelected(name) {
        selectedFileName.textContent = name;
        fileSelectedBadge.style.display = "inline-flex";
    }

    removeFileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        fileInput.value = "";
        fileSelectedBadge.style.display = "none";
    });

    // Quick Sample Pills
    document.querySelectorAll(".sample-pill").forEach(pill => {
        pill.addEventListener("click", async () => {
            const sampleType = pill.getAttribute("data-sample");
            try {
                pill.style.opacity = "0.5";
                const res = await fetch(`/sample/${sampleType}`);
                const data = await res.json();
                if (data.status === "success") {
                    documentContent.value = data.content;
                    fileInput.value = "";
                    showFileSelected(data.filename);
                } else {
                    alert("Error loading sample: " + data.error);
                }
            } catch (err) {
                console.error(err);
                alert("Failed to fetch sample contract.");
            } finally {
                pill.style.opacity = "1";
            }
        });
    });

    // Topbar new analysis button
    document.getElementById("newAnalysisBtn").addEventListener("click", () => {
        documentContent.value = "";
        fileInput.value = "";
        fileSelectedBadge.style.display = "none";
        resultsSection.style.display = "none";
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    // Format analysis report text into visual structured sections
    function formatReportHtml(reportText) {
        const lines = reportText.split("\n");
        let html = "";
        let currentHeader = "";
        let currentContent = [];

        function flushSection() {
            if (currentHeader || currentContent.length > 0) {
                const headerText = currentHeader || "GENERAL ANALYSIS";
                const bodyText = currentContent.join("\n").trim();
                
                let cardClass = "report-section-card";
                let icon = "📌";
                
                if (headerText.includes("DOCUMENT TYPE")) icon = "📄";
                else if (headerText.includes("SUMMARY")) icon = "📝";
                else if (headerText.includes("PARTIES")) icon = "👥";
                else if (headerText.includes("OBLIGATION")) icon = "🎯";
                else if (headerText.includes("PAYMENT")) icon = "💳";
                else if (headerText.includes("DURATION") || headerText.includes("DATE")) icon = "📅";
                else if (headerText.includes("KEY CLAUSES") || headerText.includes("CLAUSE")) icon = "⚖️";
                else if (headerText.includes("RISK")) {
                    icon = "⚠️";
                    cardClass += " risk-card";
                }
                else if (headerText.includes("MISSING")) {
                    icon = "❓";
                    cardClass += " missing-card";
                }
                else if (headerText.includes("RECOMMENDATION")) {
                    icon = "💡";
                    cardClass += " rec-card";
                }
                else if (headerText.includes("DISCLAIMER")) icon = "ℹ️";

                html += `
                <div class="${cardClass}">
                    <div class="report-section-title">
                        <span>${icon}</span>
                        <span>${escapeHtml(headerText)}</span>
                    </div>
                    <div class="report-section-content">${escapeHtml(bodyText)}</div>
                </div>`;
                currentHeader = "";
                currentContent = [];
            }
        }

        lines.forEach(line => {
            const trimmed = line.trim();
            if (trimmed.startsWith("===") && trimmed.endsWith("===")) {
                flushSection();
                currentHeader = trimmed.replace(/===/g, "").trim();
            } else if (trimmed.startsWith("LEGAL DOCUMENT ANALYSIS") || trimmed.startsWith("--------------------------------")) {
                // Skip syllabus banner lines
            } else {
                currentContent.push(line);
            }
        });

        flushSection();
        return html || `<pre style="white-space: pre-wrap; font-family: inherit;">${escapeHtml(reportText)}</pre>`;
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.innerText = text;
        return div.innerHTML;
    }

    // Submit Form
    analyzeForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const content = documentContent.value.trim();
        const hasFile = fileInput.files.length > 0;

        if (!content && !hasFile) {
            alert("Please choose a file or paste legal document text first.");
            return;
        }

        const formData = new FormData();
        if (hasFile) {
            formData.append("file", fileInput.files[0]);
        }
        formData.append("content", content);
        formData.append("engine", engineSelect.value);

        const apiKeyVal = document.getElementById("apiKeyInput") ? document.getElementById("apiKeyInput").value.trim() : "";
        if (apiKeyVal) {
            formData.append("api_key", apiKeyVal);
        }

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.querySelector(".btn-text").textContent = "Analyzing document with AI...";
        loadingBanner.style.display = "flex";
        resultsSection.style.display = "none";

        try {
            const response = await fetch("/analyze", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.status === "success") {
                // Populate metrics
                document.getElementById("metricDocName").textContent = data.document_name || "Legal Contract";
                document.getElementById("metricWords").textContent = (data.metrics.total_words || 0).toLocaleString();
                document.getElementById("metricChars").textContent = (data.metrics.total_characters || 0).toLocaleString();
                document.getElementById("metricSections").textContent = data.sections_detected || 0;
                document.getElementById("metricEngine").textContent = data.engine_used || "Llama 3.2";

                // Render report
                reportViewer.innerHTML = formatReportHtml(data.analysis);
                resultsSection.style.display = "block";

                // Smooth scroll to results
                resultsSection.scrollIntoView({ behavior: "smooth" });
            } else {
                alert("Analysis failed: " + (data.message || "Unknown error"));
            }
        } catch (err) {
            console.error(err);
            alert("An error occurred during document analysis. Please check console for details.");
        } finally {
            submitBtn.disabled = false;
            submitBtn.querySelector(".btn-text").textContent = "Analyze Document";
            loadingBanner.style.display = "none";
        }
    });
});
