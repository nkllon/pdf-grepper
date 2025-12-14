from __future__ import annotations

import hashlib
import re
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import XSD

from pdf_grepper.da import _extract_pg_namespace, _load_pg_spans
from pdf_grepper.validate import load_graph


M = Namespace("https://nkllon.org/meaning#")
DA = Namespace("https://nkllon.org/da#")
PG_DEFAULT = Namespace("http://example.org/pdf-grepper/pg#")


def _stable_id(*parts: str) -> str:
	h = hashlib.sha256()
	for p in parts:
		h.update(p.encode("utf-8"))
		h.update(b"\x1f")
	return h.hexdigest()[:16]


def _find_pg_document(pg_graph: Graph, pg: Namespace) -> Optional[URIRef]:
	for doc in pg_graph.subjects(RDF.type, pg.Document):
		return URIRef(doc)
	return None


_STEP_RE = re.compile(r"^\s*(?:\(?\d+\)?[.)]|[-*•])\s+(?P<body>.+?)\s*$")


def _is_high_signal_claim(text: str) -> Tuple[bool, str, Decimal, Optional[str]]:
	"""
	Returns (is_claim, polarity, confidence, strength)
	"""
	t = text.strip()
	if not t:
		return (False, "asserts", Decimal("0.0"), None)
	lo = t.lower()

	# hazards / prohibitions
	if any(k in lo for k in ["warning", "danger", "caution", "hazard", "risk of", "shock", "injury", "burn"]):
		return (True, "asserts", Decimal("0.85"), None)
	if any(k in lo for k in ["do not", "never "]):
		return (True, "asserts", Decimal("0.80"), "avoid")

	# directives
	if any(k in lo for k in ["must ", "shall "]):
		return (True, "asserts", Decimal("0.70"), "must")
	if any(k in lo for k in ["should ", "recommended", "recommend "]):
		return (True, "asserts", Decimal("0.60"), "should")
	if lo.endswith(":") and len(lo) <= 80:
		# section-y line: hedge to avoid over-claiming
		return (True, "hedges", Decimal("0.45"), None)

	return (False, "asserts", Decimal("0.0"), None)


def _extract_action_verb(step_body: str) -> str:
	# Very lightweight heuristic: first token that looks like a verb-ish imperative.
	toks = re.split(r"\s+", step_body.strip())
	if not toks:
		return "do"
	first = re.sub(r"[^A-Za-z-]", "", toks[0]).lower()
	return first or "do"


def _sorted_spans_for_order(spans) -> List:
	def key_fn(s) -> Tuple[int, float, float, str]:
		page = s.page_index if s.page_index is not None else 10**9
		if s.bbox:
			x0, y0, _, _ = s.bbox
			return (page, y0, x0, str(s.uri))
		return (page, 10**9, 10**9, str(s.uri))

	return sorted(spans, key=key_fn)


