from __future__ import annotations

import os
from typing import List, Tuple

from pdf_grepper.types import Entity, Relation, SourceSpan


class OpenAIConfigError(RuntimeError):
	pass


def available() -> bool:
	return bool(os.environ.get("OPENAI_API_KEY"))


def refine_entities_relations(
	entities: List[Entity],
	texts: List[Tuple[str, SourceSpan | None]],
	model: str = "gpt-4o-mini",
) -> tuple[List[Entity], List[Relation]]:
	"""
	Placeholder for OpenAI-based refinement. Requires OPENAI_API_KEY.
	Currently returns inputs unchanged to keep local-first flow.
	"""
	if not available():
		raise OpenAIConfigError("OPENAI_API_KEY not set")
	return entities, []


