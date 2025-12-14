from __future__ import annotations

from pathlib import Path

from rdflib import RDF, Namespace

from pdf_grepper.da import build_da_graph
from pdf_grepper.meaning import build_meaning_graph
from pdf_grepper.validate import load_graph, validate_with_pyshacl


DA = Namespace("https://nkllon.org/da#")
M = Namespace("https://nkllon.org/meaning#")


def test_da_output_conforms_to_shacl() -> None:
	pg_graph = load_graph(Path("tests/fixtures/pg_small.ttl"))
	da_graph = build_da_graph(pg_graph=pg_graph)
	shapes = load_graph(Path("shacl/da.shacl.ttl"))

	res = validate_with_pyshacl(da_graph, shapes)
	assert res.conforms, res.report_text

	# sanity: should produce at least one Analysis + Block
	assert any(da_graph.subjects(RDF.type, DA.Analysis))
	assert any(da_graph.subjects(RDF.type, DA.Block))


def test_meaning_output_conforms_to_shacl() -> None:
	pg_graph = load_graph(Path("tests/fixtures/pg_small.ttl"))
	da_graph = build_da_graph(pg_graph=pg_graph)
	m_graph = build_meaning_graph(pg_graph=pg_graph, da_graph=da_graph)
	shapes = load_graph(Path("shacl/meaning.shacl.ttl"))

	res = validate_with_pyshacl(m_graph, shapes)
	assert res.conforms, res.report_text

	# sanity: should produce at least one Claim and one Procedure
	assert any(m_graph.subjects(RDF.type, M.Claim))
	assert any(m_graph.subjects(RDF.type, M.Procedure))

