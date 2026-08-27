from typing import Dict, List, Any
import uuid

def format_and_aggregate_alerts(*alert_lists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Standardizes alert objects into unified schema format.
    """
    standardized = []
    
    for alert_list in alert_lists:
        for alert in alert_list:
            standardized.append({
                "id": str(uuid.uuid4()),
                "alert_type": alert["alert_type"],
                "severity": alert["severity"],
                "plate_number": alert["plate_number"],
                "camera_id": alert.get("camera_id", "N/A"),
                "timestamp": alert["timestamp"],
                "details": alert["details"]
            })

    return standardized