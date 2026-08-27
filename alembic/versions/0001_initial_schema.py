"""create initial backend schema

Revision ID: 0001_initial_schema
Revises:
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cameras",
        sa.Column("camera_id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("road", sa.String(255), nullable=False),
        sa.Column("direction", sa.String(32), nullable=False),
    )
    op.create_table(
        "blacklist",
        sa.Column("plate_number", sa.String(32), primary_key=True),
        sa.Column("reason", sa.Text(), nullable=True),
    )
    op.create_table(
        "detections",
        sa.Column("event_id", sa.String(128), primary_key=True),
        sa.Column("plate_number", sa.String(32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("camera_id", sa.String(64), sa.ForeignKey("cameras.camera_id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("direction", sa.String(32), nullable=False),
        sa.Column("vehicle_type", sa.String(32), nullable=False),
        sa.Column("snapshot_path", sa.Text(), nullable=True),
    )
    op.create_index("ix_detections_plate_number", "detections", ["plate_number"])
    op.create_index("ix_detections_plate_timestamp", "detections", ["plate_number", "timestamp"])
    op.create_index("ix_detections_camera_timestamp", "detections", ["camera_id", "timestamp"])
    op.create_table(
        "alerts",
        sa.Column("alert_id", sa.String(128), primary_key=True),
        sa.Column("plate_number", sa.String(32), nullable=False),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("camera_id", sa.String(64), sa.ForeignKey("cameras.camera_id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
    )
    op.create_index("ix_alerts_plate_number", "alerts", ["plate_number"])


def downgrade() -> None:
    op.drop_index("ix_alerts_plate_number", table_name="alerts")
    op.drop_table("alerts")
    op.drop_index("ix_detections_camera_timestamp", table_name="detections")
    op.drop_index("ix_detections_plate_timestamp", table_name="detections")
    op.drop_index("ix_detections_plate_number", table_name="detections")
    op.drop_table("detections")
    op.drop_table("blacklist")
    op.drop_table("cameras")