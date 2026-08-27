from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any
import math

def calculate_haversine_distance(coord1: tuple, coord2: tuple) -> float:
    """Calculates distance between two (lat, lon) coordinates in kilometers."""
    R = 6371.0  # Earth radius in km
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def detect_impossible_travel(
    detections: List[Dict[str, Any]], 
    camera_locations: Dict[str, tuple], 
    max_speed_kmh: float = 180.0
) -> List[Dict[str, Any]]:
    """
    Identifies vehicles moving between cameras faster than physically possible.
    """
    alerts = []
    vehicle_history = defaultdict(list)
    
    # Sort detections chronologically per vehicle
    sorted_detections = sorted(detections, key=lambda x: x["timestamp"])
    for record in sorted_detections:
        vehicle_history[record["plate_number"]].append(record)

    for plate, history in vehicle_history.items():
        for i in range(len(history) - 1):
            prev = history[i]
            curr = history[i + 1]
            
            prev_cam, curr_cam = prev["camera_id"], curr["camera_id"]
            if prev_cam not in camera_locations or curr_cam not in camera_locations:
                continue

            # Calculate time difference in hours
            t1 = datetime.fromisoformat(prev["timestamp"].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(curr["timestamp"].replace("Z", "+00:00"))
            time_delta_hours = (t2 - t1).total_seconds() / 3600.0

            if time_delta_hours <= 0:
                continue

            # Calculate distance and speed
            dist_km = calculate_haversine_distance(
                camera_locations[prev_cam], 
                camera_locations[curr_cam]
            )
            speed_kmh = dist_km / time_delta_hours

            if speed_kmh > max_speed_kmh:
                alerts.append({
                    "alert_type": "IMPOSSIBLE_TRAVEL",
                    "severity": "HIGH",
                    "plate_number": plate,
                    "timestamp": curr["timestamp"],
                    "details": f"Vehicle covered {dist_km:.2f}km in {time_delta_hours*60:.1f} mins ({speed_kmh:.1f} km/h)."
                })

    return alerts