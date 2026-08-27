import json
from pathlib import Path

from sqlalchemy import select

from backend.db.session import SessionLocal
from backend.models.db_models import Camera, Detection
from backend.models.schemas import DetectionEvent


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_json(filename: str) -> list[dict[str, object]]:
    with (PROJECT_ROOT / "data" / filename).open(encoding="utf-8") as fixture:
        return json.load(fixture)


def seed() -> tuple[int, int]:
    cameras_created = 0
    detections_created = 0
    with SessionLocal() as session:
        for item in load_json("cameras.json"):
            if session.get(Camera, item["camera_id"]) is None:
                session.add(Camera(**item))
                cameras_created += 1
        session.flush()
        for item in load_json("detections.json"):
            event = DetectionEvent.model_validate(item)
            if session.scalar(
                select(Detection.event_id).where(Detection.event_id == event.event_id)
            ) is None:
                session.add(
                    Detection(
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
                )
                detections_created += 1
        session.commit()
    return cameras_created, detections_created


if __name__ == "__main__":
    created_cameras, created_detections = seed()
    print(f"Created {created_cameras} cameras and {created_detections} detections")