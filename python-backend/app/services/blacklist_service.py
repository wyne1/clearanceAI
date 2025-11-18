import json
import os
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


def check_60b_list(entity_name: str) -> Dict[str, any]:
    """
    Check if an entity is on the 60B tax blacklist.
    Returns dict with 'listed' (bool) and optional 'reason' and 'date'.
    """
    data = _load_json_file("blacklist_60b.json")
    entities = data.get("entities", [])
    
    # Case-insensitive search
    entity_name_lower = entity_name.lower()
    for entity in entities:
        if entity.get("name", "").lower() == entity_name_lower:
            return {
                "listed": True,
                "reason": entity.get("reason", "Tax/fiscal issues"),
                "listedDate": entity.get("listedDate", "Unknown")
            }
    
    return {"listed": False}


def check_approved_manufacturer(entity_name: str, commodity: Optional[str] = None) -> Dict[str, any]:
    """
    Check if an entity is an approved manufacturer.
    Optionally check if approved for a specific commodity.
    """
    data = _load_json_file("approved_manufacturers.json")
    manufacturers = data.get("manufacturers", [])
    
    entity_name_lower = entity_name.lower()
    for manufacturer in manufacturers:
        if manufacturer.get("name", "").lower() == entity_name_lower:
            approved_commodities = manufacturer.get("commodities", [])
            
            result = {
                "approved": True,
                "country": manufacturer.get("country", ""),
                "approvedDate": manufacturer.get("approvedDate", ""),
                "commodities": approved_commodities
            }
            
            # If commodity specified, check if approved for that commodity
            if commodity:
                commodity_lower = commodity.lower()
                is_approved_for_commodity = any(
                    c.lower() == commodity_lower for c in approved_commodities
                )
                result["approvedForCommodity"] = is_approved_for_commodity
            
            return result
    
    return {"approved": False}


def get_blacklist_status(
    entity_name: str,
    entity_type: str = "shipper",
    commodity: Optional[str] = None
) -> Dict[str, any]:
    """
    Get comprehensive blacklist status for an entity.
    Returns dict with list60B, approvedManufacturer, and otherFlags.
    """
    status = {
        "list60B": False,
        "approvedManufacturer": False,
        "otherFlags": []
    }
    
    # Check 60B list
    list60b_result = check_60b_list(entity_name)
    if list60b_result.get("listed", False):
        status["list60B"] = True
        reason = list60b_result.get("reason", "Tax/fiscal issues")
        status["otherFlags"].append(f"60B List: {reason}")
    
    # Check approved manufacturer (only if type is manufacturer or shipper)
    if entity_type in ["manufacturer", "shipper"]:
        approved_result = check_approved_manufacturer(entity_name, commodity)
        status["approvedManufacturer"] = approved_result.get("approved", False)
        
        # If commodity specified and not approved for it, add flag
        if commodity and not approved_result.get("approvedForCommodity", True):
            status["otherFlags"].append(
                f"Not on approved manufacturer list for {commodity}"
            )
    
    return status

