from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any

def compute_hourly_trends(detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aggregates overall traffic volume grouped by hour of the day.
    """
    hourly_map = defaultdict(int)

    for record in detections:
        dt = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
        hour_key = dt.strftime("%Y-%m-%dT%H:00:00")
        hourly_map[hour_key] += 1

    sorted_hours = sorted(hourly_map.keys())
    return [
        {"timestamp": hour, "total_detections": hourly_map[hour]}
        for hour in sorted_hours
    ]