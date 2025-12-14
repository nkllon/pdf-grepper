import os
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import pytest

from pdf_grepper.pdf.loader import load_pdf_or_docx


# Feature: pdf-intelligence-system, Property 2: Multi-file provenance tracking
def _make_pdf_with_text(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), text, fontsize=14)
    doc.save(path)
    doc.close()
    return path


def test_multi_file_provenance_tracking():
    p1 = _make_pdf_with_text("Doc1 page")
    p2 = _make_pdf_with_text("Doc2 page")
    try:
        model = load_pdf_or_docx([p1, p2], ocr_mode="none")
        valid_sources = set(model.sources)
        assert valid_sources == {p1, p2}
        for page in model.pages:
            for ts in page.text_blocks:
                assert ts.span is not None
                assert ts.span.source_path in valid_sources
    finally:
        Path(p1).unlink(missing_ok=True)
        Path(p2).unlink(missing_ok=True)


# Feature: pdf-intelligence-system, Property 3: Invalid file error reporting
def test_invalid_file_error_includes_path():
    # Create a bogus file with .pdf extension but invalid content
    fd, bogus_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    Path(bogus_path).write_text("not a real pdf", encoding="utf-8")
    try:
        with pytest.raises(Exception) as excinfo:
            load_pdf_or_docx([bogus_path], ocr_mode="none")
        msg = str(excinfo.value)
        assert bogus_path in msg
    finally:
        Path(bogus_path).unlink(missing_ok=True)

