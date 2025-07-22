import os
import json
from datetime import datetime
import fitz  # PyMuPDF

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"
INPUT_JSON = os.path.join(INPUT_DIR, "input.json")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "result.json")

def auto_generate_input_json(pdf_files):
    return {
        "challenge_info": {
            "challenge_id": "round_1b_002",
            "test_case_name": "auto_generated_case",
            "description": "Auto-generated input based on available PDFs"
        },
        "documents": [{"filename": f, "title": os.path.splitext(f)[0]} for f in pdf_files],
        "persona": {"role": "Generic Persona"},
        "job_to_be_done": {"task": "Analyze documents and extract sections"}
    }

def get_font_stats(doc):
    font_sizes = []
    for page in doc:
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l.get("spans", []):
                    font_sizes.append(round(s["size"], 1))
    unique_sizes = sorted(set(font_sizes), reverse=True)
    return {
        "H1": unique_sizes[0] if len(unique_sizes) > 0 else 20,
        "H2": unique_sizes[1] if len(unique_sizes) > 1 else 16,
        "H3": unique_sizes[2] if len(unique_sizes) > 2 else 13,
    }

def is_heading(text, size, thresholds):
    if size >= thresholds.get("H1", 20):
        return "H1"
    elif size >= thresholds.get("H2", 16):
        return "H2"
    elif size >= thresholds.get("H3", 13):
        return "H3"
    return None

def extract_sections(doc_path):
    doc = fitz.open(doc_path)
    size_thresholds = get_font_stats(doc)
    sections = []

    for page_num, page in enumerate(doc, start=1):
        full_text = page.get_text("dict")
        for block in full_text["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if not text or len(text) > 150:
                        continue
                    level = is_heading(text, span["size"], size_thresholds)
                    if level:
                        importance = {"H1": 1, "H2": 2, "H3": 3}.get(level, 4)
                        snippet = get_snippet_after_heading(page, text)
                        sections.append({
                            "document": os.path.basename(doc_path),
                            "page_number": page_num,
                            "section_title": text,
                            "importance_rank": importance,
                            "refined_text": snippet
                        })
    return sections

def get_snippet_after_heading(page, heading_text):
    full_text = page.get_text()
    parts = full_text.split(heading_text)
    if len(parts) > 1:
        rest = parts[1].strip()
        para = rest.split('\n\n')[0]
        return para.strip()[:600]
    return ""

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: Scan PDFs and generate input.json
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
    input_data = auto_generate_input_json(pdf_files)
    with open(INPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(input_data, f, ensure_ascii=False, indent=2)

    # Step 2: Extract content
    extracted_sections = []
    subsection_analysis = []

    for pdf in pdf_files:
        path = os.path.join(INPUT_DIR, pdf)
        results = extract_sections(path)
        for item in results:
            extracted_sections.append({
                "document": item["document"],
                "page_number": item["page_number"],
                "section_title": item["section_title"],
                "importance_rank": item["importance_rank"]
            })
            subsection_analysis.append({
                "document": item["document"],
                "refined_text": item["refined_text"],
                "page_number": item["page_number"]
            })

    metadata = {
        "input_documents": pdf_files,
        "persona": input_data["persona"]["role"],
        "job_to_be_done": input_data["job_to_be_done"]["task"],
        "processing_timestamp": datetime.now().isoformat()
    }

    result = {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("✅ output/result.json generated")
    print("✅ input/input.json auto-generated")

if __name__ == "__main__":
    main()
