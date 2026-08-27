from datetime import datetime, timezone

from backend.models.db_models import Detection
from backend.models.schemas import Direction, VehicleType
from backend.services.seed import load_json
from backend.services.trajectory import reconstruct_trajectory


def camera_payload() -> dict[str, object]:
    return {
        "camera_id": "CAM_01",
        "name": "Test Camera",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "road": "Test Road",
        "direction": "EAST",
    }


def detection_payload(event_id: str = "evt_001") -> dict[str, object]:
    return {
        "event_id": event_id,
        "plate_number": "ka01 ab1234",
        "confidence": 0.96,
        "camera_id": "CAM_01",
        "timestamp": "2026-08-25T08:42:00Z",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "direction": "EAST",
        "vehicle_type": "car",
    }


def test_detection_search_and_trajectory(client) -> None:
    cameras = client.get("/api/cameras")
    assert cameras.status_code == 200
    assert cameras.json()[0]["camera_id"] == "CAM_01"

    response = client.post("/api/detections", json=detection_payload())
    assert response.status_code == 201
    assert response.json() == {"status": "created", "event_id": "evt_001"}

    summary = client.get("/api/vehicles/KA01AB1234")
    assert summary.status_code == 200
    assert summary.json()["plate_number"] == "KA01AB1234"
    assert summary.json()["detection_count"] == 1
    assert summary.json()["camera_count"] == 1

    trajectory = client.get("/api/vehicles/ka01 ab1234/trajectory")
    assert trajectory.status_code == 200
    assert trajectory.json()["detections"][0]["camera_id"] == "CAM_01"

    duplicate = client.post("/api/detections", json=detection_payload())
    assert duplicate.status_code == 400
    assert duplicate.json()["error"]["code"] == "DUPLICATE_EVENT"

    invalid = client.post("/api/detections", json={"confidence": 2})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"

    unknown_camera = client.post(
        "/api/detections",
        json={**detection_payload("evt_002"), "camera_id": "CAM_UNKNOWN"},
    )
    assert unknown_camera.status_code == 404
    assert unknown_camera.json()["error"]["code"] == "CAMERA_NOT_FOUND"

    missing_vehicle = client.get("/api/vehicles/KA99ZZ0000")
    assert missing_vehicle.status_code == 404
    assert missing_vehicle.json()["error"]["code"] == "VEHICLE_NOT_FOUND"


def test_health_and_deferred_routes(client) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}
    for path in (
        "/api/analytics/density",
        "/api/analytics/congestion",
        "/api/analytics/od",
        "/api/alerts",
    ):
        response = client.get(path)
        assert response.status_code == 501
        assert response.json()["error"]["code"] == "MODULE_NOT_IMPLEMENTED"


def test_seed_fixtures_are_available() -> None:
    cameras = load_json("cameras.json")
    detections = load_json("detections.json")
    assert len(cameras) == 8
    assert len(detections) == 15


def test_trajectory_orders_and_deduplicates() -> None:
    first = datetime(2026, 8, 25, 8, 42, tzinfo=timezone.utc)
    second = datetime(2026, 8, 25, 8, 50, tzinfo=timezone.utc)
    detections = [
        Detection(event_id="b", plate_number="KA01AB1234", confidence=0.9, camera_id="CAM_02", timestamp=second, latitude=1, longitude=2, direction=Direction.NORTH.value, vehicle_type=VehicleType.CAR.value),
        Detection(event_id="a", plate_number="KA01AB1234", confidence=0.9, camera_id="CAM_01", timestamp=first, latitude=1, longitude=2, direction=Direction.EAST.value, vehicle_type=VehicleType.CAR.value),
        Detection(event_id="c", plate_number="KA01AB1234", confidence=0.9, camera_id="CAM_02", timestamp=second, latitude=1, longitude=2, direction=Direction.NORTH.value, vehicle_type=VehicleType.CAR.value),
    ]
    trajectory = reconstruct_trajectory("KA01AB1234", detections)
    assert [item.camera_id for item in trajectory.detections] == ["CAM_01", "CAM_02"]
    assert trajectory.first_seen == first
    assert trajectory.last_seen == second