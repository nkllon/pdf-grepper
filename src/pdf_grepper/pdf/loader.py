from __future__ import annotations

import os
from typing import List, Tuple

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from PIL import Image

from pdf_grepper.types import DocumentModel, Page, SourceSpan, TextSpan
from pdf_grepper.pdf.ocr import ocr_image_to_text


def _extract_text_blocks_from_page(doc_path: str, page: fitz.Page, page_index: int, do_ocr: bool) -> List[TextSpan]:
	blocks: List[TextSpan] = []
	# Try vector text first
	try:
		for b in page.get_text("blocks"):
			x0, y0, x1, y1, text, *_ = list(b) + [None] * (6 - len(b))
			if not text:
				continue
			blocks.append(
				TextSpan(
					text=text.strip(),
					span=SourceSpan(page_index=page_index, bbox=(x0, y0, x1, y1), source_path=doc_path),
				)
			)
	except Exception:
		pass

	# If very little text, attempt OCR
	if do_ocr and len(" ".join(tb.text for tb in blocks)) < 20:
		try:
			pix = page.get_pixmap(dpi=300, alpha=False)
			img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
			text = ocr_image_to_text(img)
			if text and text.strip():
				blocks.append(
					TextSpan(
						text=text.strip(),
						span=SourceSpan(page_index=page_index, bbox=None, source_path=doc_path, note="ocr"),
						confidence=0.6,
					)
				)
		except Exception:
			pass

	return blocks


def load_pdf_or_docx(paths: List[str], ocr_mode: str = "auto") -> DocumentModel:
	"""
	Load one or more sources (PDF/DOCX), returning a single fused DocumentModel with per-page text spans.
	ocr_mode: "none" | "local" | "auto"
	"""
	pages: List[Page] = []
	collected_sources: List[str] = []
	for path in paths:
		collected_sources.append(path)
		ext = os.path.splitext(path)[1].lower()
		if ext == ".pdf":
			with fitz.open(path) as doc:
				for i, page in enumerate(doc):
					do_ocr = (ocr_mode == "local") or (ocr_mode == "auto")
					blocks = _extract_text_blocks_from_page(path, page, i, do_ocr=do_ocr)
					pages.append(Page(index=len(pages), text_blocks=blocks))
		elif ext == ".docx":
			docx = DocxDocument(path)
			texts = []
			for para in docx.paragraphs:
				txt = para.text.strip()
				if txt:
					texts.append(txt)
			blocks = [TextSpan(text=t, span=SourceSpan(page_index=None, source_path=path)) for t in texts]
			# Pack all DOCX content into a synthetic page
			pages.append(Page(index=len(pages), text_blocks=blocks))
		else:
			raise ValueError(f"Unsupported file type: {ext}")

	return DocumentModel(sources=collected_sources, pages=pages)


