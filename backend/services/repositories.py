from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.db_models import Camera, Detection
from backend.models.schemas import DetectionEvent


def list_cameras(session: Session) -> list[Camera]:
    return list(session.scalars(select(Camera).order_by(Camera.camera_id)))


def get_camera(session: Session, camera_id: str) -> Camera | None:
    return session.get(Camera, camera_id)


def get_detection(session: Session, event_id: str) -> Detection | None:
    return session.get(Detection, event_id)


def create_detection(session: Session, event: DetectionEvent) -> Detection:
    detection = Detection(
        event_id=event.event_id,
        plate_number=event.plate_number,
        confidence=event.confidence,
        camera_id=event.camera_id,
        timestamp=event.timestamp,
        latitude=event.latitude,
        longitude=event.longitude,
        direction=event.direction.value,
        vehicle_type=event.vehicle_type.value,
        snapshot_path=event.snapshot_path,
    )
    session.add(detection)
    session.commit()
    session.refresh(detection)
    return detection


def get_vehicle_detections(
    session: Session,
    plate_number: str,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> list[Detection]:
    statement = select(Detection).where(Detection.plate_number == plate_number)
    if start_time is not None:
        statement = statement.where(Detection.timestamp >= start_time)
    if end_time is not None:
        statement = statement.where(Detection.timestamp <= end_time)
    statement = statement.order_by(Detection.timestamp, Detection.event_id)
    return list(session.scalars(statement))