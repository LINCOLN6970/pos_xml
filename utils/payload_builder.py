"""Convert _pos_data.json structure to _payload.json format for downstream API."""

import uuid
from datetime import datetime


DEFAULT_CHANNEL_ID = 5637192654
DEFAULT_PRODUCT_ID = 5637146394
DEFAULT_ITEM_ID = "000006056"
STORE_ID_PREFIX = "ac4_"


def _float(s, default=0.0):
    """Convert string to float, return default if invalid."""
    if s is None or s == "":
        return default
    try:
        return float(s)
    except (ValueError, TypeError):
        return default


def _receipt_time_to_seconds(time_str):
    """Convert 'HH:MM:SS' to seconds since midnight."""
    if not time_str or not time_str.strip():
        return 0
    parts = time_str.strip().split(":")
    if len(parts) < 3:
        return 0
    try:
        h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
        return h * 3600 + m * 60 + s
    except (ValueError, TypeError):
        return 0


def _date_time_to_unix(date_str, time_str):
    """Convert 'YYYY-MM-DD' + 'HH:MM:SS' to Unix timestamp."""
    if not date_str or not date_str.strip():
        return 0
    time_str = (time_str or "").strip()
    if not time_str:
        time_str = "00:00:00"
    try:
        dt = datetime.strptime(
            f"{date_str.strip()} {time_str}",
            "%Y-%m-%d %H:%M:%S",
        )
        return int(dt.replace(tzinfo=None).timestamp())
    except (ValueError, TypeError):
        return 0


def _ext_prop_str(key, val):
    """ExtensionProperties entry with StringValue."""
    return {"Key": key, "Value": {"StringValue": str(val) if val else ""}}


def _ext_prop_decimal(key, val):
    """ExtensionProperties entry with DecimalValue."""
    return {"Key": key, "Value": {"DecimalValue": _float(val)}}


def _ext_prop_int(key, val):
    """ExtensionProperties entry with IntegerValue."""
    try:
        v = int(val) if val is not None and val != "" else 0
    except (ValueError, TypeError):
        v = 0
    return {"Key": key, "Value": {"IntegerValue": v}}


def build_payload(pos_data: dict, channel_id: int = DEFAULT_CHANNEL_ID) -> dict | None:
    """
    Convert _pos_data.json structure to _payload.json format.
    Returns payload dict for first transaction, or None if no transactions.
    """
    transactions = pos_data.get("Transactions") or []
    if not transactions:
        return None

    tx = transactions[0]
    # TODO: 实现完整映射，参考 PAYLOAD_实施方案.md 和 output/*/_{payload,pos_data}.json
    return {
        "Id": f"000000000-{tx.get('TRANSACTIONID', '')}",
        "StoreId": f"{STORE_ID_PREFIX}{tx.get('STORELOCATIONID', '')}",
        "TerminalId": f"{tx.get('STORELOCATIONID', '')}-{tx.get('REGISTERID', '')}",
        "TotalAmount": _float(tx.get("TRANSACTIONTOTALGRANDAMOUNT")),
        "TransactionDate": tx.get("BUSINESSDATE") or tx.get("RECEIPTDATE", ""),
        "InternalTransactionId": str(uuid.uuid4()),
        "ChannelId": channel_id,
        "SalesLines": [],
        "TenderLines": [],
        "ExtensionProperties": [],
    }