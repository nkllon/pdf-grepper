from __future__ import annotations

from typing import Dict, List

try:
	from duckduckgo_search import DDGS  # type: ignore
except Exception:  # pragma: no cover - optional
	DDGS = None  # type: ignore


def enrich_terms(terms: List[str], offline: bool = True, max_results: int = 3) -> Dict[str, List[dict]]:
	"""
	Optional: use DuckDuckGo search to retrieve snippets for domain inference.
	When offline=True or library not installed, returns empty enrichment.
	"""
	if offline or DDGS is None:
		return {t: [] for t in terms}
	results: Dict[str, List[dict]] = {}
	try:
		with DDGS() as ddgs:
			for t in terms:
				hits = ddgs.text(t, max_results=max_results)
				results[t] = hits or []
	except Exception:
		results = {t: [] for t in terms}
	return results


