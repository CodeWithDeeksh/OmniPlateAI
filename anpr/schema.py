"""
schema.py

Defines the DetectionEvent structure and allowed enum values exactly as
specified in docs/data_contract.md. This is the ONLY place the ANPR
module should define what a DetectionEvent looks like — do not create
alternative versions of this structure elsewhere (see Shared Contract
Rule #1 in the data contract).
"""

from dataclasses import dataclass, asdict
from typing import Optional


# --- Allowed enum values (data_contract.md Section 6 & 7) -----------------

VALID_DIRECTIONS = {
    "NORTH", "SOUTH", "EAST", "WEST",
    "NORTH_EAST", "NORTH_WEST", "SOUTH_EAST", "SOUTH_WEST",
    "UNKNOWN",
}

VALID_VEHICLE_TYPES = {
    "car", "motorcycle", "bus", "truck", "auto", "van", "other", "unknown",
}


@dataclass
class DetectionEvent:
    """Mirrors the DetectionEvent JSON shape in data_contract.md Section 1-2."""

    event_id: str
    plate_number: str
    confidence: float          # 0.0 - 1.0, must reflect real pipeline output
    camera_id: str
    timestamp: str             # ISO 8601 UTC, e.g. 2026-08-25T18:21:32Z
    latitude: float
    longitude: float
    direction: str             # one of VALID_DIRECTIONS
    vehicle_type: str          # one of VALID_VEHICLE_TYPES
    snapshot_path: Optional[str] = None

    def __post_init__(self):
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"confidence must be between 0.0 and 1.0, got {self.confidence}"
            )
        if self.direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"direction must be one of {VALID_DIRECTIONS}, got {self.direction!r}"
            )
        if self.vehicle_type not in VALID_VEHICLE_TYPES:
            raise ValueError(
                f"vehicle_type must be one of {VALID_VEHICLE_TYPES}, "
                f"got {self.vehicle_type!r}"
            )

    def to_dict(self) -> dict:
        """Serializable form matching the exact contract field names/order."""
        return asdict(self)
