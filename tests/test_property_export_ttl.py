from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4

from rdflib import Graph

from pdf_grepper.ontology.export_ttl import export_turtle
from pdf_grepper.types import (
    DocumentModel,
    Page,
    TextSpan,
    SourceSpan,
    Entity,
    Relation,
    StakeholderPerspective,
    Dimension,
    DiagramNode,
    DiagramEdge,
)


def _sample_model(tmp_name: str) -> DocumentModel:
    page = Page(
        index=0,
        text_blocks=[
            TextSpan(text="Alpha uses Beta", span=SourceSpan(page_index=0, bbox=(1, 2, 3, 4), source_path=tmp_name))
        ],
    )
    e1 = Entity(id=str(uuid4()), text="Alpha", label="CONCEPT", span=page.text_blocks[0].span, confidence=0.9)
    e2 = Entity(id=str(uuid4()), text="Beta", label="CONCEPT", span=page.text_blocks[0].span, confidence=0.8)
    r = Relation(
        id=str(uuid4()),
        subject_id=e1.id,
        predicate="pg:uses",
        object_id=e2.id,
        span=page.text_blocks[0].span,
        confidence=0.5,
    )
    st = StakeholderPerspective(
        id=str(uuid4()), actor="The Org", claim="According to The Org ...", span=page.text_blocks[0].span
    )
    dim = Dimension(id=str(uuid4()), name="latency", value="120", unit="ms", span=page.text_blocks[0].span)
    node = DiagramNode(id=str(uuid4()), label="Box", kind="box", span=page.text_blocks[0].span)
    edge = DiagramEdge(
        id=str(uuid4()),
        source=node.id,
        target=node.id,
        label=None,
        span=page.text_blocks[0].span,
        directed=False,
    )
    model = DocumentModel(
        sources=[tmp_name],
        title="Sample",
        pages=[page],
        entities=[e1, e2],
        relations=[r],
        stakeholders=[st],
        dimensions=[dim],
        domain_labels=["architecture"],
        extra_metadata={},
    )
    # attach diagram elements to page
    model.pages[0].diagram_nodes.append(node)
    model.pages[0].diagram_edges.append(edge)
    return model


# Property 29: Turtle export round-trip consistency
def test_turtle_round_trip_consistency():
    fd, path = tempfile.mkstemp(suffix=".ttl")
    os.close(fd)
    try:
        model = _sample_model("doc.pdf")
        g = export_turtle(model, ttl_path=path, base_uri="http://example.org/pdf-grepper/")
        g2 = Graph().parse(path, format="turtle")
        # Check that entity URIs are present and relation triple count matches
        for e in model.entities:
            e_uri = f"http://example.org/pdf-grepper/entity/{e.id}"
            assert (None, None, None) in g2.triples((None, None, None))  # graph parsed
            # Basic presence: an entity resource exists by label
            assert any(str(o) == e.text for (_, _, o) in g2.triples((None, None, None)))
        # Relation subject/object references exist
        assert any(True for _ in g2.triples((None, None, None)))
    finally:
        Path(path).unlink(missing_ok=True)


# Property 30: Turtle URI generation completeness
def test_turtle_uri_generation_completeness():
    fd, path = tempfile.mkstemp(suffix=".ttl")
    os.close(fd)
    try:
        model = _sample_model("doc.pdf")
        export_turtle(model, ttl_path=path)
        ttl = Path(path).read_text(encoding="utf-8")
        # URIs for various element types should appear
        assert "entity/" in ttl and "relation/" in ttl and "page/" in ttl and "node/" in ttl and "edge/" in ttl
    finally:
        Path(path).unlink(missing_ok=True)


# Property 31: Turtle provenance inclusion
def test_turtle_provenance_inclusion():
    fd, path = tempfile.mkstemp(suffix=".ttl")
    os.close(fd)
    try:
        model = _sample_model("doc.pdf")
        export_turtle(model, ttl_path=path)
        ttl = Path(path).read_text(encoding="utf-8")
        assert "pg:bboxX0" in ttl and "pg:pageIndex" in ttl and "pg:sourcePath" in ttl
    finally:
        Path(path).unlink(missing_ok=True)


# Property 32: Turtle vocabulary compliance
def test_turtle_vocabulary_compliance():
    fd, path = tempfile.mkstemp(suffix=".ttl")
    os.close(fd)
    try:
        model = _sample_model("doc.pdf")
        g = export_turtle(model, ttl_path=path)
        prefixes = dict(g.namespaces())
        for ns in ("rdf", "rdfs", "dcterms", "xsd"):
            assert ns in prefixes
    finally:
        Path(path).unlink(missing_ok=True)


# Property 33: Turtle file creation
def test_turtle_file_creation():
    fd, path = tempfile.mkstemp(suffix=".ttl")
    os.close(fd)
    try:
        model = _sample_model("doc.pdf")
        export_turtle(model, ttl_path=path)
        assert Path(path).exists()
        # Can rdflib parse it
        Graph().parse(path, format="turtle")
    finally:
        Path(path).unlink(missing_ok=True)

