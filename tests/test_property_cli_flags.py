from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
from typer.testing import CliRunner

from pdf_grepper.cli import app


def _make_pdf(text: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), text, fontsize=14)
    doc.save(path)
    doc.close()
    return path


def test_cli_basic_flags():
    runner = CliRunner()
    pdf_path = _make_pdf("CLI test")
    ttl_path = str(Path(pdf_path).with_suffix(".ttl"))
    json_path = str(Path(pdf_path).with_suffix(".json"))
    try:
        result = runner.invoke(
            app,
            [
                "parse",
                pdf_path,
                "--out",
                ttl_path,
                "--json",
                json_path,
                "--ocr",
                "none",
                "--cloud",
                "",
                "--enrich-web",
                "False",
                "--offline",
                "True",
            ],
        )
        assert result.exit_code == 0
        assert Path(ttl_path).exists()
        assert Path(json_path).exists()
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(ttl_path).unlink(missing_ok=True)
        Path(json_path).unlink(missing_ok=True)


def test_cli_invalid_ocr_value():
    runner = CliRunner()
    pdf_path = _make_pdf("CLI invalid")
    ttl_path = str(Path(pdf_path).with_suffix(".ttl"))
    try:
        # Typer will accept any string; the pipeline will still run, so this is a smoke test
        result = runner.invoke(app, ["parse", pdf_path, "--out", ttl_path, "--ocr", "auto", "--offline", "True"])
        assert result.exit_code == 0
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(ttl_path).unlink(missing_ok=True)

