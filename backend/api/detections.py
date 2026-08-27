from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.api.errors import ApiError
from backend.db.session import get_db
from backend.models.schemas import DetectionEvent
from backend.services.repositories import create_detection, get_camera, get_detection


router = APIRouter()


@router.post("/detections", status_code=status.HTTP_201_CREATED)
def ingest_detection(
    event: DetectionEvent, session: Session = Depends(get_db)
) -> dict[str, str]:
    if get_camera(session, event.camera_id) is None:
        raise ApiError("CAMERA_NOT_FOUND", f"No camera found for {event.camera_id}", 404)
    if get_detection(session, event.event_id) is not None:
        raise ApiError("DUPLICATE_EVENT", f"Event {event.event_id} already exists", 400)
    try:
        create_detection(session, event)
    except IntegrityError:
        session.rollback()
        raise ApiError("DUPLICATE_EVENT", f"Event {event.event_id} already exists", 400)
    return {"status": "created", "event_id": event.event_id}