import json
import os
import tempfile
from pathlib import Path

import fitz  # PyMuPDF

from pdf_grepper.pipeline import run_pipeline


def _make_pdf(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), text, fontsize=14)
    doc.save(path)
    doc.close()
    return path


# Property 34: JSON export round-trip consistency
def test_json_export_round_trip():
    pdf_path = _make_pdf("Hello world")
    json_path = str(Path(pdf_path).with_suffix(".json"))
    ttl_path = str(Path(pdf_path).with_suffix(".ttl"))
    try:
        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=ttl_path,
            json_out=json_path,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
        )
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        # basic keys check
        assert set(["sources", "pages", "entities", "relations", "stakeholders", "dimensions", "domain_labels"]).issubset(
            data.keys()
        )
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(json_path).unlink(missing_ok=True)
        Path(ttl_path).unlink(missing_ok=True)


# Property 35: JSON completeness
def test_json_completeness():
    pdf_path = _make_pdf("Hello again")
    json_path = str(Path(pdf_path).with_suffix(".json"))
    ttl_path = str(Path(pdf_path).with_suffix(".ttl"))
    try:
        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=ttl_path,
            json_out=json_path,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
        )
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        for key in ["pages", "entities", "relations", "stakeholders", "dimensions"]:
            assert key in data
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(json_path).unlink(missing_ok=True)
        Path(ttl_path).unlink(missing_ok=True)


# Property 36: JSON file creation
def test_json_file_creation():
    pdf_path = _make_pdf("Hello third")
    json_path = str(Path(pdf_path).with_suffix(".json"))
    ttl_path = str(Path(pdf_path).with_suffix(".ttl"))
    try:
        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=ttl_path,
            json_out=json_path,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
        )
        assert Path(json_path).exists()
        # Ensure valid JSON
        json.loads(Path(json_path).read_text(encoding="utf-8"))
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(json_path).unlink(missing_ok=True)
        Path(ttl_path).unlink(missing_ok=True)

