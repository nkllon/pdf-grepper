from __future__ import annotations

import re
from typing import List, Optional, Tuple
from uuid import uuid4

try:
	import spacy  # type: ignore
except Exception:  # pragma: no cover - optional
	spacy = None  # type: ignore

from pdf_grepper.types import Entity, SourceSpan

COMMON_ENTITY_LABELS = {"PERSON", "ORG", "GPE", "PRODUCT", "FAC", "LOC", "EVENT"}


def _load_nlp() -> Optional["spacy.Language"]:
	if spacy is None:
		return None
	try:
		return spacy.load("en_core_web_sm")
	except Exception:
		# fallback to blank pipeline
		return spacy.blank("en")


def extract_entities(texts: List[Tuple[str, Optional[SourceSpan]]]) -> List[Entity]:
	"""
	Extract entities from list of (text, span) using spaCy if available, else regex heuristics.
	"""
	nlp = _load_nlp()
	entities: List[Entity] = []
	if nlp is not None and "ner" in nlp.pipe_names:
		doc = nlp("\n".join(t for t, _ in texts))
		offset = 0
		# Map character offsets to spans; simple approach: assign entire doc span to None
		for ent in doc.ents:
			label = ent.label_
			if label not in COMMON_ENTITY_LABELS:
				continue
			entities.append(
				Entity(
					id=str(uuid4()),
					text=ent.text,
					label=label,
					span=None,
					confidence=None,
				)
			)
	else:
		# Simple heuristic: Proper noun sequences (capitalized words) as ORG/PRODUCT/CONCEPT
		proper_noun_pattern = re.compile(r"(?:[A-Z][a-zA-Z0-9\-]+(?:\s+[A-Z][a-zA-Z0-9\-]+)+)")
		seen = set()
		for text, span in texts:
			for m in proper_noun_pattern.finditer(text):
				val = m.group(0).strip()
				key = val.lower()
				if key in seen:
					continue
				seen.add(key)
				entities.append(
					Entity(
						id=str(uuid4()),
						text=val,
						label="CONCEPT",
						span=span,
						confidence=0.4,
					)
				)
	# Deduplicate across both branches by normalized text
	unique_by_text: dict[str, Entity] = {}
	for e in entities:
		key = e.text.lower().strip()
		if key not in unique_by_text:
			unique_by_text[key] = e
	return list(unique_by_text.values())


