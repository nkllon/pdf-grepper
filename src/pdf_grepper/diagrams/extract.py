from __future__ import annotations

from typing import List
from uuid import uuid4

import fitz  # PyMuPDF

from pdf_grepper.types import DiagramEdge, DiagramNode, Page, SourceSpan


def extract_diagram_primitives(doc_path: str, page_obj: fitz.Page, page: Page) -> None:
	"""
	Very light extraction of vector shapes as nodes/edges placeholders using PyMuPDF drawings.
	"""
	try:
		drawings = page_obj.get_drawings()
	except Exception:
		return
	for d in drawings:
		# Add rectangles as nodes
		for path in d["items"]:
			if path[0] == "re":  # rectangle
				_, rect, _, _ = path
				node_id = f"n-{uuid4()}"
				page.diagram_nodes.append(
					DiagramNode(
						id=node_id,
						label=None,
						kind="box",
						span=SourceSpan(
							page_index=page.index,
							bbox=(rect.x0, rect.y0, rect.x1, rect.y1),
							source_path=doc_path,
						),
					)
				)
		# Add lines as edges (direction unknown)
		for path in d["items"]:
			if path[0] == "l":  # line
				_, p1, p2 = path
				edge_id = f"e-{uuid4()}"
				# Without association to nodes, keep as anonymous edges
				page.diagram_edges.append(
					DiagramEdge(
						id=edge_id,
						source=f"anon-{edge_id}-s",
						target=f"anon-{edge_id}-t",
						label=None,
						span=SourceSpan(
							page_index=page.index,
							bbox=(min(p1.x, p2.x), min(p1.y, p2.y), max(p1.x, p2.x), max(p1.y, p2.y)),
							source_path=doc_path,
						),
						directed=False,
					)
				)


