from __future__ import annotations

import os
from typing import List, Tuple

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from PIL import Image

from pdf_grepper.types import DocumentModel, Page, SourceSpan, TextSpan
from pdf_grepper.pdf.ocr import ocr_image_to_text, tesseract_available


def _extract_text_blocks_from_page(
	doc_path: str, page: fitz.Page, page_index: int, do_ocr: bool, force_ocr: bool = False
) -> List[TextSpan]:
	blocks: List[TextSpan] = []
	# Try vector text first: collect and sort by (y0, x0) for reading order
	raw_blocks: List[Tuple[float | None, float | None, float | None, float | None, str]] = []
	try:
		for b in page.get_text("blocks"):
			x0, y0, x1, y1, text, *_ = list(b) + [None] * (6 - len(b))
			if not text:
				continue
			raw_blocks.append((y0, x0, x1, y1, str(text)))
	except Exception:
		pass
	# Sort: top-to-bottom (y), then left-to-right (x)
	raw_blocks.sort(key=lambda t: ((t[0] or 0.0), (t[1] or 0.0)))
	for y0, x0, x1, y1, text in raw_blocks:
		blocks.append(
			TextSpan(
				text=text.strip(),
				span=SourceSpan(page_index=page_index, bbox=(x0, y0, x1, y1), source_path=doc_path),
			)
		)

	# OCR: always in local mode (force_ocr), or on sparse text in auto mode
	if do_ocr and (force_ocr or len(" ".join(tb.text for tb in blocks)) < 20):
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
			try:
				# Ensure Tesseract presence when local OCR is requested
				if ocr_mode == "local" and not tesseract_available():
					raise RuntimeError("Tesseract is not available but ocr_mode='local' was requested")
				with fitz.open(path) as doc:
					for i, page in enumerate(doc):
						do_ocr = ocr_mode in {"local", "auto"}
						force_ocr = ocr_mode == "local"
						blocks = _extract_text_blocks_from_page(
							path, page, i, do_ocr=do_ocr, force_ocr=force_ocr
						)
						pages.append(Page(index=len(pages), text_blocks=blocks))
			except Exception as e:
				raise ValueError(f"Failed to open PDF: {path}: {e}") from e
		elif ext == ".docx":
			try:
				docx = DocxDocument(path)
			except Exception as e:
				raise ValueError(f"Failed to open DOCX: {path}: {e}") from e
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


