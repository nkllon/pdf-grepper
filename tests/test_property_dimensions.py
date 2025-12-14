from __future__ import annotations

from typing import List, Tuple, Optional

from pdf_grepper.dimensions.discover import discover_dimensions
from pdf_grepper.types import SourceSpan


# Feature: pdf-intelligence-system, Property 23: Dimension structure completeness
def test_dimension_structure_completeness():
    texts: List[Tuple[str, Optional[SourceSpan]]] = [
        ("Latency is 120 ms under load", None),
        ("Throughput reached 500 mb per second", None),
        ("Cost reduced by 10 %", None),
    ]
    dims = discover_dimensions(texts)
    assert dims, "Expected at least one dimension"
    for d in dims:
        assert d.id and d.name

