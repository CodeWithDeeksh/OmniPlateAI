from collections import defaultdict
from typing import Dict, List, Any, Set, Tuple

def detect_route_anomalies(
    detections: List[Dict[str, Any]], 
    expected_transitions: Set[Tuple[str, str]]
) -> List[Dict[str, Any]]:
    """
    Flags camera transitions that do not exist in standard route patterns.
    """
    alerts = []
    vehicle_history = defaultdict(list)
    sorted_detections = sorted(detections, key=lambda x: x["timestamp"])

    for record in sorted_detections:
        vehicle_history[record["plate_number"]].append(record)

    for plate, history in vehicle_history.items():
        for i in range(len(history) - 1):
            from_cam = history[i]["camera_id"]
            to_cam = history[i+1]["camera_id"]

            if from_cam != to_cam and (from_cam, to_cam) not in expected_transitions:
                alerts.append({
                    "alert_type": "ROUTE_ANOMALY",
                    "severity": "MEDIUM",
                    "plate_number": plate,
                    "timestamp": history[i+1]["timestamp"],
                    "details": f"Unusual transition detected: {from_cam} -> {to_cam}"
                })

    return alerts