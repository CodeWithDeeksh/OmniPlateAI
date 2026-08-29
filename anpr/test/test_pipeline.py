"""
test_pipeline.py

Contract-focused tests: make sure anything the ANPR module emits actually
matches docs/data_contract.md. Run before every commit (see Development
Rule #9 / step 9 of the workflow).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from schema import DetectionEvent, VALID_DIRECTIONS, VALID_VEHICLE_TYPES
from event_builder import build_detection_event
from ocr import clean_plate_text, is_valid_plate_format


def make_valid_event(**overrides):
    defaults = dict(
        plate_number="KA01AB1234",
        confidence=0.96,
        camera_id="CAM_07",
        latitude=12.9716,
        longitude=77.5946,
        direction="NORTH",
        vehicle_type="car",
    )
    defaults.update(overrides)
    return build_detection_event(**defaults)


def test_valid_event_builds_successfully():
    event = make_valid_event()
    assert isinstance(event, DetectionEvent)
    assert event.plate_number == "KA01AB1234"
    assert event.event_id.startswith("evt_")


def test_event_serializes_to_contract_shape():
    event = make_valid_event()
    d = event.to_dict()
    expected_fields = {
        "event_id", "plate_number", "confidence", "camera_id", "timestamp",
        "latitude", "longitude", "direction", "vehicle_type", "snapshot_path",
    }
    assert set(d.keys()) == expected_fields


def test_confidence_out_of_range_rejected():
    with pytest.raises(ValueError):
        make_valid_event(confidence=1.5)
    with pytest.raises(ValueError):
        make_valid_event(confidence=-0.1)


def test_invalid_direction_rejected():
    with pytest.raises(ValueError):
        make_valid_event(direction="SIDEWAYS")


def test_invalid_vehicle_type_rejected():
    with pytest.raises(ValueError):
        make_valid_event(vehicle_type="spaceship")


def test_all_contract_directions_accepted():
    for d in VALID_DIRECTIONS:
        make_valid_event(direction=d)  # should not raise


def test_all_contract_vehicle_types_accepted():
    for vt in VALID_VEHICLE_TYPES:
        make_valid_event(vehicle_type=vt)  # should not raise


def test_snapshot_path_optional():
    event = make_valid_event()
    assert event.snapshot_path is None


def test_clean_plate_text_strips_noise():
    assert clean_plate_text("ka 01-ab 1234") == "KA01AB1234"
    assert clean_plate_text("KA01AB1234") == "KA01AB1234"


def test_plate_format_validation():
    assert is_valid_plate_format("KA01AB1234") is True
    assert is_valid_plate_format("NOTAPLATE") is False
    assert is_valid_plate_format("") is False
