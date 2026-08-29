"""
event_builder.py

Stage 5: Packages detection + OCR results into a standardized
DetectionEvent (schema.py), which is the ANPR module's ONLY output
per the shared contract.
"""

import uuid
from datetime import datetime, timezone

from schema import DetectionEvent


def new_event_id() -> str:
    return f"evt_{uuid.uuid4().hex[:8]}"


def current_utc_timestamp() -> str:
    """ISO 8601 UTC, matching data_contract.md Section 4, e.g. 2026-08-25T18:21:32Z"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_detection_event(
    plate_number: str,
    confidence: float,
    camera_id: str,
    latitude: float,
    longitude: float,
    direction: str,
    vehicle_type: str,
    snapshot_path: str = None,
    timestamp: str = None,
    event_id: str = None,
) -> DetectionEvent:
    """
    Assembles a DetectionEvent. Raises ValueError (via schema validation)
    if confidence/direction/vehicle_type don't meet the contract's rules —
    fail loudly here rather than let bad data reach the backend.
    """
    return DetectionEvent(
        event_id=event_id or new_event_id(),
        plate_number=plate_number,
        confidence=confidence,
        camera_id=camera_id,
        timestamp=timestamp or current_utc_timestamp(),
        latitude=latitude,
        longitude=longitude,
        direction=direction,
        vehicle_type=vehicle_type,
        snapshot_path=snapshot_path,
    )
