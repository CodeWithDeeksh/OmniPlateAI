from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any

def calculate_traffic_density(
    detections: List[Dict[str, Any]], 
    interval_minutes: int = 15
) -> List[Dict[str, Any]]:
    """
    Groups vehicle detections by camera_id and time window.
    """
    density_map = defaultdict(int)

    for record in detections:
        camera_id = record["camera_id"]
        # Parse timestamp string to datetime object
        dt = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
        
        # Bucket timestamp by interval
        bucket_minute = (dt.minute // interval_minutes) * interval_minutes
        bucket_time = dt.replace(minute=bucket_minute, second=0, microsecond=0).isoformat()
        
        density_map[(camera_id, bucket_time)] += 1

    return [
        {
            "camera_id": camera_id,
            "timestamp_bucket": bucket_time,
            "vehicle_count": count
        }
        for (camera_id, bucket_time), count in density_map.items()
    ]