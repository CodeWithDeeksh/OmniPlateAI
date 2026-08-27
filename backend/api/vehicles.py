from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.errors import ApiError
from backend.db.session import get_db
from backend.models.schemas import VehicleSummary, VehicleTrajectory
from backend.services.repositories import get_vehicle_detections
from backend.services.trajectory import reconstruct_trajectory


router = APIRouter()


def normalized_plate(plate_number: str) -> str:
    return "".join(plate_number.split()).upper()


@router.get("/vehicles/{plate_number}", response_model=VehicleSummary)
def vehicle_summary(
    plate_number: str, session: Session = Depends(get_db)
) -> VehicleSummary:
    detections = get_vehicle_detections(session, normalized_plate(plate_number))
    if not detections:
        raise ApiError(
            "VEHICLE_NOT_FOUND",
            f"No detections found for plate {plate_number}",
            404,
        )
    return VehicleSummary(
        plate_number=normalized_plate(plate_number),
        first_seen=detections[0].timestamp,
        last_seen=detections[-1].timestamp,
        detection_count=len(detections),
        camera_count=len({detection.camera_id for detection in detections}),
    )


@router.get("/vehicles/{plate_number}/trajectory", response_model=VehicleTrajectory)
def vehicle_trajectory(
    plate_number: str, session: Session = Depends(get_db)
) -> VehicleTrajectory:
    normalized = normalized_plate(plate_number)
    detections = get_vehicle_detections(session, normalized)
    if not detections:
        raise ApiError(
            "VEHICLE_NOT_FOUND",
            f"No detections found for plate {plate_number}",
            404,
        )
    return reconstruct_trajectory(normalized, detections)