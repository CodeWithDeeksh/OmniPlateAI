from typing import Dict, List, Any

DEFAULT_THRESHOLDS = {
    "LOW": 10,     # < 10 vehicles per interval
    "MEDIUM": 25   # 10 to 25 vehicles per interval
    # > 25 is HIGH
}

def analyze_congestion(
    density_records: List[Dict[str, Any]], 
    thresholds: Dict[str, int] = DEFAULT_THRESHOLDS
) -> List[Dict[str, Any]]:
    """
    Evaluates traffic density against threshold levels.
    """
    congestion_results = []

    for record in density_records:
        count = record["vehicle_count"]
        
        if count < thresholds["LOW"]:
            level = "LOW"
        elif count <= thresholds["MEDIUM"]:
            level = "MEDIUM"
        else:
            level = "HIGH"

        congestion_results.append({
            "camera_id": record["camera_id"],
            "timestamp_bucket": record["timestamp_bucket"],
            "vehicle_count": count,
            "congestion_level": level
        })

    return congestion_results