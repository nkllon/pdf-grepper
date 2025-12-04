from __future__ import annotations

import os
from typing import Optional

from PIL import Image


class AWSTextractConfigError(RuntimeError):
	pass


def available() -> bool:
	return bool(os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"))


def ocr_image(image: Image.Image) -> Optional[str]:
	"""
	Placeholder for AWS Textract OCR. Requires AWS credentials.
	Currently returns None to keep local-first flow.
	"""
	if not available():
		raise AWSTextractConfigError("AWS credentials not set")
	return None


