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


def _build_sales_line_from_fuel(fuel, seq, tx_id, channel_id):
    """Build one SalesLine from fuel_lines item."""
    amount = _float(fuel.get("SALESAMOUNT"))
    qty = _float(fuel.get("SALESQUANTITY"))
    price = _float(fuel.get("REGULARSELLPRICE") or fuel.get("ACTUALSALESPRICE"))
    ext_props = [
        _ext_prop_str("FuelGradeId", fuel.get("FUELGRADEID")),
        _ext_prop_decimal("ActualSalesPrice", fuel.get("ACTUALSALESPRICE")),
        _ext_prop_str("FuelPositionId", fuel.get("FUELPOSITIONID")),
        _ext_prop_int("LineType", 4),
        _ext_prop_str("EntryMethod", fuel.get("ENTRYMETHOD", "other")),
        _ext_prop_str("OriginalTransactionId", ""),
        _ext_prop_str("ServiceLevelCode", fuel.get("SERVICELEVELCODE")),
    ]
    return {
        "StaffId": "",
        "LineId": str(seq),
        "OriginLineId": str(seq),
        "TaxOverrideCode": "",
        "ProductId": DEFAULT_PRODUCT_ID,
        "EntryMethodTypeValue": 0,
        "ListingId": DEFAULT_PRODUCT_ID,
        "IsPriceOverridden": False,
        "OriginalPrice": price,
        "TotalAmount": amount,
        "NetAmountWithoutTax": amount,
        "Description": fuel.get("DESCRIPTION", ""),
        "DiscountAmount": 0.0,
        "DiscountAmountWithoutTax": 0.0,
        "NetPrice": -amount,
        "TotalDiscount": 0.0,
        "TotalPercentageDiscount": 0.0,
        "LineDiscount": 0.0,
        "PeriodicDiscount": 0.0,
        "LineManualDiscountPercentage": 0.0,
        "LineManualDiscountAmount": 0.0,
        "InventoryLocationId": "Default",
        "ItemType": 0,
        "LineNumber": float(seq),
        "ReturnQuantity": 0.0,
        "StatusValue": 0,
        "SalesStatusValue": 0,
        "ProductSourceValue": 0,
        "InvoiceTypeValue": 0,
        "BasePrice": 0.0,
        "ReturnChannelId": channel_id,
        "QuantityOrdered": qty,
        "BatchId": "",
        "UnitOfMeasureSymbol": "L",
        "TenderDiscountAmount": 0.0,
        "TenderDiscountPercentage": 0.0,
        "LinePercentageDiscount": 0.0,
        "PeriodicPercentageDiscount": 0.0,
        "QuantityDiscounted": 0,
        "UnitQuantity": 0.0,
        "LineMultilineDiscOnItemValue": 0,
        "FulfillmentStatusValue": 0,
        "DetailedLineStatusValue": 0,
        "ItemId": DEFAULT_ITEM_ID,
        "Quantity": qty,
        "Price": price,
        "ItemTaxGroupId": "",
        "SalesTaxGroupId": "",
        "TaxAmount": 0.0,
        "SalesOrderUnitOfMeasure": "L",
        "NetAmount": amount,
        "NetAmountPerUnit": 0.0,
        "GrossAmount": amount,
        "TaxAmountExemptInclusive": 0,
        "TaxAmountInclusive": 0,
        "TaxAmountExclusive": 0.0,
        "NetAmountWithAllInclusiveTax": amount,
        "TaxRatePercent": 0.0,
        "ReturnLineTaxAmount": 0,
        "TaxExemptPriceInclusiveReductionAmount": 0.0,
        "TaxExemptPriceInclusiveOriginalPrice": amount,
        "ChargeLines": [],
        "DiscountLines": [],
        "PriceLines": [],
        "AttainablePriceLines": [],
        "PeriodicDiscountPossibilities": [],
        "ReasonCodeLines": [],
        "AttributeValues": [],
        "TaxLines": [],
        "TaxMeasures": [],
        "ReturnTaxLines": [],
        "ExtensionProperties": ext_props,
    }


