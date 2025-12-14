import os
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pytest

from pdf_grepper.pdf import ocr as ocr_mod
from pdf_grepper.pdf.loader import load_pdf_or_docx


def _make_pdf_with_pages(texts):
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    for t in texts:
        page = doc.new_page()
        if t is not None:
            page.insert_text((72, 100), t, fontsize=14)
        # If t is None, leave page blank (sparse text)
    doc.save(path)
    doc.close()
    return path


# Feature: pdf-intelligence-system, Property 4: Auto OCR triggers on sparse text
def test_auto_ocr_triggers_on_sparse_text(monkeypatch):
    pdf_path = _make_pdf_with_pages([None])  # blank page triggers OCR
    try:
        monkeypatch.setattr(ocr_mod, "ocr_image_to_text", lambda img: "OCR TEXT")
        model = load_pdf_or_docx([pdf_path], ocr_mode="auto")
        spans = model.pages[0].text_blocks
        assert any(ts.span and ts.span.note == "ocr" for ts in spans)
        # confidence should be included
        assert any(ts.confidence is not None for ts in spans if ts.span and ts.span.note == "ocr")
    finally:
        Path(pdf_path).unlink(missing_ok=True)


# Feature: pdf-intelligence-system, Property 5: Local OCR mode universality
def test_local_ocr_invoked_for_all_pages(monkeypatch):
    pdf_path = _make_pdf_with_pages(["native text present"])
    try:
        monkeypatch.setattr(ocr_mod, "ocr_image_to_text", lambda img: "OCR LOCAL")
        model = load_pdf_or_docx([pdf_path], ocr_mode="local")
        spans = model.pages[0].text_blocks
        assert any(ts.span and ts.span.note == "ocr" for ts in spans), "OCR span expected in local mode"
    finally:
        Path(pdf_path).unlink(missing_ok=True)


# Feature: pdf-intelligence-system, Property 6: None OCR mode skips processing
def test_none_ocr_mode_skips_processing(monkeypatch):
    pdf_path = _make_pdf_with_pages([None])
    try:
        monkeypatch.setattr(ocr_mod, "ocr_image_to_text", lambda img: "OCR SHOULD NOT RUN")
        model = load_pdf_or_docx([pdf_path], ocr_mode="none")
        spans = model.pages[0].text_blocks
        assert not any(ts.span and ts.span.note == "ocr" for ts in spans)
    finally:
        Path(pdf_path).unlink(missing_ok=True)

