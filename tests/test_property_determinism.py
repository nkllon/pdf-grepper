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


# Property 43: Deterministic offline processing
def test_deterministic_offline_turtle_output():
    pdf_path = _make_pdf("Determinism test text content")
    ttl1 = str(Path(pdf_path).with_suffix(".1.ttl"))
    ttl2 = str(Path(pdf_path).with_suffix(".2.ttl"))
    try:
        _ = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=ttl1,
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
        )
        _ = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=ttl2,
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
        )
        assert Path(ttl1).read_bytes() == Path(ttl2).read_bytes()
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(ttl1).unlink(missing_ok=True)
        Path(ttl2).unlink(missing_ok=True)

