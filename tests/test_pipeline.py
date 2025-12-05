import json
from pathlib import Path
from typing import List

import pytest

from pdf_grepper import pipeline
from pdf_grepper.types import (
    DiagramEdge,
    DiagramNode,
    DocumentModel,
    Page,
    Relation,
    SourceSpan,
    TextSpan,
)


@pytest.fixture
def sample_pdf_path(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("Synthetic PDF placeholder")
    return pdf_path


@pytest.fixture
def sample_docx_path(tmp_path: Path) -> Path:
    from docx import Document

    doc_path = tmp_path / "sample.docx"
    doc = Document()
    doc.add_paragraph("Galactic Network depends on Stellar Link")
    doc.save(doc_path)
    return doc_path


def _document_with_diagrams(source: str, lines: List[str]) -> DocumentModel:
    text_spans = [
        TextSpan(
            text=line,
            span=SourceSpan(page_index=0, source_path=source),
        )
        for line in lines
    ]
    page = Page(
        index=0,
        text_blocks=text_spans,
        diagram_nodes=[
            DiagramNode(
                id="n1",
                label="System",
                span=SourceSpan(page_index=0, source_path=source, bbox=(0, 0, 10, 10)),
                kind="box",
            )
        ],
        diagram_edges=[
            DiagramEdge(
                id="e1",
                source="n1",
                target="n1",
                span=SourceSpan(page_index=0, source_path=source, bbox=(0, 0, 5, 5)),
                directed=False,
            )
        ],
    )
    return DocumentModel(sources=[source], pages=[page])


@pytest.mark.usefixtures("install_stubs")
def test_pipeline_processes_pdf_fixture(monkeypatch, sample_pdf_path: Path, tmp_path: Path):
    def fake_loader(paths, ocr_mode="auto"):
        return _document_with_diagrams(
            str(sample_pdf_path), ["Acme Rocket uses Booster Engine"]
        )

    monkeypatch.setattr(pipeline, "load_pdf_or_docx", fake_loader)
    monkeypatch.setattr(
        pipeline,
        "extract_relations",
        lambda entities, texts: [
            Relation(
                id="r1",
                subject_id=entities[0].id,
                predicate="pg:uses",
                object_id=entities[1].id,
            )
        ]
        if len(entities) >= 2
        else [],
    )

    ttl_path = tmp_path / "output.ttl"
    json_path = tmp_path / "output.json"

    model = pipeline.run_pipeline(
        [str(sample_pdf_path)],
        ttl_out=str(ttl_path),
        json_out=str(json_path),
        ocr_mode="none",
    )

    assert model.entities, "Entities should be detected from PDF text."
    assert any(r.predicate == "pg:uses" for r in model.relations)
    assert model.pages[0].diagram_nodes and model.pages[0].diagram_edges
    assert ttl_path.exists() and "entity/" in ttl_path.read_text()

    with json_path.open() as jf:
        exported = json.load(jf)
    assert exported["entities"], "JSON export should include entities"
    assert exported["pages"][0]["diagram_nodes"], "Diagrams should be preserved in JSON"


@pytest.mark.usefixtures("install_stubs")
def test_pipeline_docx_offline_without_cloud(sample_docx_path: Path, tmp_path: Path):
    ttl_path = tmp_path / "doc.ttl"
    json_path = tmp_path / "doc.json"

    def relation_stub(entities, texts):
        if len(entities) >= 2:
            return [
                Relation(
                    id="r-docx",
                    subject_id=entities[0].id,
                    predicate="pg:dependsOn",
                    object_id=entities[1].id,
                )
            ]
        return []

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(pipeline, "extract_relations", relation_stub)

    model = pipeline.run_pipeline(
        [str(sample_docx_path)],
        ttl_out=str(ttl_path),
        json_out=str(json_path),
        offline=True,
        use_cloud=["openai"],
        enrich_web=True,
    )

    monkeypatch.undo()

    assert model.entities, "Entities should be found in DOCX content"
    assert any(rel.predicate == "pg:dependsOn" for rel in model.relations)
    assert "enrichment_counts" not in model.extra_metadata

    ttl_text = ttl_path.read_text()
    assert "dependsOn" in ttl_text

    exported = json.loads(json_path.read_text())
    assert exported["relations"], "Relations should be exported to JSON"


@pytest.mark.usefixtures("install_stubs")
def test_pipeline_rejects_unsupported_extension(tmp_path: Path):
    bad_path = tmp_path / "note.txt"
    bad_path.write_text("plain text")

    ttl_path = tmp_path / "bad.ttl"

    with pytest.raises(ValueError):
        pipeline.run_pipeline([str(bad_path)], ttl_out=str(ttl_path))
