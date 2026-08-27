from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


class Camera(Base):
    __tablename__ = "cameras"

    camera_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    road: Mapped[str] = mapped_column(String(255), nullable=False)
    direction: Mapped[str] = mapped_column(String(32), nullable=False)

    detections: Mapped[list["Detection"]] = relationship(back_populates="camera")


class Detection(Base):
    __tablename__ = "detections"
    __table_args__ = (
        Index("ix_detections_plate_timestamp", "plate_number", "timestamp"),
        Index("ix_detections_camera_timestamp", "camera_id", "timestamp"),
    )

    event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    plate_number: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    camera_id: Mapped[str] = mapped_column(ForeignKey("cameras.camera_id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    direction: Mapped[str] = mapped_column(String(32), nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(32), nullable=False)
    snapshot_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    camera: Mapped[Camera] = relationship(back_populates="detections")


class Blacklist(Base):
    __tablename__ = "blacklist"

    plate_number: Mapped[str] = mapped_column(String(32), primary_key=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    alert_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    plate_number: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    camera_id: Mapped[str] = mapped_column(ForeignKey("cameras.camera_id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)