def _build_tender_line(tender, seq, store_id, terminal_id, tx_id, channel_id):
    """Build one TenderLine from tender_lines item."""
    amount = _float(tender.get("TENDERAMOUNT"))
    ext_props = [
        _ext_prop_str("TenderSubCode", tender.get("TENDERSUBCODE")),
    ]
    return {
        "StoreId": store_id,
        "TerminalId": terminal_id,
        "TransactionId": tx_id,
        "InternalTransactionId": "00000000-0000-0000-0000-000000000000",
        "RefundableAmount": 0.0,
        "CaptureToken": "",
        "CardToken": "",
        "Authorization": "",
        "TransactionStatusValue": 0,
        "IncomeExpenseAccountTypeValue": -1,
        "MaskedCardNumber": "",
        "IsPreProcessed": False,
        "IsDeposit": False,
        "IsCustomerAccountFloorLimitUsed": False,
        "IsIncrementalCaptureEnabled": False,
        "IsReauthorizationEnabled": False,
        "IncrementalOffsetAmount": 0,
        "ChannelId": channel_id,
        "IsLinkedRefund": False,
        "LinkedPaymentStore": "",
        "LinkedPaymentTerminalId": "",
        "LinkedPaymentTransactionId": "",
        "LinkedPaymentLineNumber": 0.0,
        "LinkedPaymentCurrency": "",
        "RoundingDifference": 0,
        "RemainingLinkedRefundAmount": 0,
        "TenderLineId": str(seq),
        "Amount": amount,
        "CashBackAmount": 0,
        "AmountInTenderedCurrency": amount,
        "AmountInCompanyCurrency": amount,
        "Currency": "CAD",
        "ExchangeRate": 1.0,
        "CompanyCurrencyExchangeRate": 1.0,
        "TenderTypeId": str(tender.get("TENDERCODE", "")),
        "LineNumber": float(seq),
        "CustomerId": "",
        "CardTypeId": "",
        "StatusValue": 4,
        "VoidStatusValue": 0,
        "AuthorizedAmount": 0.0,
        "CardPaymentAccountId": "",
        "ProcessingTypeValue": 0,
        "CardProcessorStatusValue": 0,
        "ReasonCodeLines": [],
        "ExtensionProperties": ext_props,
    }