def build_meaning_graph(
	*,
	pg_graph: Graph,
	da_graph: Optional[Graph] = None,
	meaning_ontology_path: str = "ontology/meaning.ttl",
	analysis_uri: str = "http://example.org/pdf-grepper/meaning/run/main",
) -> Graph:
	out = Graph()
	out.parse(meaning_ontology_path, format="turtle")
	# If DA graph is provided, merge it in as context for cross-links (and vocabulary).
	if da_graph is not None:
		out += da_graph

	out.bind("m", M)
	out.bind("da", DA)

	pg_ns = _extract_pg_namespace(pg_graph)
	out.bind("pg", pg_ns)

	doc_uri = _find_pg_document(pg_graph, pg_ns)
	if doc_uri is None:
		raise ValueError("No pg:Document found in input graph.")
	# Minimal pg typing triples for SHACL validation.
	out.add((doc_uri, RDF.type, pg_ns.Document))

	_, spans = _load_pg_spans(pg_graph)
	for s in spans:
		out.add((s.uri, RDF.type, pg_ns.TextSpan))
	spans_sorted = _sorted_spans_for_order(spans)

	# Claims
	for s in spans_sorted:
		is_claim, polarity, conf, strength = _is_high_signal_claim(s.text)
		if not is_claim:
			continue
		cid = _stable_id("claim", str(s.uri), s.text)
		c_uri = URIRef(f"{analysis_uri}/claim/{cid}")
		out.add((c_uri, RDF.type, M.Claim))
		out.add((c_uri, M.polarity, Literal(polarity, datatype=XSD.string)))
		out.add((c_uri, M.confidence, Literal(conf, datatype=XSD.decimal)))
		out.add((c_uri, M.evidenceSpan, s.uri))
		# satisfy sh:or branch via predicate
		out.add((c_uri, M.predicate, Literal("states", datatype=XSD.string)))
		# optional helpful label
		out.add((c_uri, RDFS.label, Literal(s.text.strip(), datatype=XSD.string)))
		if strength:
			out.add((c_uri, M.strength, Literal(strength, datatype=XSD.string)))

	# Procedures / steps from sequences
	step_candidates: List[Tuple] = []
	for s in spans_sorted:
		m = _STEP_RE.match(s.text or "")
		if not m:
			continue
		body = m.group("body").strip()
		if not body:
			continue
		step_candidates.append((s, body))

	# group by page and contiguous ordering
	by_page: Dict[int, List[Tuple]] = {}
	for s, body in step_candidates:
		page = s.page_index if s.page_index is not None else -1
		by_page.setdefault(page, []).append((s, body))

	proc_idx = 0
	for page in sorted(by_page.keys()):
		items = by_page[page]
		# already ordered by spans_sorted; ensure deterministic
		items = sorted(items, key=lambda x: spans_sorted.index(x[0]))

		# simple segmentation: start new procedure when vertical gap is large
		current: List[Tuple] = []
		prev_y1: Optional[float] = None
		for s, body in items:
			if s.bbox:
				_, y0, _, y1 = s.bbox
			else:
				y0, y1 = None, None
			if not current:
				current = [(s, body)]
				prev_y1 = y1
				continue
			if prev_y1 is not None and y0 is not None and (y0 - prev_y1) > 40.0:
				# flush
				if len(current) >= 2:
					pid = _stable_id("proc", str(doc_uri), str(page), str(proc_idx))
					p_uri = URIRef(f"{analysis_uri}/procedure/{pid}")
					out.add((p_uri, RDF.type, M.Procedure))
					out.add((p_uri, M.derivedFromDocument, doc_uri))
					for order, (ss, bb) in enumerate(current, start=1):
						sid = _stable_id("step", str(p_uri), str(order), str(ss.uri))
						step_uri = URIRef(f"{analysis_uri}/step/{sid}")
						out.add((step_uri, RDF.type, M.Step))
						out.add((step_uri, M.stepOrder, Literal(order, datatype=XSD.integer)))
						out.add((step_uri, M.actionVerb, Literal(_extract_action_verb(bb), datatype=XSD.string)))
						out.add((step_uri, M.derivedFromSpan, ss.uri))
						out.add((step_uri, RDFS.label, Literal(bb, datatype=XSD.string)))
						out.add((p_uri, M.hasStep, step_uri))
					proc_idx += 1
				current = [(s, body)]
			else:
				current.append((s, body))
			prev_y1 = max(prev_y1 or (y1 or 0.0), y1 or 0.0) if y1 is not None else prev_y1
		# final flush
		if len(current) >= 2:
			pid = _stable_id("proc", str(doc_uri), str(page), str(proc_idx))
			p_uri = URIRef(f"{analysis_uri}/procedure/{pid}")
			out.add((p_uri, RDF.type, M.Procedure))
			out.add((p_uri, M.derivedFromDocument, doc_uri))
			for order, (ss, bb) in enumerate(current, start=1):
				sid = _stable_id("step", str(p_uri), str(order), str(ss.uri))
				step_uri = URIRef(f"{analysis_uri}/step/{sid}")
				out.add((step_uri, RDF.type, M.Step))
				out.add((step_uri, M.stepOrder, Literal(order, datatype=XSD.integer)))
				out.add((step_uri, M.actionVerb, Literal(_extract_action_verb(bb), datatype=XSD.string)))
				out.add((step_uri, M.derivedFromSpan, ss.uri))
				out.add((step_uri, RDFS.label, Literal(bb, datatype=XSD.string)))
				out.add((p_uri, M.hasStep, step_uri))
			proc_idx += 1

	return out


def run_meaning(
	input_ttl: str,
	*,
	da_ttl: Optional[str],
	out_ttl: str,
	meaning_ontology_path: str = "ontology/meaning.ttl",
	analysis_uri: str = "http://example.org/pdf-grepper/meaning/run/main",
) -> Graph:
	pg_graph = load_graph(input_ttl)
	da_graph = load_graph(da_ttl) if da_ttl else None
	m_graph = build_meaning_graph(
		pg_graph=pg_graph, da_graph=da_graph, meaning_ontology_path=meaning_ontology_path, analysis_uri=analysis_uri
	)
	m_graph.serialize(destination=out_ttl, format="turtle")
	return m_graph

