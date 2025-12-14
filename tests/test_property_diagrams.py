import os
import tempfile
from pathlib import Path

import fitz  # PyMuPDF

from pdf_grepper.pipeline import run_pipeline


def _make_pdf_with_shapes() -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    page = doc.new_page()
    # Draw a rectangle and a line (vector graphics)
    page.draw_rect(fitz.Rect(100, 100, 200, 160), color=(0, 0, 0), fill=None, width=1)
    page.draw_line(fitz.Point(220, 120), fitz.Point(280, 160), color=(0, 0, 0), width=1)
    doc.save(path)
    doc.close()
    return path


# Feature: pdf-intelligence-system, Property 20: Diagram node structure completeness
def test_diagram_node_structure_completeness():
    pdf_path = _make_pdf_with_shapes()
    try:
        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=str(Path(pdf_path).with_suffix(".ttl")),
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
        )
        nodes = model.pages[0].diagram_nodes
        assert nodes, "Expected at least one diagram node"
        for n in nodes:
            assert n.id
            assert n.span is not None and n.span.bbox is not None
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(str(Path(pdf_path).with_suffix(".ttl"))).unlink(missing_ok=True)


# Feature: pdf-intelligence-system, Property 21: Diagram edge structure completeness
def test_diagram_edge_structure_completeness():
    pdf_path = _make_pdf_with_shapes()
    try:
        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=str(Path(pdf_path).with_suffix(".ttl")),
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
        )
        edges = model.pages[0].diagram_edges
        assert edges, "Expected at least one diagram edge"
        for e in edges:
            assert e.id and e.source and e.target
            assert isinstance(e.directed, bool)
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(str(Path(pdf_path).with_suffix(".ttl"))).unlink(missing_ok=True)


# Feature: pdf-intelligence-system, Property 22: Diagram processing resilience
def test_diagram_processing_resilience(monkeypatch):
    pdf_path = _make_pdf_with_shapes()
    try:
        import pdf_grepper.diagrams.interpret as interpret_mod

        def raise_interpret(page):
            raise RuntimeError("interpret failed")

        monkeypatch.setattr(interpret_mod, "interpret_diagram", raise_interpret)

        model = run_pipeline(
            input_paths=[pdf_path],
            ttl_out=str(Path(pdf_path).with_suffix(".ttl")),
            json_out=None,
            ocr_mode="none",
            use_cloud=[],
            enrich_web=False,
            offline=True,
        )
        # Should still succeed
        assert model is not None
    finally:
        Path(pdf_path).unlink(missing_ok=True)
        Path(str(Path(pdf_path).with_suffix(".ttl"))).unlink(missing_ok=True)

