# SIH26127 — API Contract

This document defines the HTTP API exposed by the backend.

All frontend and external modules must use these documented API contracts.

Internal implementation details may change without changing the API contract unless approved by the lead.

---

## 1. Base URL

Local development:

```text
http://localhost:8000
```

All API routes are prefixed with:
/api

Example:

GET /api/health

2. Health Check
GET /api/health

Checks whether the backend is running.

Response
{
  "status": "ok"
}
3. Detection Ingestion
POST /api/detections

Adds a new DetectionEvent to the system.

The ANPR module may use this endpoint when detections are produced outside the backend process.

Request Body

Must follow the DetectionEvent structure defined in:

docs/data_contract.md

Example:

{
  "event_id": "evt_001",
  "plate_number": "KA01AB1234",
  "confidence": 0.96,
  "camera_id": "CAM_07",
  "timestamp": "2026-08-25T18:21:32Z",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "direction": "NORTH",
  "vehicle_type": "car",
  "snapshot_path": "data/snapshots/evt_001.jpg"
}
Response
{
  "status": "created",
  "event_id": "evt_001"
}

4. Vehicle Search
GET /api/vehicles/{plate_number}

Returns a summary of observations for a vehicle.

Example
GET /api/vehicles/KA01AB1234
Response
{
  "plate_number": "KA01AB1234",
  "first_seen": "2026-08-25T08:42:00Z",
  "last_seen": "2026-08-25T18:27:00Z",
  "detection_count": 8,
  "camera_count": 6
}
5. Vehicle Trajectory
GET /api/vehicles/{plate_number}/trajectory

Returns the reconstructed trajectory of a vehicle.

Example
GET /api/vehicles/KA01AB1234/trajectory
Response

Must follow the VehicleTrajectory structure defined in:

docs/data_contract.md

Example:

{
  "plate_number": "KA01AB1234",
  "first_seen": "2026-08-25T08:42:00Z",
  "last_seen": "2026-08-25T18:27:00Z",
  "detections": [
    {
      "camera_id": "CAM_01",
      "timestamp": "2026-08-25T08:42:00Z",
      "latitude": 12.9716,
      "longitude": 77.5946,
      "direction": "EAST"
    },
    {
      "camera_id": "CAM_04",
      "timestamp": "2026-08-25T08:50:00Z",
      "latitude": 12.9780,
      "longitude": 77.6010,
      "direction": "NORTH"
    }
  ]
}
6. Camera List
GET /api/cameras

Returns all configured cameras.

Response
[
  {
    "camera_id": "CAM_01",
    "name": "MG Road Junction",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "road": "MG Road",
    "direction": "EAST"
  },
  {
    "camera_id": "CAM_02",
    "name": "Brigade Road",
    "latitude": 12.9712,
    "longitude": 77.6050,
    "road": "Brigade Road",
    "direction": "NORTH"
  }
]
7. Traffic Density
GET /api/analytics/density

Returns traffic volume statistics.

Optional Query Parameters
camera_id
start_time
end_time

Example:

GET /api/analytics/density?camera_id=CAM_07
Response
[
  {
    "camera_id": "CAM_07",
    "road": "MG Road",
    "vehicles_per_hour": 1240
  }
]
8. Congestion
GET /api/analytics/congestion

Returns congestion information between camera/road segments.

Optional Query Parameters
start_time
end_time
Response
[
  {
    "from_camera": "CAM_12",
    "to_camera": "CAM_16",
    "travel_time_minutes": 18,
    "normal_travel_time_minutes": 9,
    "congestion_level": "HIGH"
  }
]
9. Origin-Destination Analysis
GET /api/analytics/od

Returns aggregated vehicle movement between zones.

Optional Query Parameters
start_time
end_time
Response
[
  {
    "origin_zone": "ZONE_A",
    "destination_zone": "ZONE_D",
    "vehicle_count": 1540
  }
]
10. Alerts
GET /api/alerts

Returns generated alerts.

Optional Query Parameters
severity
type
start_time
end_time

Example:

GET /api/alerts?severity=HIGH
Response
[
  {
    "alert_id": "alert_001",
    "plate_number": "KA01AB1234",
    "type": "BLACKLISTED_VEHICLE",
    "camera_id": "CAM_17",
    "timestamp": "2026-08-25T18:44:00Z",
    "severity": "HIGH",
    "message": "Blacklisted vehicle detected"
  }
]

11. Error Response

All API errors should follow a consistent structure.

Example
{
  "error": {
    "code": "VEHICLE_NOT_FOUND",
    "message": "No detections found for plate KA01AB1234"
  }
}

12. HTTP Status Codes

Use standard HTTP status codes.

| Status | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 400 | Invalid request |
| 404 | Resource not found |
| 422 | Validation error |
| 500 | Internal server error |

13. API Ownership
Lead / Backend

Owns:

/api/health
/api/detections
/api/vehicles/{plate_number}
/api/vehicles/{plate_number}/trajectory
/api/cameras
Analytics Module

Provides data used by:

/api/analytics/density
/api/analytics/congestion
/api/analytics/od
Alerts Module

Provides data used by:

/api/alerts
Frontend

Consumes the documented API responses.

The frontend must not directly access the database.

14. API Rules
Do not change endpoint names without approval from the lead.
Do not change response structures without updating this document.
Request and response schemas must remain consistent with docs/data_contract.md.
Use JSON for API request and response bodies unless otherwise documented.
Use UTC timestamps.
Validate incoming data at the API boundary.
Do not expose database credentials, API keys or internal secrets.
Backend errors must use the documented error structure.
New endpoints must be documented before dependent frontend code is merged.