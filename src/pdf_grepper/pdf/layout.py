from __future__ import annotations

from typing import List

from pdf_grepper.types import Page, TextSpan


def consolidate_text(page: Page, min_block_len: int = 20) -> List[str]:
	"""
	Produce consolidated text strings per page by joining short blocks.
	"""
	buf: List[str] = []
	current: List[str] = []
	for ts in page.text_blocks:
		if len(ts.text) < min_block_len:
			current.append(ts.text)
		else:
			if current:
				buf.append(" ".join(current))
				current = []
			buf.append(ts.text)
	if current:
		buf.append(" ".join(current))
	return buf


