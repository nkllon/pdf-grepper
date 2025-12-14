from __future__ import annotations

from dataclasses import asdict, replace
from typing import Iterable, List, Optional, Tuple
import hashlib
import json
import logging
import os
import random

from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore

from pdf_grepper.dimensions.discover import discover_dimensions
from pdf_grepper.diagrams.extract import extract_diagram_primitives
from pdf_grepper.diagrams.interpret import interpret_diagram
from pdf_grepper.ie.entities import extract_entities
from pdf_grepper.ie.relations import extract_relations
from pdf_grepper.ie.stakeholders import extract_stakeholders
from pdf_grepper.ontology.export_ttl import export_turtle
from pdf_grepper.pdf.layout import consolidate_text
from pdf_grepper.pdf.loader import load_pdf_or_docx
from pdf_grepper.types import (
	DocumentModel,
	Page,
	SourceSpan,
	TextSpan,
	Entity,
	Relation,
	StakeholderPerspective,
	Dimension,
	DiagramNode,
	DiagramEdge,
)

try:
	import numpy as _np  # type: ignore
except Exception:  # pragma: no cover
	_np = None

logger = logging.getLogger("pdf_grepper.pipeline")


def _collect_text_spans(pages: List[Page]) -> List[Tuple[str, Optional[SourceSpan]]]:
	texts: List[Tuple[str, Optional[SourceSpan]]] = []
	for p in pages:
		for ts in p.text_blocks:
			if ts.text and ts.text.strip():
				texts.append((ts.text.strip(), ts.span))
	return texts


def _infer_domain_labels(pages: List[Page], top_k: int = 8) -> List[str]:
	docs = []
	for p in pages:
		docs.extend(consolidate_text(p))
	if not docs:
		return []
	try:
		tf = TfidfVectorizer(
			max_features=256,
			stop_words="english",
			ngram_range=(1, 2),
			token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9\-]+\b",
		)
		X = tf.fit_transform(docs)
		terms = tf.get_feature_names_out()
		scores = X.sum(axis=0).A1
		ranked = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
		return [w for w, _ in ranked[:top_k]]
	except Exception:
		return []


def _hash_file(path: str) -> str:
	h = hashlib.sha256()
	with open(path, "rb") as f:
		for chunk in iter(lambda: f.read(65536), b""):
			h.update(chunk)
	return h.hexdigest()


def _cache_key(
	input_paths: List[str], ocr_mode: str, use_cloud: List[str], enrich_web: bool, offline: bool, base_uri: str
) -> str:
	h = hashlib.sha256()
	for p in sorted(input_paths):
		h.update(_hash_file(p).encode())
	cfg = json.dumps(
		{"ocr": ocr_mode, "cloud": sorted(use_cloud), "enrich": enrich_web, "offline": offline, "base_uri": base_uri},
		sort_keys=True,
	).encode()
	h.update(cfg)
	return h.hexdigest()


def _span_from_dict(d: Optional[dict]) -> Optional[SourceSpan]:
	if not d:
		return None
	return SourceSpan(
		page_index=d.get("page_index"),
		bbox=tuple(d["bbox"]) if d.get("bbox") else None,
		source_path=d.get("source_path"),
		note=d.get("note"),
	)


def _page_from_dict(d: dict) -> Page:
	page = Page(index=d["index"])
	for ts in d.get("text_blocks", []):
		page.text_blocks.append(
			TextSpan(text=ts["text"], span=_span_from_dict(ts.get("span")), confidence=ts.get("confidence"))
		)
	for n in d.get("diagram_nodes", []):
		page.diagram_nodes.append(
			DiagramNode(id=n["id"], label=n.get("label"), span=_span_from_dict(n.get("span")), kind=n.get("kind"))
		)
	for e in d.get("diagram_edges", []):
		page.diagram_edges.append(
			DiagramEdge(
				id=e["id"],
				source=e["source"],
				target=e["target"],
				label=e.get("label"),
				span=_span_from_dict(e.get("span")),
				directed=bool(e.get("directed", True)),
			)
		)
	return page


def _model_from_dict(d: dict) -> DocumentModel:
	model = DocumentModel(
		sources=list(d.get("sources", [])),
		title=d.get("title"),
		pages=[_page_from_dict(p) for p in d.get("pages", [])],
		entities=[
			Entity(
				id=e["id"],
				text=e["text"],
				label=e["label"],
				span=_span_from_dict(e.get("span")),
				confidence=e.get("confidence"),
				domain_type=e.get("domain_type"),
			)
			for e in d.get("entities", [])
		],
		relations=[
			Relation(
				id=r["id"],
				subject_id=r["subject_id"],
				predicate=r["predicate"],
				object_id=r["object_id"],
				span=_span_from_dict(r.get("span")),
				confidence=r.get("confidence"),
			)
			for r in d.get("relations", [])
		],
		stakeholders=[
			StakeholderPerspective(
				id=s["id"],
				actor=s["actor"],
				claim=s["claim"],
				span=_span_from_dict(s.get("span")),
				confidence=s.get("confidence"),
			)
			for s in d.get("stakeholders", [])
		],
		dimensions=[
			Dimension(
				id=dm["id"],
				name=dm["name"],
				value=dm.get("value"),
				unit=dm.get("unit"),
				span=_span_from_dict(dm.get("span")),
				confidence=dm.get("confidence"),
			)
			for dm in d.get("dimensions", [])
		],
		domain_labels=list(d.get("domain_labels", [])),
		extra_metadata=dict(d.get("extra_metadata", {})),
	)
	return model

