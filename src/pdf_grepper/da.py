from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import re
from typing import Dict, List, Optional, Tuple

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import XSD

from pdf_grepper.validate import load_graph


DA = Namespace("https://nkllon.org/da#")
DIM = Namespace("https://nkllon.org/dim#")
QUDT = Namespace("http://qudt.org/schema/qudt/")
UNIT = Namespace("http://qudt.org/vocab/unit/")
PG_DEFAULT = Namespace("http://example.org/pdf-grepper/pg#")


@dataclass(frozen=True)
class PgSpan:
	uri: URIRef
	text: str
	page_index: Optional[int]
	bbox: Optional[Tuple[float, float, float, float]]  # x0, y0, x1, y1


def _coerce_int(v) -> Optional[int]:
	try:
		if v is None:
			return None
		return int(str(v))
	except Exception:
		return None


def _coerce_float(v) -> Optional[float]:
	try:
		if v is None:
			return None
		return float(str(v))
	except Exception:
		return None


def _parse_decimal(v: Optional[str]) -> Optional[Decimal]:
	if v is None:
		return None
	s = v.strip()
	if not s:
		return None
	# fraction like 1/2
	m = re.fullmatch(r"(\d+)\s*/\s*(\d+)", s)
	if m:
		try:
			return Decimal(m.group(1)) / Decimal(m.group(2))
		except Exception:
			return None
	# remove commas
	s = s.replace(",", "")
	try:
		return Decimal(s)
	except InvalidOperation:
		return None


def _best_evidence_span(spans: List[PgSpan], page_index: Optional[int], bbox: Optional[Tuple[float, float, float, float]]) -> Optional[PgSpan]:
	if not spans:
		return None
	if page_index is None:
		return spans[0]
	candidates = [s for s in spans if s.page_index == page_index]
	if not candidates:
		return spans[0]
	if bbox is None:
		return candidates[0]
	x0, y0, x1, y1 = bbox
	cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

	def score(s: PgSpan) -> float:
		if not s.bbox:
			return 1e9
		sx0, sy0, sx1, sy1 = s.bbox
		scx, scy = (sx0 + sx1) / 2.0, (sy0 + sy1) / 2.0
		return abs(scx - cx) + abs(scy - cy)

	return sorted(candidates, key=score)[0]


def _stable_id(*parts: str) -> str:
	h = hashlib.sha256()
	for p in parts:
		h.update(p.encode("utf-8"))
		h.update(b"\x1f")
	return h.hexdigest()[:16]


def _extract_pg_namespace(g: Graph) -> Namespace:
	# Prefer the bound prefix, else fall back to default.
	for prefix, ns in g.namespaces():
		if prefix == "pg":
			return Namespace(str(ns))
	return PG_DEFAULT


def _load_pg_spans(pg_graph: Graph) -> Tuple[Namespace, List[PgSpan]]:
	pg = _extract_pg_namespace(pg_graph)
	spans: List[PgSpan] = []
	for s in pg_graph.subjects(RDF.type, pg.TextSpan):
		text = str(pg_graph.value(s, RDFS.label) or "")
		page_index = _coerce_int(pg_graph.value(s, pg.pageIndex))
		x0 = _coerce_float(pg_graph.value(s, pg.bboxX0))
		y0 = _coerce_float(pg_graph.value(s, pg.bboxY0))
		x1 = _coerce_float(pg_graph.value(s, pg.bboxX1))
		y1 = _coerce_float(pg_graph.value(s, pg.bboxY1))
		bbox = (x0, y0, x1, y1) if None not in (x0, y0, x1, y1) else None
		spans.append(PgSpan(uri=URIRef(s), text=text, page_index=page_index, bbox=bbox))
	return pg, spans


def _find_pg_document(pg_graph: Graph, pg: Namespace) -> Optional[URIRef]:
	for doc in pg_graph.subjects(RDF.type, pg.Document):
		return URIRef(doc)
	return None


