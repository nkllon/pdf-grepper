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


# Feature: pdf-intelligence-system, Property 8: Offline mode prevents cloud calls
def test_offline_mode_prevents_cloud_calls(monkeypatch):
    pdf_path = _make_pdf_with_text("hello")
    try:
        # If refine is called, raise to fail the test
        def boom(*args, **kwargs):
            raise AssertionError("Cloud refine should not be called in offline mode")

        monkeypatch.setenv("OPENAI_API_KEY", "dummy")  # simulate available credentials
        monkeypatch.setenv("PYTHONHASHSEED", "0")
        import pdf_grepper.cloud.openai_ie as openai_ie

        monkeypatch.setattr(openai_ie, "refine_entities_relations", boom)

        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=str(Path(pdf_path).with_suffix(".ttl")),
            json_out=None,
            ocr_mode="none",
            use_cloud=["openai"],
            enrich_web=False,
            offline=True,
        )
        # If we got here, offline prevented cloud invocation
        assert model is not None
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(str(Path(pdf_path).with_suffix(".ttl"))).unlink(missing_ok=True)


# Feature: pdf-intelligence-system, Property 9: Cloud adapter graceful degradation
def test_cloud_adapter_graceful_degradation(monkeypatch):
    pdf_path = _make_pdf_with_text("hello")
    try:
        monkeypatch.setenv("OPENAI_API_KEY", "dummy")  # simulate available credentials
        import pdf_grepper.cloud.openai_ie as openai_ie

        def raise_err(*args, **kwargs):
            raise RuntimeError("adapter failed")

        monkeypatch.setattr(openai_ie, "refine_entities_relations", raise_err)

        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=str(Path(pdf_path).with_suffix(".ttl")),
            json_out=None,
            ocr_mode="none",
            use_cloud=["openai"],
            enrich_web=False,
            offline=False,
        )
        # Should complete even if adapter failed
        assert model is not None
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(str(Path(pdf_path).with_suffix(".ttl"))).unlink(missing_ok=True)

