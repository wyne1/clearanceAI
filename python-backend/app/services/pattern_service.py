import json
from pathlib import Path
from typing import Dict, List, Optional

# Load mock data files
DATA_DIR = Path(__file__).parent.parent / "data"


def _load_json_file(filename: str) -> dict:
    """Load a JSON file from the data directory."""
    file_path = DATA_DIR / filename
    if not file_path.exists():
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_commodity_pattern(commodity: str) -> Optional[Dict[str, any]]:
    """
    Get the expected pattern for a commodity (typical origins).
    Returns None if no pattern found.
    """
    data = _load_json_file("commodity_patterns.json")
    patterns = data.get("patterns", [])
    
    commodity_lower = commodity.lower()
    for pattern in patterns:
        if pattern.get("commodity", "").lower() == commodity_lower:
            return pattern
    
    return None


def check_commodity_origin_match(commodity: str, origin: str) -> Dict[str, any]:
    """
    Check if a commodity-origin combination matches expected patterns.
    Returns dict with match status, risk level, and analysis.
    """
    pattern = get_commodity_pattern(commodity)
    
    if not pattern:
        return {
            "match": True,  # No pattern = no mismatch
            "riskLevel": "low",
            "analysis": f"No established pattern for {commodity}. Cannot determine if origin is anomalous.",
            "expectedOrigins": [],
            "primaryOrigin": None
        }
    
    expected_origins = [o.lower() for o in pattern.get("expectedOrigins", [])]
    primary_origin = pattern.get("primaryOrigin", "").lower()
    origin_lower = origin.lower()
    
    is_match = origin_lower in expected_origins
    is_primary = origin_lower == primary_origin
    
    if is_match:
        if is_primary:
            return {
                "match": True,
                "riskLevel": "low",
                "analysis": f"{commodity} from {origin} matches expected pattern. {origin} is the primary origin ({pattern.get('primaryOriginPercentage', 0)}% of production).",
                "expectedOrigins": pattern.get("expectedOrigins", []),
                "primaryOrigin": pattern.get("primaryOrigin"),
                "primaryOriginPercentage": pattern.get("primaryOriginPercentage", 0)
            }
        else:
            return {
                "match": True,
                "riskLevel": "low",
                "analysis": f"{commodity} from {origin} is within expected origins, though {pattern.get('primaryOrigin')} is more common.",
                "expectedOrigins": pattern.get("expectedOrigins", []),
                "primaryOrigin": pattern.get("primaryOrigin"),
                "primaryOriginPercentage": pattern.get("primaryOriginPercentage", 0)
            }
    else:
        # Mismatch - this is a risk flag
        primary_pct = pattern.get("primaryOriginPercentage", 0)
        return {
            "match": False,
            "riskLevel": "high" if primary_pct > 50 else "medium",
            "analysis": f"Commodity Origin Mismatch: {commodity} typically comes from {pattern.get('primaryOrigin')} ({primary_pct}% of production), but this shipment is from {origin}. This represents an anomaly that requires investigation.",
            "expectedOrigins": pattern.get("expectedOrigins", []),
            "primaryOrigin": pattern.get("primaryOrigin"),
            "primaryOriginPercentage": primary_pct,
            "flag": f"Commodity Origin Mismatch - Expected {pattern.get('primaryOrigin')}, got {origin}"
        }


def analyze_trading_pattern_anomaly(
    entity_name: str,
    commodity: str,
    origin: str,
    historical_patterns: List[Dict[str, any]]
) -> Dict[str, any]:
    """
    Analyze if a shipment represents an anomaly based on historical trading patterns.
    historical_patterns should be a list of dicts with 'commodity', 'frequency', 'normalOrigins'.
    """
    # Check commodity-origin match first
    origin_check = check_commodity_origin_match(commodity, origin)
    
    # Check if entity has history with this commodity
    commodity_lower = commodity.lower()
    entity_history = [
        p for p in historical_patterns
        if p.get("commodity", "").lower() == commodity_lower
    ]
    
    # Check if entity typically ships from this origin
    origin_lower = origin.lower()
    origin_history = [
        p for p in historical_patterns
        if origin_lower in [o.lower() for o in p.get("normalOrigins", [])]
    ]
    
    anomalies = []
    risk_level = "low"
    
    # Anomaly: Entity never shipped this commodity before
    if not entity_history:
        anomalies.append(f"Entity typically handles other commodities, not {commodity}")
        risk_level = "medium"
    
    # Anomaly: Origin mismatch
    if not origin_check.get("match", True):
        anomalies.append(origin_check.get("flag", "Origin mismatch"))
        if origin_check.get("riskLevel") == "high":
            risk_level = "high"
        elif risk_level != "high":
            risk_level = "medium"
    
    # Anomaly: Entity doesn't typically ship from this origin
    if entity_history and not any(
        origin_lower in [o.lower() for o in p.get("normalOrigins", [])]
        for p in entity_history
    ):
        anomalies.append(f"Entity typically ships from different origins")
        if risk_level != "high":
            risk_level = "medium"
    
    analysis_text = f"Trading pattern analysis for {entity_name}: "
    if anomalies:
        analysis_text += "Multiple anomalies detected. " + " ".join(anomalies)
    else:
        analysis_text += "Pattern appears consistent with historical data."
    
    return {
        "isAnomaly": len(anomalies) > 0,
        "anomalies": anomalies,
        "riskLevel": risk_level,
        "analysis": analysis_text,
        "originCheck": origin_check
    }

