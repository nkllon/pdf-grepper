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


# Property 40: Pipeline logging invocation
def test_pipeline_logging_invocation(caplog):
    pdf_path = _make_pdf("Logging test")
    ttl_path = str(Path(pdf_path).with_suffix(".ttl"))
    try:
        with caplog.at_level("INFO", logger="pdf_grepper.pipeline"):
            _ = run_pipeline(
                input_paths=[pdf_path],
                ttl_out=ttl_path,
                json_out=None,
                ocr_mode="none",
                use_cloud=[],
                enrich_web=False,
                offline=True,
            )
        messages = " ".join(rec.message for rec in caplog.records)
        assert "ingest_done" in messages and "ie_done" in messages and "export_done" in messages
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(ttl_path).unlink(missing_ok=True)


# Property 42: Output path logging
def test_output_path_logging(caplog):
    pdf_path = _make_pdf("Out path")
    ttl_path = str(Path(pdf_path).with_suffix(".ttl"))
    try:
        with caplog.at_level("INFO", logger="pdf_grepper.pipeline"):
            _ = run_pipeline(
                input_paths=[pdf_path],
                ttl_out=ttl_path,
                json_out=None,
                ocr_mode="none",
                use_cloud=[],
                enrich_web=False,
                offline=True,
            )
        messages = " ".join(rec.message for rec in caplog.records)
        assert "export_done" in messages and ttl_path in messages
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(ttl_path).unlink(missing_ok=True)