def _cluster_spans_into_blocks(spans: List[PgSpan], *, y_gap_threshold: float = 20.0) -> List[List[PgSpan]]:
	# Deterministic clustering: group by page, sort by y0 then x0, start a new block on large y gaps.
	by_page: Dict[int, List[PgSpan]] = {}
	orphans: List[PgSpan] = []
	for s in spans:
		if s.page_index is None or not s.bbox:
			orphans.append(s)
			continue
		by_page.setdefault(s.page_index, []).append(s)

	blocks: List[List[PgSpan]] = []
	for page in sorted(by_page.keys()):
		page_spans = by_page[page]

		def key_fn(x: PgSpan) -> Tuple[float, float]:
			assert x.bbox is not None
			x0, y0, _, _ = x.bbox
			return (y0, x0)

		page_spans = sorted(page_spans, key=key_fn)
		current: List[PgSpan] = []
		prev_y1: Optional[float] = None
		for s in page_spans:
			assert s.bbox is not None
			_, y0, _, y1 = s.bbox
			if not current:
				current = [s]
				prev_y1 = y1
				continue
			if prev_y1 is not None and (y0 - prev_y1) > y_gap_threshold:
				blocks.append(current)
				current = [s]
			else:
				current.append(s)
			prev_y1 = max(prev_y1 or y1, y1)
		if current:
			blocks.append(current)

	# Orphans become their own block(s) so SHACL `hasBlock` is always satisfiable.
	for s in orphans:
		blocks.append([s])
	return blocks


def _axis_rules() -> List[Tuple[URIRef, List[str], Decimal]]:
	return [
		(DIM.SafetyRisk, ["danger", "warning", "caution", "hazard", "shock", "injury", "burn"], Decimal("0.85")),
		(DIM.ToolsRequired, ["tool", "wrench", "screwdriver", "pliers", "allen", "hex"], Decimal("0.65")),
		(DIM.Compliance, ["dispose", "disposal", "permit", "code", "compliance"], Decimal("0.60")),
		(DIM.Cost, ["$", "cost", "price", "fee"], Decimal("0.55")),
		(DIM.Time, ["minute", "minutes", "hour", "hours", "sec", "seconds"], Decimal("0.55")),
		(DIM.Location, ["kitchen", "basement", "garage", "under sink", "undersink"], Decimal("0.50")),
	]


def _normalize_unit_to_qudt(unit_str: Optional[str]) -> Optional[URIRef]:
	if unit_str is None:
		return None
	u = unit_str.strip().lower()
	if not u:
		return None
	# Common, conservative mapping
	if u in {"in", "inch", "inches", "\""}:
		return UNIT.IN
	if u in {"ft", "foot", "feet", "'"}:
		return UNIT.FT
	if u in {"mm", "millimeter", "millimeters"}:
		return UNIT.MilliM
	if u in {"cm", "centimeter", "centimeters"}:
		return UNIT.CentiM
	if u in {"m", "meter", "meters"}:
		return UNIT.M
	return None


