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


# Property 37: Cache write and read consistency
def test_cache_write_and_read_consistency(tmp_path):
    pdf_path = _make_pdf("Cache test")
    ttl1 = str(Path(pdf_path).with_suffix(".ttl"))
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    try:
        m1 = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=ttl1,
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
            cache_dir=str(cache_dir),
        )
        # Second run should hit cache
        m2 = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=ttl1,
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
            cache_dir=str(cache_dir),
        )
        assert m1.sources == m2.sources
        assert m1.domain_labels == m2.domain_labels
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(ttl1).unlink(missing_ok=True)


# Property 38: Cache provenance metadata
def test_cache_provenance_metadata(tmp_path):
    pdf_path = _make_pdf("Cache provenance")
    ttl1 = str(Path(pdf_path).with_suffix(".ttl"))
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    try:
        _ = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=ttl1,
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
            cache_dir=str(cache_dir),
        )
        m2 = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=ttl1,
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
            cache_dir=str(cache_dir),
        )
        # Accept either extra_metadata flag or span note
        from_cache_flag = m2.extra_metadata.get("cache") == "true"
        span_note = False
        for p in m2.pages:
            for ts in p.text_blocks:
                if ts.span and ts.span.note == "cache":
                    span_note = True
                    break
        assert from_cache_flag or span_note
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(ttl1).unlink(missing_ok=True)

