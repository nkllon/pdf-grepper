from __future__ import annotations

import os
from typing import Optional

from PIL import Image


class AzureReadConfigError(RuntimeError):
	pass


def available() -> bool:
	return bool(os.environ.get("AZURE_FORM_RECOGNIZER_ENDPOINT") and os.environ.get("AZURE_FORM_RECOGNIZER_KEY"))


def ocr_image(image: Image.Image) -> Optional[str]:
	"""
	Placeholder for Azure Read OCR. Requires AZURE_* env vars.
	Currently returns None to keep local-first flow.
	"""
	if not available():
		raise AzureReadConfigError("Azure credentials not set")
	return None


