from __future__ import annotations

import os
from typing import Optional

from PIL import Image


class GoogleVisionConfigError(RuntimeError):
	pass


def available() -> bool:
	return bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))


def ocr_image(image: Image.Image) -> Optional[str]:
	"""
	Placeholder for Google Vision OCR. Requires GOOGLE_APPLICATION_CREDENTIALS.
	Currently returns None to keep local-first flow.
	"""
	if not available():
		raise GoogleVisionConfigError("GOOGLE_APPLICATION_CREDENTIALS not set")
	return None


