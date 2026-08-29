"""
preprocess.py

Stage 3: Image preprocessing — cleans up a raw plate crop before OCR.
Typical steps: grayscale, deskew, denoise, contrast/threshold, resize.

Kept dependency-light (cv2 + numpy) so it's easy to swap steps in/out
while you tune against real plate images.
"""

import cv2
import numpy as np


def to_grayscale(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def denoise(image: np.ndarray) -> np.ndarray:
    return cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)


def enhance_contrast(image: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)


def deskew(image: np.ndarray) -> np.ndarray:
    """Rough deskew based on the minAreaRect of non-zero pixels."""
    coords = np.column_stack(np.where(image > 0))
    if coords.size == 0:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )


def resize_for_ocr(image: np.ndarray, target_height: int = 64) -> np.ndarray:
    h, w = image.shape[:2]
    scale = target_height / h
    return cv2.resize(image, (int(w * scale), target_height), interpolation=cv2.INTER_CUBIC)


def preprocess_plate(plate_crop: np.ndarray) -> np.ndarray:
    """Full pipeline: raw plate crop -> OCR-ready image."""
    gray = to_grayscale(plate_crop)
    denoised = denoise(gray)
    contrasted = enhance_contrast(denoised)
    deskewed = deskew(contrasted)
    resized = resize_for_ocr(deskewed)
    return resized