def build_da_graph(
	*,
	pg_graph: Graph,
	da_ontology_path: str = "ontology/da.ttl",
	analysis_uri: str = "http://example.org/pdf-grepper/da/analysis/main",
) -> Graph:
	"""
	Create a DA output graph from an existing pg:* parse graph.
	"""
	out = Graph()
	out.parse(da_ontology_path, format="turtle")
	out.bind("da", DA)
	out.bind("dim", DIM)
	out.bind("qudt", QUDT)
	out.bind("unit", UNIT)
	# Keep pg prefix consistent with input (shapes assume default, but this helps readability).
	pg_ns = _extract_pg_namespace(pg_graph)
	out.bind("pg", pg_ns)

	doc_uri = _find_pg_document(pg_graph, pg_ns)
	if doc_uri is None:
		raise ValueError("No pg:Document found in input graph.")

	analysis = URIRef(analysis_uri)
	out.add((analysis, RDF.type, DA.Analysis))
	out.add((analysis, DA.aboutDocument, doc_uri))
	# Minimal pg typing triples so SHACL can validate class constraints without
	# needing to merge the full pg graph into this output.
	out.add((doc_uri, RDF.type, pg_ns.Document))

	_, spans = _load_pg_spans(pg_graph)
	for s in spans:
		out.add((s.uri, RDF.type, pg_ns.TextSpan))

	# Blocks
	blocks = _cluster_spans_into_blocks(spans)
	for i, block_spans in enumerate(blocks):
		b_uri = URIRef(f"{analysis_uri}/block/{i}")
		out.add((b_uri, RDF.type, DA.Block))
		label = (block_spans[0].text or "").strip()
		if len(label) > 80:
			label = label[:77] + "..."
		if not label:
			label = f"Block {i}"
		out.add((b_uri, DA.blockLabel, Literal(label, datatype=XSD.string)))
		out.add((b_uri, DA.spanCount, Literal(len(block_spans), datatype=XSD.integer)))
		for s in block_spans:
			out.add((b_uri, DA.hasEvidenceSpan, s.uri))
		out.add((analysis, DA.hasBlock, b_uri))

	# Observations (keyword rules)
	for axis_uri, keywords, conf in _axis_rules():
		for s in spans:
			t = (s.text or "").lower()
			if not t:
				continue
			if any(k in t for k in keywords):
				oid = _stable_id(str(axis_uri), str(s.uri))
				o_uri = URIRef(f"{analysis_uri}/obs/{oid}")
				out.add((o_uri, RDF.type, DA.Observation))
				out.add((o_uri, DA.dimension, axis_uri))
				out.add((o_uri, DA.confidence, Literal(conf, datatype=XSD.decimal)))
				out.add((o_uri, DA.hasEvidenceSpan, s.uri))
				out.add((analysis, DA.hasObservation, o_uri))

	# Quantity mentions from pg:Dimension
	unit_typed: set[URIRef] = set()
	for d in pg_graph.subjects(RDF.type, pg_ns.Dimension):
		value_raw = pg_graph.value(d, pg_ns.hasValue)
		unit_raw = pg_graph.value(d, pg_ns.hasUnit)
		val = _parse_decimal(str(value_raw) if value_raw is not None else None)
		unit_uri = _normalize_unit_to_qudt(str(unit_raw) if unit_raw is not None else None)
		if val is None or unit_uri is None:
			continue
		page_index = _coerce_int(pg_graph.value(d, pg_ns.pageIndex))
		x0 = _coerce_float(pg_graph.value(d, pg_ns.bboxX0))
		y0 = _coerce_float(pg_graph.value(d, pg_ns.bboxY0))
		x1 = _coerce_float(pg_graph.value(d, pg_ns.bboxX1))
		y1 = _coerce_float(pg_graph.value(d, pg_ns.bboxY1))
		dbox = (x0, y0, x1, y1) if None not in (x0, y0, x1, y1) else None
		ev = _best_evidence_span(spans, page_index, dbox)
		if ev is None:
			continue

		qid = _stable_id(str(d), str(val), str(unit_uri))
		q_uri = URIRef(f"{analysis_uri}/quantity/{qid}")
		out.add((q_uri, RDF.type, DA.QuantityMention))
		out.add((q_uri, DA.numericValue, Literal(val, datatype=XSD.decimal)))
		out.add((q_uri, DA.unit, unit_uri))
		orig = " ".join([x for x in [str(value_raw or "").strip(), str(unit_raw or "").strip()] if x]).strip()
		out.add((q_uri, DA.originalText, Literal(orig, datatype=XSD.string)))
		out.add((q_uri, DA.hasEvidenceSpan, ev.uri))
		out.add((analysis, DA.hasQuantityMention, q_uri))

		unit_typed.add(unit_uri)

	# Ensure any referenced unit nodes satisfy SHACL `sh:class qudt:Unit`
	for u in unit_typed:
		out.add((u, RDF.type, QUDT.Unit))

	return out


def run_da(
	input_ttl: str,
	*,
	out_ttl: str,
	da_ontology_path: str = "ontology/da.ttl",
	analysis_uri: str = "http://example.org/pdf-grepper/da/analysis/main",
) -> Graph:
	pg_graph = load_graph(input_ttl)
	da_graph = build_da_graph(pg_graph=pg_graph, da_ontology_path=da_ontology_path, analysis_uri=analysis_uri)
	da_graph.serialize(destination=out_ttl, format="turtle")
	return da_graph

