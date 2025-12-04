from __future__ import annotations

import os
from typing import Optional

import pytesseract
from PIL import Image


def ocr_image_to_text(image: Image.Image, lang: str = "eng") -> Optional[str]:
	"""
	Run local Tesseract OCR on a PIL image. Requires tesseract in PATH.
	"""
	try:
		config = "--oem 1 --psm 3"
		text = pytesseract.image_to_string(image, lang=lang, config=config)
		return text
	except Exception:
		return None


