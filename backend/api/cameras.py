from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.schemas import Camera
from backend.services.repositories import list_cameras


router = APIRouter()


@router.get("/cameras", response_model=list[Camera])
def cameras(session: Session = Depends(get_db)) -> list[Camera]:
    return list_cameras(session)