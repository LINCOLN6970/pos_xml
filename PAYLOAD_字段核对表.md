# Payload 字段核对表

根据下游 API 文档核对 `_payload.json` 各字段。你来填充「API 要求」「当前实现」「是否一致」。

---

## 顶层字段

| 字段名 | API 要求（你来填） | 当前实现 / 来源 | 一致？ |
|--------|---------------------|------------------|--------|
| Id | | `000000000-{TRANSACTIONID}` | |
| StoreId | | `ac4_{STORELOCATIONID}` | |
| TerminalId | | `{STORELOCATIONID}-{REGISTERID}` | |
| TotalAmount | | `TRANSACTIONTOTALGRANDAMOUNT` | |
| GrossAmount | | 同 TotalAmount | |
| NetAmount | | -TotalAmount（需确认符号） | |
| TransactionDate | | `BUSINESSDATE` | |
| TransactionTime | | Unix 时间戳（RECEIPTDATE + RECEIPTTIME） | |
| BusinessDate | | `{date}T00:00:00-05:00`（你来确认时区） | |
| ChannelId | | 常量 5637192654 | |
| CurrencyCode | | 硬编码 "CAD" | |
| StatusValue | | 硬编码 4 | |
| ShiftTerminalId | | 同 TerminalId | |

---

## ExtensionProperties（交易层）

| Key | API 要求（你来填） | 当前来源 | 一致？ |
|-----|---------------------|----------|--------|
| BullochShiftId | | `BULLOCHSHIFTID` | |
| LpeLoyaltyTransactionId | | `LPELOYALTYTRANSACTIONID` | |
| MobilaInvoiceNumber | | `MOBILAINVOICENUMBER` | |
| ReceiptDate | | `RECEIPTDATE` | |
| ReceiptTime | | 秒数（RECEIPTTIME → HH:MM:SS） | |
| TransactionTotalNetAmount | | `TRANSACTIONTOTALNETAMOUNT` | |
| TransactionTotalGrossAmount | | `TRANSACTIONTOTALGROSSAMOUNT` | |
| TransactionTotalGrandAmount | | `TRANSACTIONTOTALGRANDAMOUNT` | |
| StoreLocationId | | `STORELOCATIONID` | |
| CashierId | | `CASHIERID` | |
| RegisterId | | `REGISTERID` | |

---

## SalesLines（来自 fuel_lines）

| 字段名 | API 要求（你来填） | 当前映射 | 一致？ |
|--------|---------------------|----------|--------|
| LineId | | 序列号 | |
| TotalAmount | | `SALESAMOUNT` | |
| Quantity | | `SALESQUANTITY` | |
| Price | | `REGULARSELLPRICE` 或 `ACTUALSALESPRICE` | |
| ProductId | | 常量 DEFAULT_PRODUCT_ID | |
| ItemId | | 常量 DEFAULT_ITEM_ID | |
| UnitOfMeasureSymbol | | "L" | |

### SalesLine ExtensionProperties

| Key | API 要求（你来填） | 当前来源 | 一致？ |
|-----|---------------------|----------|--------|
| FuelGradeId | | `FUELGRADEID` | |
| FuelPositionId | | `FUELPOSITIONID` | |
| ActualSalesPrice | | `ACTUALSALESPRICE` | |
| LineType | | 固定 4 | |
| EntryMethod | | `ENTRYMETHOD` | |
| ServiceLevelCode | | `SERVICELEVELCODE` | |

---

## TenderLines（来自 tender_lines）

| 字段名 | API 要求（你来填） | 当前映射 | 一致？ |
|--------|---------------------|----------|--------|
| Amount | | `TENDERAMOUNT` | |
| TenderTypeId | | `TENDERCODE` | |
| Currency | | "CAD" | |
| StatusValue | | 4 | |

### TenderLine ExtensionProperties

| Key | API 要求（你来填） | 当前来源 | 一致？ |
|-----|---------------------|----------|--------|
| TenderSubCode | | `TENDERSUBCODE` | |

---

## 待补充字段（若 API 要求）

你来列出 API 需要但当前未实现的字段，并在 `utils/payload_builder.py` 中补全：

- [ ] 字段 1：_____ → 来源 _____
- [ ] 字段 2：_____ → 来源 _____
