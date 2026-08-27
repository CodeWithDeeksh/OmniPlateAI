from datetime import timezone

from backend.models.db_models import Detection
from backend.models.schemas import (
    Direction,
    TrajectoryDetection,
    VehicleTrajectory,
)


def reconstruct_trajectory(
    plate_number: str, detections: list[Detection]
) -> VehicleTrajectory:
    ordered = sorted(detections, key=lambda item: (item.timestamp, item.event_id))
    unique: list[Detection] = []
    seen_observations: set[tuple[str, object]] = set()
    for detection in ordered:
        observation = (detection.camera_id, detection.timestamp)
        if observation not in seen_observations:
            unique.append(detection)
            seen_observations.add(observation)

    trajectory_detections = [
        TrajectoryDetection(
            camera_id=detection.camera_id,
            timestamp=as_utc(detection.timestamp),
            latitude=detection.latitude,
            longitude=detection.longitude,
            direction=Direction(detection.direction),
        )
        for detection in unique
    ]
    return VehicleTrajectory(
        plate_number=plate_number,
        first_seen=as_utc(unique[0].timestamp),
        last_seen=as_utc(unique[-1].timestamp),
        detections=trajectory_detections,
    )


def as_utc(value):
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)