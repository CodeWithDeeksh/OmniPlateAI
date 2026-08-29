"""
ocr.py

Stage 4: OCR — reads characters off a preprocessed plate image.

Uses EasyOCR by default (handles varied fonts/plate styles reasonably
well out of the box). Swap `EasyOCREngine` for Tesseract or PaddleOCR
if you find they perform better on your dataset — just keep the same
`.read(image) -> (text, confidence)` interface so pipeline.py doesn't
need to change.
"""

import re
from typing import Tuple

# Indian plate format sanity check, e.g. KA01AB1234 / KA-01-AB-1234
PLATE_PATTERN = re.compile(r"^[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{1,4}$")


def clean_plate_text(raw_text: str) -> str:
    """Uppercase, strip spaces/hyphens, drop non-alphanumeric noise."""
    text = raw_text.upper()
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text


def is_valid_plate_format(text: str) -> bool:
    return bool(PLATE_PATTERN.match(text))


class EasyOCREngine:
    def __init__(self, languages=("en",), gpu: bool = False):
        # TODO: lazy-init so importing this module doesn't require the
        # easyocr package / model download unless OCR is actually used
        self._reader = None
        self.languages = list(languages)
        self.gpu = gpu

    def _ensure_loaded(self):
        if self._reader is None:
            import easyocr
            self._reader = easyocr.Reader(self.languages, gpu=self.gpu)

    def read(self, image) -> Tuple[str, float]:
        """
        image: preprocessed plate crop (numpy array)
        returns: (plate_text, confidence) where confidence is 0.0-1.0,
                 matching the DetectionEvent contract's confidence field.
        """
        self._ensure_loaded()
        results = self._reader.readtext(image)
        if not results:
            return "", 0.0

        # Concatenate all detected text fragments, weight confidence by
        # the lowest-confidence fragment (conservative estimate).
        raw_text = "".join(r[1] for r in results)
        confidences = [r[2] for r in results]
        confidence = min(confidences)

        cleaned = clean_plate_text(raw_text)
        return cleaned, float(confidence)
