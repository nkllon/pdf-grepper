import os
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pytest

import pdf_grepper.pdf.loader as loader_mod
from pdf_grepper.pdf.loader import load_pdf_or_docx


def _make_pdf_for_layout():
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    page = doc.new_page()
    # Three blocks at increasing y to test order
    page.insert_text((72, 80), "Block A", fontsize=12)
    page.insert_text((72, 120), "Block B", fontsize=12)
    page.insert_text((72, 160), "Block C", fontsize=12)
    doc.save(path)
    doc.close()
    return path


# Feature: pdf-intelligence-system, Property 10: Layout parsing includes bounding boxes
def test_layout_includes_bounding_boxes():
    pdf_path = _make_pdf_for_layout()
    try:
        model = load_pdf_or_docx([pdf_path], ocr_mode="none")
        spans = model.pages[0].text_blocks
        assert spans, "Expected at least one text block"
        for ts in spans:
            assert ts.span is not None
            assert ts.span.bbox is not None
    finally:
        Path(pdf_path).unlink(missing_ok=True)


# Feature: pdf-intelligence-system, Property 11: Reading order preservation
def test_reading_order_top_to_bottom_then_left_to_right():
    pdf_path = _make_pdf_for_layout()
    try:
        model = load_pdf_or_docx([pdf_path], ocr_mode="none")
        spans = model.pages[0].text_blocks
        # Ensure they are ordered by y ascending (top to bottom)
        y_values = [ts.span.bbox[1] for ts in spans if ts.span and ts.span.bbox]
        assert y_values == sorted(y_values), "Blocks must be ordered top-to-bottom"
    finally:
        Path(pdf_path).unlink(missing_ok=True)


# Feature: pdf-intelligence-system, Property 12: Layout parsing resilience
def test_layout_parsing_resilience(monkeypatch):
    pdf_path = _make_pdf_for_layout()
    try:
        # Force get_text to raise to simulate parsing failure; helper should swallow and continue
        orig = loader_mod.fitz.Page.get_text
        def raise_get_text(self, *args, **kwargs):
            raise RuntimeError("get_text failed")
        monkeypatch.setattr(loader_mod.fitz.Page, "get_text", raise_get_text, raising=True)
        model = load_pdf_or_docx([pdf_path], ocr_mode="none")
        # Should still return model and page, possibly with zero blocks
        assert len(model.pages) == 1
    finally:
        # restore not necessary; monkeypatch handles it
        Path(pdf_path).unlink(missing_ok=True)

