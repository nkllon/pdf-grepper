import os
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pytest

from pdf_grepper.pdf.loader import load_pdf_or_docx


# Feature: pdf-intelligence-system, Property 1: PDF loading preserves page structure
def _make_pdf(num_pages: int) -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    for i in range(num_pages):
        page = doc.new_page()
        page.insert_text((72, 100), f"Hello from page {i+1}", fontsize=14)
    doc.save(path)
    doc.close()
    return path


def test_pdf_loading_preserves_page_structure():
    pdf_path = _make_pdf(3)
    try:
        model = load_pdf_or_docx([pdf_path], ocr_mode="none")
        assert len(model.pages) == 3, "Model page count must equal PDF page count"
        # Each page should have at least one text block extracted
        for idx, page in enumerate(model.pages):
            assert page.index == idx
            assert len(page.text_blocks) >= 1
            # Each text block should carry provenance with matching page index
            for ts in page.text_blocks:
                assert ts.text and ts.text.strip()
                assert ts.span is not None
                assert ts.span.page_index == idx
    finally:
        Path(pdf_path).unlink(missing_ok=True)

