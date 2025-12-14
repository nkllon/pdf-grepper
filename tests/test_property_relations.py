from __future__ import annotations

from typing import List, Tuple, Optional
from uuid import uuid4

from pdf_grepper.ie.relations import extract_relations
from pdf_grepper.types import Entity, SourceSpan


def _entities_for(texts: List[str]) -> List[Entity]:
    # Create entities whose texts match lowercase tokens in relations patterns
    return [
        Entity(id=str(uuid4()), text=t, label="CONCEPT", span=None, confidence=0.9, domain_type=None)
        for t in texts
    ]


# Feature: pdf-intelligence-system, Property 16: Relation structure completeness
def test_relation_structure_completeness():
    entities = _entities_for(["alpha", "beta", "gamma"])
    texts: List[Tuple[str, Optional[SourceSpan]]] = [
        ("alpha uses beta", None),
        ("gamma depends on alpha", None),
    ]
    rels = extract_relations(entities, texts)
    assert rels, "Expected at least one relation"
    for r in rels:
        assert r.id and r.subject_id and r.predicate and r.object_id


# Feature: pdf-intelligence-system, Property 17: Relation unique identifiers
def test_relation_unique_identifiers():
    entities = _entities_for(["service a", "service b"])
    texts: List[Tuple[str, Optional[SourceSpan]]] = [
        ("service a integrates with service b", None),
        ("service a is part of service b", None),
    ]
    rels = extract_relations(entities, texts)
    ids = [r.id for r in rels]
    assert len(ids) == len(set(ids)), "All relation IDs must be unique"

