from __future__ import annotations

import re
from typing import List, Tuple
from uuid import uuid4

from pdf_grepper.types import StakeholderPerspective, SourceSpan


def extract_stakeholders(texts: List[Tuple[str, SourceSpan | None]]) -> List[StakeholderPerspective]:
	"""
	Heuristics to find actor claims, e.g., 'According to <ORG>', 'We propose', 'Users report'.
	"""
	results: List[StakeholderPerspective] = []
	patterns = [
		(r"According to\s+([A-Z][A-Za-z0-9&\-\s]+)", "citation"),
		(r"\bWe\s+(propose|recommend|report)\b(.*)", "author"),
		(r"\bUsers?\s+(report|complain|prefer)\b(.*)", "user"),
		(r"\bStakeholders?\s+(expect|require|demand)\b(.*)", "stakeholder"),
	]
	for text, span in texts:
		for pat, actor_hint in patterns:
			m = re.search(pat, text)
			if not m:
				continue
			actor = m.group(1) if m.lastindex and m.lastindex >= 1 else actor_hint
			claim = text.strip()
			results.append(
				StakeholderPerspective(
					id=str(uuid4()),
					actor=actor.strip(),
					claim=claim,
					span=span,
					confidence=0.4,
				)
			)
	return results


