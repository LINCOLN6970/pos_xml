"""
Validation utilities for pos_data.json and payload.json outputs.
Can be imported for programmatic use or called from scripts/validate.py.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

# Exit codes
EXIT_OK = 0
EXIT_FAIL = 1

# Required payload fields
REQUIRED_PAYLOAD_FIELDS = ("Id", "StoreId", "TotalAmount")

# Payload list fields that must be lists
PAYLOAD_LIST_FIELDS = ("SalesLines", "TenderLines")


def _load_json(path: Path) -> Tuple[dict | None, str | None]:
    """
    Load JSON from path. Returns (data, None) on success, (None, error_msg) on failure.
    """
    if not path.exists():
        return None, f"File not found: {path}"

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {e}"


def validate_pos_data(path: Path) -> Tuple[bool, str]:
    """
    Validate _pos_data.json structure.
    Returns (success, error_message). success=True means valid.
    """
    data, err = _load_json(path)
    if err:
        return False, err

    if not data.get("Transactions"):
        return False, "Transactions is empty or missing"

    status = data.get("ProcessingStatus")
    if status != "Success":
        return False, f"ProcessingStatus is not Success (got: {status})"

    return True, ""


def validate_payload(path: Path) -> Tuple[bool, str]:
    """
    Validate _payload.json structure.
    Returns (success, error_message). success=True means valid.
    """
    data, err = _load_json(path)
    if err:
        return False, err

    for key in REQUIRED_PAYLOAD_FIELDS:
        if key not in data:
            return False, f"Missing required field: {key}"

    for key in PAYLOAD_LIST_FIELDS:
        val = data.get(key)
        if not isinstance(val, list):
            return False, f"{key} must be a list (got: {type(val).__name__})"

    return True, ""
