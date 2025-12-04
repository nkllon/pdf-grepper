from __future__ import annotations

import re
from typing import List, Tuple
from uuid import uuid4

from pdf_grepper.types import Dimension, SourceSpan

UNITS = [
	"ms",
	"s",
	"sec",
	"seconds",
	"min",
	"minutes",
	"hour",
	"hz",
	"kb",
	"mb",
	"gb",
	"tb",
	"%",
	"usd",
	"$",
	"kg",
	"g",
	"mg",
	"m",
	"cm",
	"mm",
	"km",
]


def discover_dimensions(texts: List[Tuple[str, SourceSpan | None]]) -> List[Dimension]:
	results: List[Dimension] = []
	number_unit = re.compile(r"(\b\d+(?:\.\d+)?\b)\s*([%a-zA-Z$]{1,4})")
	for text, span in texts:
		for m in number_unit.finditer(text):
			val = m.group(1)
			unit = m.group(2).lower()
			if unit not in UNITS:
				continue
			results.append(
				Dimension(
					id=str(uuid4()),
					name="value",
					value=val,
					unit=unit,
					span=span,
					confidence=0.5,
				)
			)
	return results


