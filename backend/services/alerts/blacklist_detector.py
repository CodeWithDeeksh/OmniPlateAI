from typing import Dict, List, Any

def detect_blacklisted_vehicles(
    detections: List[Dict[str, Any]], 
    blacklist: List[str]
) -> List[Dict[str, Any]]:
    """
    Checks detections against a set or list of blacklisted license plates.
    """
    blacklisted_set = set(blacklist)
    alerts = []

    for record in detections:
        plate = record.get("plate_number")
        if plate in blacklisted_set:
            alerts.append({
                "alert_type": "BLACKLIST_MATCH",
                "severity": "CRITICAL",
                "plate_number": plate,
                "camera_id": record.get("camera_id"),
                "timestamp": record.get("timestamp"),
                "details": f"Blacklisted vehicle {plate} detected at camera {record.get('camera_id')}."
            })

    return alerts