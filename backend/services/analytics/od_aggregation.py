from collections import defaultdict
from typing import Dict, List, Any

def aggregate_origin_destination(detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Builds an Origin-Destination matrix by tracking sequential vehicle camera trips.
    """
    # Sort detections chronologically per vehicle plate
    vehicle_trips = defaultdict(list)
    sorted_detections = sorted(detections, key=lambda x: x["timestamp"])
    
    for record in sorted_detections:
        vehicle_trips[record["plate_number"]].append(record["camera_id"])

    od_counts = defaultdict(int)

    # Count consecutive camera pairs (Origin -> Destination)
    for plate, path in vehicle_trips.items():
        for i in range(len(path) - 1):
            origin = path[i]
            destination = path[i + 1]
            if origin != destination:  # Skip stationary detections at the same camera
                od_counts[(origin, destination)] += 1

    return [
        {
            "origin_camera": origin,
            "destination_camera": destination,
            "trip_count": count
        }
        for (origin, destination), count in od_counts.items()
    ]