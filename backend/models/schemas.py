from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Direction(StrEnum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"
    NORTH_EAST = "NORTH_EAST"
    NORTH_WEST = "NORTH_WEST"
    SOUTH_EAST = "SOUTH_EAST"
    SOUTH_WEST = "SOUTH_WEST"
    UNKNOWN = "UNKNOWN"


class VehicleType(StrEnum):
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    BUS = "bus"
    TRUCK = "truck"
    AUTO = "auto"
    VAN = "van"
    OTHER = "other"
    UNKNOWN = "unknown"


def utc_timestamp(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp must include a UTC offset")
    return value.astimezone(timezone.utc)


class DetectionEvent(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    event_id: str = Field(min_length=1)
    plate_number: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    camera_id: str = Field(min_length=1)
    timestamp: datetime
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    direction: Direction
    vehicle_type: VehicleType
    snapshot_path: str | None = None

    @field_validator("plate_number")
    @classmethod
    def normalize_plate(cls, value: str) -> str:
        normalized = "".join(value.split()).upper()
        if not normalized:
            raise ValueError("plate_number must not be empty")
        return normalized

    @field_validator("timestamp")
    @classmethod
    def require_utc_timestamp(cls, value: datetime) -> datetime:
        return utc_timestamp(value)


class Camera(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    camera_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    road: str = Field(min_length=1)
    direction: Direction


class TrajectoryDetection(BaseModel):
    camera_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    direction: Direction

    @field_validator("timestamp")
    @classmethod
    def require_utc_timestamp(cls, value: datetime) -> datetime:
        return utc_timestamp(value)


class VehicleTrajectory(BaseModel):
    plate_number: str
    first_seen: datetime
    last_seen: datetime
    detections: list[TrajectoryDetection]


class VehicleSummary(BaseModel):
    plate_number: str
    first_seen: datetime
    last_seen: datetime
    detection_count: int
    camera_count: int