def run_pipeline(
	input_paths: List[str],
	ttl_out: str,
	json_out: Optional[str] = None,
	ocr_mode: str = "auto",
	use_cloud: List[str] | None = None,
	enrich_web: bool = False,
	offline: bool = False,
	base_uri: str = "http://example.org/pdf-grepper/",
	cache_dir: Optional[str] = None,
) -> DocumentModel:
	use_cloud = use_cloud or []
	# Determinism in offline mode
	if offline:
		try:
			os.environ["PYTHONHASHSEED"] = "0"
		except Exception:
			pass
		random.seed(0)
		if _np is not None:
			try:
				_np.random.seed(0)  # type: ignore
			except Exception:
				pass
	# Cache read
	if cache_dir:
		try:
			os.makedirs(cache_dir, exist_ok=True)
			key = _cache_key(input_paths, ocr_mode, use_cloud, enrich_web, offline, base_uri)
			cache_path = os.path.join(cache_dir, f"{key}.json")
			if os.path.exists(cache_path):
				with open(cache_path, "r", encoding="utf-8") as f:
					data = json.load(f)
				model = _model_from_dict(data)
				model.extra_metadata["cache"] = "true"
				# annotate first available span with cache note
				for p in model.pages:
					for ts in p.text_blocks:
						if ts.span:
							ts.span.note = "cache"
							break
					break
				logger.info("cache_hit key=%s path=%s", key, cache_path)
				return model
		except Exception:
			logger.warning("cache_error", exc_info=True)
	# 1) Ingest
	model = load_pdf_or_docx(input_paths, ocr_mode=ocr_mode)
	logger.info("ingest_done sources=%s pages=%d", input_paths, len(model.pages))

	# 2) Diagram primitives from PDF pages (best-effort)
	try:
		import fitz

		for src in input_paths:
			if not src.lower().endswith(".pdf"):
				continue
			with fitz.open(src) as doc:
				for i, page_obj in enumerate(doc):
					if i < len(model.pages):
						extract_diagram_primitives(src, page_obj, model.pages[i])
						interpret_diagram(model.pages[i])
	except Exception:
		logger.warning("diagram_processing_error", exc_info=True)

	# 3) Information Extraction
	text_spans = _collect_text_spans(model.pages)
	entities = extract_entities(text_spans)
	relations = extract_relations(entities, text_spans)
	stakeholders = extract_stakeholders(text_spans)
	logger.info("ie_done entities=%d relations=%d stakeholders=%d", len(entities), len(relations), len(stakeholders))

	# Optional cloud refinement (stubs return unchanged)
	if "openai" in use_cloud and not offline:
		try:
			from pdf_grepper.cloud.openai_ie import refine_entities_relations

			entities, rel_refined = refine_entities_relations(entities, text_spans)
			if rel_refined:
				relations.extend(rel_refined)
		except Exception:
			# Keep local results
			logger.warning("cloud_refine_error adapter=openai", exc_info=True)

	# 4) Dimensions discovery
	dimensions = discover_dimensions(text_spans)

	# 5) Domain inference (+ optional web enrichment)
	domain_labels = _infer_domain_labels(model.pages)
	if enrich_web and not offline and domain_labels:
		try:
			from pdf_grepper.enrich.web_search import enrich_terms

			enrichment = enrich_terms(domain_labels, offline=False)
			# Attach simple counts as metadata
			model.extra_metadata["enrichment_counts"] = str({k: len(v) for k, v in enrichment.items()})
			logger.info("enrich_done terms=%d", len(domain_labels))
		except Exception:
			logger.warning("enrich_error", exc_info=True)

	# 6) Assemble model
	model.entities = entities
	model.relations = relations
	model.stakeholders = stakeholders
	model.dimensions = dimensions
	model.domain_labels = domain_labels

	# 7) Export
	export_turtle(model, ttl_path=ttl_out, base_uri=base_uri)
	if json_out:
		with open(json_out, "w", encoding="utf-8") as f:
			json.dump(asdict(model), f, ensure_ascii=False, indent=2)
	logger.info("export_done ttl=%s json=%s", ttl_out, json_out or "")
	# Cache write
	if cache_dir:
		try:
			key = _cache_key(input_paths, ocr_mode, use_cloud, enrich_web, offline, base_uri)
			cache_path = os.path.join(cache_dir, f"{key}.json")
			with open(cache_path, "w", encoding="utf-8") as f:
				json.dump(asdict(model), f, ensure_ascii=False, indent=2)
			logger.info("cache_write key=%s path=%s", key, cache_path)
		except Exception:
			logger.warning("cache_write_error", exc_info=True)

	return model


