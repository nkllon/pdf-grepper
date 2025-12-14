import os
import tempfile
from pathlib import Path

import fitz  # PyMuPDF

from pdf_grepper.pipeline import run_pipeline


def _make_pdf_with_text(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), text, fontsize=14)
    doc.save(path)
    doc.close()
    return path


# Feature: pdf-intelligence-system, Property 26: Offline mode skips web enrichment
def test_offline_mode_skips_web_enrichment(monkeypatch):
    pdf_path = _make_pdf_with_text("architecture system cloud data")
    try:
        import pdf_grepper.enrich.web_search as ws

        def boom(*args, **kwargs):
            raise AssertionError("enrich_terms should not be called when offline")

        monkeypatch.setattr(ws, "enrich_terms", boom)
        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=str(Path(pdf_path).with_suffix(".ttl")),
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=True,
            offline=True,
        )
        assert "enrichment_counts" not in model.extra_metadata
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(str(Path(pdf_path).with_suffix(".ttl"))).unlink(missing_ok=True)


# Feature: pdf-intelligence-system, Property 27: Web enrichment metadata recording
def test_web_enrichment_metadata_recording(monkeypatch):
    pdf_path = _make_pdf_with_text("architecture system cloud data")
    try:
        import pdf_grepper.enrich.web_search as ws

        def fake_enrich(terms, offline=False):
            return {terms[0]: [{"t": 1}, {"t": 2}]}

        monkeypatch.setattr(ws, "enrich_terms", fake_enrich)
        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=str(Path(pdf_path).with_suffix(".ttl")),
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=True,
            offline=False,
        )
        assert "enrichment_counts" in model.extra_metadata
        assert isinstance(model.extra_metadata["enrichment_counts"], str)
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(str(Path(pdf_path).with_suffix(".ttl"))).unlink(missing_ok=True)


# Feature: pdf-intelligence-system, Property 28: Web enrichment resilience
def test_web_enrichment_resilience(monkeypatch):
    pdf_path = _make_pdf_with_text("architecture system cloud data")
    try:
        import pdf_grepper.enrich.web_search as ws

        def raise_err(*args, **kwargs):
            raise RuntimeError("network failed")

        monkeypatch.setattr(ws, "enrich_terms", raise_err)
        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=str(Path(pdf_path).with_suffix(".ttl")),
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=True,
            offline=False,
        )
        # Should complete without enrichment metadata
        assert "enrichment_counts" not in model.extra_metadata
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(str(Path(pdf_path).with_suffix(".ttl"))).unlink(missing_ok=True)

