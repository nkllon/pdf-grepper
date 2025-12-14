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


def test_integration_single_file_offline_cache(tmp_path, monkeypatch):
    p1 = _make_pdf("Integration test")
    ttl_path = str(Path(tmp_path) / "out.ttl")
    cache_dir = str(tmp_path / "cache")
    try:
        m1 = run_pipeline(
            input_paths=[p1],
            ttl_out=ttl_path,
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
            cache_dir=cache_dir,
        )
        assert Path(ttl_path).exists()
        # Second run with cache
        m2 = run_pipeline(
            input_paths=[p1],
            ttl_out=ttl_path,
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
            cache_dir=cache_dir,
        )
        assert m2.extra_metadata.get("cache") == "true"
    finally:
        Path(p1).unlink(missing_ok=True)
        Path(ttl_path).unlink(missing_ok=True)

