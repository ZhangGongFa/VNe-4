import json
from typing import Dict

DEFAULT_THRESHOLDS = {"low": 0.10, "medium": 0.30}

def load_thresholds(path: str) -> Dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "__default__" not in data:
                data["__default__"] = DEFAULT_THRESHOLDS
            return data
    except Exception:
        return {"__default__": DEFAULT_THRESHOLDS}

def thresholds_for_sector(thresholds: Dict, sector: str) -> Dict:
    if not sector:
        return thresholds.get("__default__", DEFAULT_THRESHOLDS)
    return thresholds.get(sector, thresholds.get("__default__", DEFAULT_THRESHOLDS))

def classify_pd(pd_value: float, th: Dict) -> str:
    if pd_value < th["low"]:
        return "Low"
    if pd_value < th["medium"]:
        return "Medium"
    return "High"