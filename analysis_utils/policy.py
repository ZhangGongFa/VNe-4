"""Threshold policy utilities for PD classification.

This module defines helpers to load per‑sector PD thresholds from a
JSON configuration file, fall back to default thresholds when
sector‑specific values are unavailable, and classify a PD into
categories ('Low', 'Medium', 'High') accordingly.  The defaults
match those used in the PD‑monotonic‑constraints project.
"""

import json
from typing import Dict

# Default thresholds used when no sector‑specific entry is found
DEFAULT_THRESHOLDS = {"low": 0.10, "medium": 0.30}


def load_thresholds(path: str) -> Dict:
    """Load threshold configuration from a JSON file.

    The configuration file should map sectors to dictionaries with
    ``low`` and ``medium`` keys.  A special key ``__default__`` can
    define the fallback thresholds.  If the file cannot be read or
    does not include a ``__default__`` key, the module's
    ``DEFAULT_THRESHOLDS`` will be used.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "__default__" not in data:
                data["__default__"] = DEFAULT_THRESHOLDS
            return data
    except Exception:
        return {"__default__": DEFAULT_THRESHOLDS}


def thresholds_for_sector(thresholds: Dict, sector: str) -> Dict:
    """Return the PD thresholds for a given sector.

    If ``sector`` is None or not present in the thresholds map, the
    ``__default__`` thresholds are returned.
    """
    if not sector:
        return thresholds.get("__default__", DEFAULT_THRESHOLDS)
    return thresholds.get(sector, thresholds.get("__default__", DEFAULT_THRESHOLDS))


def classify_pd(pd_value: float, th: Dict) -> str:
    """Classify a PD value into 'Low', 'Medium' or 'High'.

    The classification rules are:

    * **Low** – PD < th['low']
    * **Medium** – th['low'] <= PD < th['medium']
    * **High** – PD >= th['medium']
    """
    if pd_value < th["low"]:
        return "Low"
    if pd_value < th["medium"]:
        return "Medium"
    return "High"