def build_payload(pos_data: dict, channel_id: int = DEFAULT_CHANNEL_ID) -> dict | None:
    """
    Convert _pos_data.json structure to _payload.json format.
    Returns payload dict for first transaction, or None if no transactions.
    """
    transactions = pos_data.get("Transactions") or []
    if not transactions:
        return None

    tx = transactions[0]
    store_loc = tx.get("STORELOCATIONID", "")
    register_id = tx.get("REGISTERID", "")
    tx_id_raw = tx.get("TRANSACTIONID", "")
    tx_id = f"000000000-{tx_id_raw}" if tx_id_raw else "000000000-"
    store_id = f"{STORE_ID_PREFIX}{store_loc}"
    terminal_id = f"{store_loc}-{register_id}" if store_loc and register_id else ""

    total_amount = _float(tx.get("TRANSACTIONTOTALGRANDAMOUNT"))
    receipt_time_sec = _receipt_time_to_seconds(tx.get("RECEIPTTIME", ""))
    business_date = tx.get("BUSINESSDATE", "") or tx.get("RECEIPTDATE", "")
    receipt_date = tx.get("RECEIPTDATE", "") or business_date
    receipt_time_str = tx.get("RECEIPTTIME", "")
    transaction_time_unix = _date_time_to_unix(receipt_date, receipt_time_str)

    ext_props = [
        _ext_prop_str("GenericProductId", "000999999"),
        _ext_prop_str("BullochShiftId", tx.get("BULLOCHSHIFTID")),
        _ext_prop_str("ReportSequenceNumber", tx.get("BULLOCHSHIFTID")),
        _ext_prop_str("OUN", "00013588"),
        _ext_prop_str("CsuBaseUrl", "https://scu7ej1qdsn30470363-rs.su.retail.dynamics.com"),
        _ext_prop_str("LpeLoyaltyTransactionId", tx.get("LPELOYALTYTRANSACTIONID")),
        _ext_prop_str("MobilaInvoiceNumber", tx.get("MOBILAINVOICENUMBER")),
        _ext_prop_str("ReceiptDate", tx.get("RECEIPTDATE")),
        _ext_prop_int("ReceiptTime", receipt_time_sec),
        _ext_prop_decimal("TransactionTotalNetAmount", tx.get("TRANSACTIONTOTALNETAMOUNT")),
        _ext_prop_decimal("TransactionTotalGrossAmount", tx.get("TRANSACTIONTOTALGROSSAMOUNT")),
        _ext_prop_decimal("TransactionTotalTaxNetAmount", tx.get("TRANSACTIONTOTALTAXNETAMOUNT")),
        _ext_prop_decimal("TransactionTotalGrandAmount", tx.get("TRANSACTIONTOTALGRANDAMOUNT")),
        _ext_prop_int("EventType", 7),
        _ext_prop_str("StoreLocationId", store_loc),
        _ext_prop_str("CashierId", tx.get("CASHIERID")),
        _ext_prop_int("OutsideSales", 0),
        _ext_prop_str("RegisterId", register_id),
    ]

    sales_lines = []
    for i, fuel in enumerate(tx.get("fuel_lines") or [], start=1):
        sales_lines.append(_build_sales_line_from_fuel(fuel, i, tx_id, channel_id))

    tender_lines = []
    for i, tender in enumerate(tx.get("tender_lines") or [], start=1):
        tender_lines.append(
            _build_tender_line(tender, i, store_id, terminal_id, tx_id, channel_id)
        )

    payload = {
        "DocumentStatusValue": 0,
        "StatusValue": 4,
        "PaymentStatusValue": 0,
        "DetailedOrderStatusValue": 0,
        "AmountDue": 0,
        "AmountPaid": total_amount,
        "CalculatedDepositAmount": 0,
        "ChannelId": channel_id,
        "ChannelReferenceId": "",
        "ChargeAmount": 0.0,
        "CurrencyCode": "CAD",
        "CustomerId": "",
        "CustomerOrderModeValue": 0,
        "CustomerOrderTypeValue": 0,
        "DeliveryMode": "",
        "DiscountAmount": 0.0,
        "DiscountAmountWithoutTax": 0,
        "NetPrice": total_amount,
        "DiscountCodes": [],
        "EntryStatusValue": 0,
        "GrossAmount": total_amount,
        "Id": tx_id,
        "InternalTransactionId": str(uuid.uuid4()),
        "IncomeExpenseTotalAmount": 0.0,
        "LineDiscount": 0.0,
        "LineDiscountCalculationTypeValue": 0,
        "Name": "",
        "NetAmount": -total_amount,
        "NetAmountWithoutTax": total_amount,
        "NetAmountWithNoTax": total_amount,
        "NetAmountWithTax": total_amount,
        "NumberOfItems": sum(_float(f.get("SALESQUANTITY")) for f in (tx.get("fuel_lines") or [])),
        "OriginalOrderTransactionId": "",
        "PeriodicDiscountAmount": 0.0,
        "TenderDiscountAmount": 0.0,
        "ShiftId": 0,
        "ShiftTerminalId": terminal_id,
        "StaffId": "",
        "StoreId": store_id,
        "SubtotalAmount": total_amount,
        "SubtotalAmountWithoutTax": total_amount,
        "SubtotalSalesAmount": total_amount,
        "TaxAmount": 0.0,
        "TaxAmountExclusive": 0.0,
        "TaxAmountInclusive": 0,
        "TaxOnCancellationCharge": 0,
        "TaxOnShippingCharge": 0,
        "TaxOnNonShippingCharges": 0,
        "TerminalId": terminal_id,
        "TotalAmount": total_amount,
        "TotalSalesAmount": 0,
        "TotalDiscount": 0.0,
        "TotalManualDiscountAmount": 0.0,
        "TotalManualDiscountPercentage": 0.0,
        "TransactionTypeValue": 2,
        "TaxCalculationTypeValue": 0,
        "SalesInvoiceAmount": 0,
        "ShippingChargeAmount": 0,
        "OtherChargeAmount": 0,
        "PeriodicDiscountsCalculateScopeValue": 0,
        "CustomerName": "",
        "LanguageId": "en-CA",
        "TransactionDate": business_date,
        "TransactionTime": transaction_time_unix,
        "BusinessDate": f"{business_date}T00:00:00-05:00" if business_date else "",
        "InventoryLocationId": "Default",
        "ChargeLines": [],
        "IncomeExpenseLines": [],
        "SalesLines": sales_lines,
        "TaxLines": [],
        "TenderLines": tender_lines,
        "Notes": [],
        "FiscalTransactions": [],
        "ExtensionProperties": ext_props,
    }
    return payload