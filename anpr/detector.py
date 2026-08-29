"""
detector.py

Stage 1: Vehicle detection (YOLOv8n, pretrained on COCO — runs on CPU)
Stage 2: License plate detection (OpenCV Haar cascade, bundled with
         opencv-python — no extra downloads needed)

Both are real, working detectors — not stubs. YOLOv8n was chosen over
larger YOLOv8 variants specifically because it runs at usable speed on
CPU; if you get GPU access later, swap to yolov8s.pt or yolov8m.pt for
better accuracy with no code changes beyond the model_path argument.

The Haar cascade plate detector is a reasonable CPU-only baseline for
rectangular plates at moderate angles. It will produce more false
positives / missed detections than a trained plate-specific YOLO model
— if time allows later, that's the natural upgrade path (same interface).
"""

from dataclasses import dataclass
from typing import List, Tuple
import os

import cv2
import numpy as np

BoundingBox = Tuple[int, int, int, int]  # x1, y1, x2, y2

# COCO class IDs (from YOLOv8's default weights) that map to our
# schema.VALID_VEHICLE_TYPES. COCO has no separate "auto" (auto-rickshaw)
# class — motorcycle is the closest proxy; refine later if needed.
COCO_VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


@dataclass
class VehicleDetection:
    bbox: BoundingBox
    vehicle_type: str   # already mapped to schema.VALID_VEHICLE_TYPES
    confidence: float


@dataclass
class PlateDetection:
    bbox: BoundingBox
    confidence: float


class VehicleDetector:
    """Detects vehicles in a frame using pretrained YOLOv8n (COCO weights)."""

    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.4):
        from ultralytics import YOLO  # lazy import: don't require it just to import this module
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

    def detect(self, frame: np.ndarray) -> List[VehicleDetection]:
        """
        frame: BGR image (numpy array), e.g. from cv2.imread or a video frame
        returns: list of VehicleDetection for car/motorcycle/bus/truck only
        """
        results = self.model.predict(
            frame,
            classes=list(COCO_VEHICLE_CLASSES.keys()),
            conf=self.conf_threshold,
            verbose=False,
        )

        detections: List[VehicleDetection] = []
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                vehicle_type = COCO_VEHICLE_CLASSES.get(cls_id, "unknown")
                detections.append(
                    VehicleDetection(
                        bbox=(x1, y1, x2, y2),
                        vehicle_type=vehicle_type,
                        confidence=conf,
                    )
                )
        return detections


class PlateDetector:
    """Locates license plate regions within a cropped vehicle image
    using OpenCV's bundled Haar cascade classifier."""

    def __init__(self, cascade_name: str = "haarcascade_russian_plate_number.xml"):
        cascade_path = os.path.join(cv2.data.haarcascades, cascade_name)
        self.cascade = cv2.CascadeClassifier(cascade_path)
        if self.cascade.empty():
            raise RuntimeError(f"Failed to load cascade at {cascade_path}")

    def detect(self, vehicle_crop: np.ndarray) -> List[PlateDetection]:
        """
        vehicle_crop: cropped BGR image of a single detected vehicle
        returns: list of PlateDetection (Haar cascades don't give a
                 confidence score, so we use a fixed proxy value —
                 real ranking happens later via OCR confidence)
        """
        if vehicle_crop.size == 0:
            return []

        gray = cv2.cvtColor(vehicle_crop, cv2.COLOR_BGR2GRAY)
        plates = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=4,
            minSize=(60, 20),
        )

        detections: List[PlateDetection] = []
        for (x, y, w, h) in plates:
            detections.append(
                PlateDetection(
                    bbox=(x, y, x + w, y + h),
                    confidence=0.5,  # placeholder rank; real confidence comes from OCR stage
                )
            )
        return detections
