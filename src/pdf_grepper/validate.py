from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rdflib import Graph


@dataclass(frozen=True)
class ShaclValidationResult:
	conforms: bool
	report_text: str
	report_graph: Graph


def validate_with_pyshacl(
	data_graph: Graph,
	shapes_graph: Graph,
	*,
	inference: str = "none",
	advanced: bool = True,
	abort_on_first: bool = False,
	meta_shacl: bool = False,
	debug: bool = False,
) -> ShaclValidationResult:
	"""
	Validate `data_graph` against `shapes_graph` using pySHACL.

	This is intentionally strict and deterministic: no network access, no SPARQL endpoints.
	"""
	try:
		from pyshacl import validate as _pyshacl_validate  # type: ignore
	except Exception as e:  # pragma: no cover
		raise RuntimeError(
			"pyshacl is required for SHACL validation but is not installed. "
			"Install with `uv add pyshacl` (or add to project dependencies)."
		) from e

	conforms, report_graph, report_text = _pyshacl_validate(
		data_graph,
		shacl_graph=shapes_graph,
		inference=inference,
		advanced=advanced,
		abort_on_first=abort_on_first,
		meta_shacl=meta_shacl,
		debug=debug,
	)
	return ShaclValidationResult(conforms=bool(conforms), report_text=str(report_text), report_graph=report_graph)


def load_graph(path: str | Path, *, public_id: Optional[str] = None) -> Graph:
	g = Graph()
	g.parse(str(path), format="turtle", publicID=public_id)
	return g

