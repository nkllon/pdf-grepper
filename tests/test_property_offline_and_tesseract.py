import os
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pytest

from pdf_grepper.pipeline import run_pipeline
import pdf_grepper.pdf.ocr as ocr_mod


def _make_pdf(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), text, fontsize=14)
    doc.save(path)
    doc.close()
    return path


# Property 39: Offline mode completeness
def test_offline_mode_completes_end_to_end():
    pdf_path = _make_pdf("Offline test")
    ttl_path = str(Path(pdf_path).with_suffix(".ttl"))
    try:
        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=ttl_path,
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
        )
        assert model is not None
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(ttl_path).unlink(missing_ok=True)


def test_missing_tesseract_raises_in_local_mode(monkeypatch):
    pdf_path = _make_pdf("Needs OCR")
    ttl_path = str(Path(pdf_path).with_suffix(".ttl"))
    try:
        monkeypatch.setattr(ocr_mod, "tesseract_available", lambda: False)
        with pytest.raises(RuntimeError) as excinfo:
            run_pipeline(
                input_paths=[pdf_path],
                ttl_out=ttl_path,
                json_out=None,
                ocr_mode="local",
                use_cloud=[],
                enrich_web=False,
                offline=True,
            )
        assert "Tesseract is not available" in str(excinfo.value)
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(ttl_path).unlink(missing_ok=True)

