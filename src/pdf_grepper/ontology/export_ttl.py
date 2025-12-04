from __future__ import annotations

from typing import Iterable

from rdflib import Graph, Literal, RDF, RDFS, URIRef
from rdflib.namespace import DCTERMS, XSD

from pdf_grepper.ontology.model import make_graph
from pdf_grepper.types import (
	DocumentModel,
	Page,
	Entity,
	Relation,
	StakeholderPerspective,
	Dimension,
	DiagramNode,
	DiagramEdge,
)


def _page_uri(base: str, idx: int) -> URIRef:
	return URIRef(f"{base}page/{idx}")


def _entity_uri(base: str, ent_id: str) -> URIRef:
	return URIRef(f"{base}entity/{ent_id}")


def _relation_uri(base: str, rel_id: str) -> URIRef:
	return URIRef(f"{base}relation/{rel_id}")


def _dimension_uri(base: str, dim_id: str) -> URIRef:
	return URIRef(f"{base}dimension/{dim_id}")


def _diagram_node_uri(base: str, node_id: str) -> URIRef:
	return URIRef(f"{base}node/{node_id}")


def _diagram_edge_uri(base: str, edge_id: str) -> URIRef:
	return URIRef(f"{base}edge/{edge_id}")


def _add_span(g: Graph, ctx, s: URIRef, label: str, span) -> None:
	if span is None:
		return
	if span.source_path:
		g.add((s, ctx.pg.sourcePath, Literal(span.source_path)))
	if span.page_index is not None:
		g.add((s, ctx.pg.pageIndex, Literal(span.page_index, datatype=XSD.integer)))
	if span.bbox:
		x0, y0, x1, y1 = span.bbox
		g.add((s, ctx.pg.bboxX0, Literal(x0, datatype=XSD.float)))
		g.add((s, ctx.pg.bboxY0, Literal(y0, datatype=XSD.float)))
		g.add((s, ctx.pg.bboxX1, Literal(x1, datatype=XSD.float)))
		g.add((s, ctx.pg.bboxY1, Literal(y1, datatype=XSD.float)))
	if span.note:
		g.add((s, DCTERMS.description, Literal(span.note)))


