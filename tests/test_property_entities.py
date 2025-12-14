from __future__ import annotations

from typing import List, Tuple, Optional

from pdf_grepper.ie.entities import extract_entities
from pdf_grepper.types import SourceSpan


# Feature: pdf-intelligence-system, Property 13: Entity extraction invocation
def test_entity_extraction_invocation_returns_list():
    texts: List[Tuple[str, Optional[SourceSpan]]] = [
        ("Alice works at Acme Corp", None),
        ("Bob uses Service X", None),
    ]
    ents = extract_entities(texts)
    assert isinstance(ents, list)
    # Allowed to be empty, but should not be None
    assert ents is not None


# Feature: pdf-intelligence-system, Property 14: Entity unique identifiers
def test_entity_unique_identifiers():
    texts: List[Tuple[str, Optional[SourceSpan]]] = [
        ("Alice met Alice", None),
        ("Acme Corp partners with Acme Corp", None),
    ]
    ents = extract_entities(texts)
    ids = [e.id for e in ents]
    assert len(ids) == len(set(ids)), "All entity IDs must be unique"


# Feature: pdf-intelligence-system, Property 15: Entity deduplication
def test_entity_deduplication_by_normalized_text():
    texts: List[Tuple[str, Optional[SourceSpan]]] = [
        ("Acme Corp builds the Acme Corp Platform", None),
        ("ACME CORP launches ACME Corp Cloud", None),
    ]
    ents = extract_entities(texts)
    normalized = [e.text.lower() for e in ents]
    assert len(normalized) == len(set(normalized)), "Duplicate entities should be deduplicated by normalized text"

