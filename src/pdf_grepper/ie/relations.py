from __future__ import annotations

import re
from typing import List, Tuple
from uuid import uuid4

from pdf_grepper.types import Entity, Relation, SourceSpan


def extract_relations(entities: List[Entity], texts: List[Tuple[str, SourceSpan | None]]) -> List[Relation]:
	"""
	Very lightweight relation mining: looks for patterns like 'X uses Y' or 'X depends on Y'.
	"""
	index_by_text = {e.text.lower(): e for e in entities}
	relations: List[Relation] = []
	patterns = [
		(r"(.+?)\s+uses\s+(.+?)", "pg:uses"),
		(r"(.+?)\s+depends\s+on\s+(.+?)", "pg:dependsOn"),
		(r"(.+?)\s+integrates\s+with\s+(.+?)", "pg:integratesWith"),
		(r"(.+?)\s+is\s+part\s+of\s+(.+?)", "pg:isPartOf"),
	]
	for text, span in texts:
		line = text.strip()
		for pat, pred in patterns:
			for m in re.finditer(pat, line, flags=re.IGNORECASE):
				subj = m.group(1).strip().lower()
				obj = m.group(2).strip().lower()
				subj_e = index_by_text.get(subj)
				obj_e = index_by_text.get(obj)
				if subj_e and obj_e and subj_e.id != obj_e.id:
					relations.append(
						Relation(
							id=str(uuid4()),
							subject_id=subj_e.id,
							predicate=pred,
							object_id=obj_e.id,
							span=span,
							confidence=0.5,
						)
					)
	return relations


