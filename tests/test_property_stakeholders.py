from __future__ import annotations

from typing import List, Tuple, Optional

from pdf_grepper.ie.stakeholders import extract_stakeholders
from pdf_grepper.types import SourceSpan


# Feature: pdf-intelligence-system, Property 18: Stakeholder structure completeness
def test_stakeholder_structure_completeness():
    texts: List[Tuple[str, Optional[SourceSpan]]] = [
        ("According to The Organization, the system is reliable.", None),
        ("We propose a new architecture for scalability.", None),
        ("Users report improved performance.", None),
        ("Stakeholders require clear SLAs.", None),
    ]
    stakeholders = extract_stakeholders(texts)
    assert stakeholders, "Expected at least one stakeholder"
    for s in stakeholders:
        assert s.id and s.actor and s.claim


# Feature: pdf-intelligence-system, Property 19: Stakeholder unique identifiers
def test_stakeholder_unique_identifiers():
    texts: List[Tuple[str, Optional[SourceSpan]]] = [
        ("According to Big Corp, we achieved milestones.", None),
        ("We recommend adopting best practices.", None),
    ]
    stakeholders = extract_stakeholders(texts)
    ids = [s.id for s in stakeholders]
    assert len(ids) == len(set(ids)), "All stakeholder IDs must be unique"

