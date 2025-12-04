from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SourceSpan:
	"""Spatial provenance for a snippet on a page or in a DOCX run."""

	page_index: Optional[int] = None
	bbox: Optional[Tuple[float, float, float, float]] = None  # x0, y0, x1, y1 (points)
	source_path: Optional[str] = None
	note: Optional[str] = None


@dataclass
class TextSpan:
	text: str
	span: Optional[SourceSpan] = None
	confidence: Optional[float] = None


@dataclass
class TableCell:
	row: int
	col: int
	text: str
	span: Optional[SourceSpan] = None


@dataclass
class Figure:
	id: str
	caption: Optional[str] = None
	span: Optional[SourceSpan] = None


@dataclass
class DiagramNode:
	id: str
	label: Optional[str] = None
	span: Optional[SourceSpan] = None
	kind: Optional[str] = None  # e.g., "process", "entity", "decision"


@dataclass
class DiagramEdge:
	id: str
	source: str
	target: str
	label: Optional[str] = None
	span: Optional[SourceSpan] = None
	directed: bool = True


@dataclass
class Page:
	index: int
	text_blocks: List[TextSpan] = field(default_factory=list)
	tables: List[List[TableCell]] = field(default_factory=list)
	figures: List[Figure] = field(default_factory=list)
	diagram_nodes: List[DiagramNode] = field(default_factory=list)
	diagram_edges: List[DiagramEdge] = field(default_factory=list)


@dataclass
class Entity:
	id: str
	text: str
	label: str  # e.g., PERSON, ORG, PRODUCT, CONCEPT
	span: Optional[SourceSpan] = None
	confidence: Optional[float] = None
	domain_type: Optional[str] = None  # e.g., dom:Service


@dataclass
class Relation:
	id: str
	subject_id: str
	predicate: str  # e.g., pg:uses, pg:dependsOn
	object_id: str
	span: Optional[SourceSpan] = None
	confidence: Optional[float] = None


@dataclass
class StakeholderPerspective:
	id: str
	actor: str  # may reference an Entity id or literal
	claim: str
	span: Optional[SourceSpan] = None
	confidence: Optional[float] = None


@dataclass
class Dimension:
	id: str
	name: str  # e.g., "latency", "throughput"
	value: Optional[str] = None  # e.g., "100 ms"
	unit: Optional[str] = None
	span: Optional[SourceSpan] = None
	confidence: Optional[float] = None


@dataclass
class DocumentModel:
	sources: List[str]
	title: Optional[str] = None
	pages: List[Page] = field(default_factory=list)
	entities: List[Entity] = field(default_factory=list)
	relations: List[Relation] = field(default_factory=list)
	stakeholders: List[StakeholderPerspective] = field(default_factory=list)
	dimensions: List[Dimension] = field(default_factory=list)
	domain_labels: List[str] = field(default_factory=list)
	extra_metadata: Dict[str, str] = field(default_factory=dict)