def export_turtle(model: DocumentModel, ttl_path: str, base_uri: str = "http://example.org/pdf-grepper/") -> Graph:
	g, ctx = make_graph(base_uri=base_uri)
	doc_uri = URIRef(f"{base_uri}document/main")
	g.add((doc_uri, RDF.type, ctx.pg.Document))
	for s in model.sources:
		g.add((doc_uri, ctx.pg.hasSource, Literal(s)))
	if model.title:
		g.add((doc_uri, DCTERMS.title, Literal(model.title)))
	if model.domain_labels:
		for lbl in model.domain_labels:
			g.add((doc_uri, ctx.pg.domainLabel, Literal(lbl)))

	# Pages & text
	for p in model.pages:
		page_uri = _page_uri(base_uri, p.index)
		g.add((page_uri, RDF.type, ctx.pg.Page))
		g.add((doc_uri, ctx.pg.hasPage, page_uri))
		for i, ts in enumerate(p.text_blocks):
			ts_uri = URIRef(f"{base_uri}text/{p.index}/{i}")
			g.add((ts_uri, RDF.type, ctx.pg.TextSpan))
			g.add((ts_uri, RDFS.label, Literal(ts.text)))
			g.add((page_uri, ctx.pg.hasText, ts_uri))
			_add_span(g, ctx, ts_uri, "text", ts.span)
			if ts.confidence is not None:
				g.add((ts_uri, ctx.pg.confidence, Literal(ts.confidence, datatype=XSD.float)))

	# Entities
	for e in model.entities:
		e_uri = _entity_uri(base_uri, e.id)
		g.add((e_uri, RDF.type, ctx.pg.Entity))
		g.add((e_uri, RDFS.label, Literal(e.text)))
		g.add((doc_uri, ctx.pg.mentionsEntity, e_uri))
		g.add((e_uri, ctx.pg.entityLabel, Literal(e.label)))
		if e.domain_type:
			g.add((e_uri, RDF.type, ctx.dom[e.domain_type]))
		if e.confidence is not None:
			g.add((e_uri, ctx.pg.confidence, Literal(e.confidence, datatype=XSD.float)))
		_add_span(g, ctx, e_uri, "entity", e.span)

	# Relations
	for r in model.relations:
		r_uri = _relation_uri(base_uri, r.id)
		g.add((r_uri, RDF.type, ctx.pg.Relation))
		g.add((r_uri, ctx.pg.predicate, Literal(r.predicate)))
		g.add((r_uri, ctx.pg.subject, _entity_uri(base_uri, r.subject_id)))
		g.add((r_uri, ctx.pg.object, _entity_uri(base_uri, r.object_id)))
		if r.confidence is not None:
			g.add((r_uri, ctx.pg.confidence, Literal(r.confidence, datatype=XSD.float)))
		_add_span(g, ctx, r_uri, "relation", r.span)
		g.add((doc_uri, ctx.pg.hasRelation, r_uri))

	# Stakeholders
	for s in model.stakeholders:
		s_uri = URIRef(f"{base_uri}stakeholder/{s.id}")
		g.add((s_uri, RDF.type, ctx.pg.Stakeholder))
		g.add((s_uri, RDFS.label, Literal(s.actor)))
		g.add((s_uri, ctx.pg.claim, Literal(s.claim)))
		if s.confidence is not None:
			g.add((s_uri, ctx.pg.confidence, Literal(s.confidence, datatype=XSD.float)))
		_add_span(g, ctx, s_uri, "stakeholder", s.span)
		g.add((doc_uri, ctx.pg.hasStakeholder, s_uri))

	# Dimensions
	for d in model.dimensions:
		d_uri = _dimension_uri(base_uri, d.id)
		g.add((d_uri, RDF.type, ctx.pg.Dimension))
		g.add((d_uri, RDFS.label, Literal(d.name)))
		if d.value:
			g.add((d_uri, ctx.pg.hasValue, Literal(d.value)))
		if d.unit:
			g.add((d_uri, ctx.pg.hasUnit, Literal(d.unit)))
		if d.confidence is not None:
			g.add((d_uri, ctx.pg.confidence, Literal(d.confidence, datatype=XSD.float)))
		_add_span(g, ctx, d_uri, "dimension", d.span)
		g.add((doc_uri, ctx.pg.hasDimension, d_uri))

	# Diagrams
	for p in model.pages:
		for n in p.diagram_nodes:
			n_uri = _diagram_node_uri(base_uri, n.id)
			g.add((n_uri, RDF.type, ctx.pg.Node))
			if n.label:
				g.add((n_uri, RDFS.label, Literal(n.label)))
			if n.kind:
				g.add((n_uri, ctx.pg.kind, Literal(n.kind)))
			_add_span(g, ctx, n_uri, "node", n.span)
			g.add((doc_uri, ctx.pg.hasNode, n_uri))
		for e in p.diagram_edges:
			de_uri = _diagram_edge_uri(base_uri, e.id)
			g.add((de_uri, RDF.type, ctx.pg.Edge))
			g.add((de_uri, ctx.pg.source, _diagram_node_uri(base_uri, e.source)))
			g.add((de_uri, ctx.pg.target, _diagram_node_uri(base_uri, e.target)))
			if e.label:
				g.add((de_uri, RDFS.label, Literal(e.label)))
			g.add((de_uri, ctx.pg.directed, Literal(e.directed)))
			_add_span(g, ctx, de_uri, "edge", e.span)
			g.add((doc_uri, ctx.pg.hasEdge, de_uri))

	# Write TTL
	g.serialize(destination=ttl_path, format="turtle")
	return g


