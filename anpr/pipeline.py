"""
pipeline.py

Main entry point for the ANPR module. Ties together:
Camera frame -> VehicleDetector -> PlateDetector -> preprocess -> OCR
-> DetectionEvent

This is the function other code (or a CLI / video loop) should call.
"""

from typing import List, Optional

from detector import VehicleDetector, PlateDetector
from preprocess import preprocess_plate
from ocr import EasyOCREngine, is_valid_plate_format
from event_builder import build_detection_event
from schema import DetectionEvent

# Minimum OCR confidence to accept a plate reading as a real detection.
# Tune this once you have real validation data — don't just guess a number
# and report it as measured accuracy (see contract Section 3).
MIN_CONFIDENCE = 0.5


class ANPRPipeline:
    def __init__(
        self,
        vehicle_detector: VehicleDetector = None,
        plate_detector: PlateDetector = None,
        ocr_engine: EasyOCREngine = None,
        min_confidence: float = MIN_CONFIDENCE,
    ):
        self.vehicle_detector = vehicle_detector or VehicleDetector()
        self.plate_detector = plate_detector or PlateDetector()
        self.ocr_engine = ocr_engine or EasyOCREngine()
        self.min_confidence = min_confidence

    def process_frame(
        self,
        frame,
        camera_id: str,
        latitude: float,
        longitude: float,
        direction: str,
        snapshot_dir: Optional[str] = None,
    ) -> List[DetectionEvent]:
        """
        Runs the full pipeline on a single frame and returns zero or more
        DetectionEvents (one per vehicle with a successfully read plate).
        """
        events: List[DetectionEvent] = []

        vehicles = self.vehicle_detector.detect(frame)

        for vehicle in vehicles:
            x1, y1, x2, y2 = vehicle.bbox
            vehicle_crop = frame[y1:y2, x1:x2]

            plates = self.plate_detector.detect(vehicle_crop)
            if not plates:
                continue

            # Take the highest-confidence plate detection for this vehicle
            plate = max(plates, key=lambda p: p.confidence)
            px1, py1, px2, py2 = plate.bbox
            plate_crop = vehicle_crop[py1:py2, px1:px2]

            processed = preprocess_plate(plate_crop)
            plate_text, ocr_confidence = self.ocr_engine.read(processed)

            if not plate_text or ocr_confidence < self.min_confidence:
                continue
            if not is_valid_plate_format(plate_text):
                # Still worth logging during development, but don't emit
                # a DetectionEvent for garbage OCR output.
                continue

            snapshot_path = None
            if snapshot_dir:
                snapshot_path = self._save_snapshot(plate_crop, snapshot_dir)

            event = build_detection_event(
                plate_number=plate_text,
                confidence=ocr_confidence,
                camera_id=camera_id,
                latitude=latitude,
                longitude=longitude,
                direction=direction,
                vehicle_type=vehicle.vehicle_type,
                snapshot_path=snapshot_path,
            )
            events.append(event)

        return events

    def _save_snapshot(self, image, snapshot_dir: str) -> str:
        import os
        import cv2
        import uuid

        os.makedirs(snapshot_dir, exist_ok=True)
        filename = f"{uuid.uuid4().hex[:8]}.jpg"
        path = os.path.join(snapshot_dir, filename)
        cv2.imwrite(path, image)
        return path


if __name__ == "__main__":
    # Minimal manual smoke-test scaffold — replace with real frame source.
    print("ANPR pipeline module loaded. See tests/test_pipeline.py for usage.")
