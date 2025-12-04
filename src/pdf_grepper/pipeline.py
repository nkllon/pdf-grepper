from __future__ import annotations

from dataclasses import replace
from typing import Iterable, List, Optional, Tuple

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
from pdf_grepper.types import DocumentModel, Page, SourceSpan, TextSpan


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


def run_pipeline(
	input_paths: List[str],
	ttl_out: str,
	json_out: Optional[str] = None,
	ocr_mode: str = "auto",
	use_cloud: List[str] | None = None,
	enrich_web: bool = False,
	offline: bool = False,
	base_uri: str = "http://example.org/pdf-grepper/",
) -> DocumentModel:
	use_cloud = use_cloud or []
	# 1) Ingest
	model = load_pdf_or_docx(input_paths, ocr_mode=ocr_mode)

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
		pass

	# 3) Information Extraction
	text_spans = _collect_text_spans(model.pages)
	entities = extract_entities(text_spans)
	relations = extract_relations(entities, text_spans)
	stakeholders = extract_stakeholders(text_spans)

	# Optional cloud refinement (stubs return unchanged)
	if "openai" in use_cloud and not offline:
		try:
			from pdf_grepper.cloud.openai_ie import refine_entities_relations

			entities, rel_refined = refine_entities_relations(entities, text_spans)
			if rel_refined:
				relations.extend(rel_refined)
		except Exception:
			# Keep local results
			pass

	# 4) Dimensions discovery
	dimensions = discover_dimensions(text_spans)

	# 5) Domain inference (+ optional web enrichment)
	domain_labels = _infer_domain_labels(model.pages)
	if enrich_web and not offline and domain_labels:
		try:
			from pdf_grepper.enrich.web_search import enrich_terms

			enrichment = enrich_terms(domain_labels, offline=False)
			# Attach simple counts as metadata
			model.extra_metadata["enrichment_counts"] = str(
				{k: len(v) for k, v in enrichment.items()}
			)
		except Exception:
			pass

	# 6) Assemble model
	model.entities = entities
	model.relations = relations
	model.stakeholders = stakeholders
	model.dimensions = dimensions
	model.domain_labels = domain_labels

	# 7) Export
	export_turtle(model, ttl_path=ttl_out, base_uri=base_uri)
	if json_out:
		import json
		from dataclasses import asdict

		with open(json_out, "w", encoding="utf-8") as f:
			json.dump(asdict(model), f, ensure_ascii=False, indent=2)

	return model


