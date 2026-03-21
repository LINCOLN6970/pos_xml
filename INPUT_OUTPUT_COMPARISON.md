# Input → Output 对比报告

以 `naxml-posjournal 10477 035502 1.xml` 为例。

---

## 一、Input（XML）→ Output（_pos_data.json）字段映射

| Output 字段 | 来源（Input XML 路径） | 示例值 |
|-------------|------------------------|--------|
| BULLOCHSHIFTID | `JournalHeader/SecondaryReportPeriod` | 10477 |
| STORELOCATIONID | `TransmissionHeader/StoreLocationID` | 33370 |
| TRANSACTIONID | `SaleEvent/TransactionID` | 035502 |
| BUSINESSDATE | `SaleEvent/BusinessDate` | 2026-03-01 |
| RECEIPTDATE | `SaleEvent/ReceiptDate` | 2026-03-01 |
| RECEIPTTIME | `SaleEvent/ReceiptTime` | 18:53:42 |
| REGISTERID | `SaleEvent/RegisterID` | 1 |
| TRANSACTIONTOTALGRANDAMOUNT | `TransactionSummary/TransactionTotalGrandAmount` | 20.00 |
| CASHIERID | `SaleEvent/CashierID` | surekah |
| LPELOYALTYTRANSACTIONID | `Extension/LoyaltyTransactionID` | 35502 |
| MOBILAINVOICENUMBER | `Extension/MobilaInvoiceNumber` | 310470 |
| fuel_lines[].DESCRIPTION | `FuelLine/Description` | ULTRA 94 |
| fuel_lines[].FUELGRADEID | `FuelLine/FuelGradeID` | 4 |
| fuel_lines[].SALESQUANTITY | `FuelLine/SalesQuantity` | 11.912 |
| tender_lines[].TENDERAMOUNT | `TenderInfo/TenderAmount` | 20.00 |
| tender_lines[].TENDERCODE | `Tender/TenderCode` | 2 |
| tender_lines[].TENDERSUBCODE | `Tender/TenderSubCode` | VISA |

---

## 二、我们生成的 output vs 你之前放的 reference output

### 结构对比

| 项目 | 我们生成的 _pos_data.json | 你之前放的 reference |
|------|---------------------------|------------------------|
| 顶层结构 | `Transactions`, `SourceFile`, `ProcessedAt`, `ProcessingStatus`, `ExtractionDuration` | **相同** |
| Transactions 结构 | BULLOCHSHIFTID, STORELOCATIONID, regular_lines, tender_lines, fuel_lines 等 | **相同** |
| fuel_lines 字段 | DESCRIPTION, FUELGRADEID, SALESQUANTITY, TRANSACTIONID 等 | **相同** |
| tender_lines 字段 | TENDERAMOUNT, TENDERCODE, TENDERSUBCODE 等 | **相同** |

### 内容差异（仅会随时间/路径变化的部分）

| 字段 | 我们生成的 | 你之前放的（参考） |
|------|------------|---------------------|
| SourceFile | `test_data/error/naxml-posjournal 10477 035502 1.xml` | `posjournaltransaction/2026/03/02/ppret66021/naxml-posjournal 10477 035502 1.xml` |
| ProcessedAt | `2026-03-19T00:50:26.225252+00:00` | `2026-03-02T18:29:38.402025+00:00` |
| ExtractionDuration | 每次运行不同 | 每次运行不同 |

### 结论

- **_pos_data.json 结构**：与 reference 完全一致  
- **业务数据**（BULLOCHSHIFTID、STORELOCATIONID、Transactions 等）：与 reference 一致  
- **SourceFile**：不同，因为输入路径不同（reference 是上游路径，我们的是本地路径）  
- **ProcessedAt / ExtractionDuration**：每次运行都会不同，属于正常现象  

---

## 三、output 目录下还有哪些文件我们没生成

| 文件 | 我们是否生成 | 说明 |
|------|--------------|------|
| `_pos_data.json` | ✅ 是 | 已实现 |
| `_payload.json` | ❌ 否 | 计划中未实现，面向下游 API 的另一种格式 |
| `_shift_send_result.json` | ❌ 否 | 计划中未实现，shift 专用 |

---

## 四、快速验证

运行以下命令可重新生成 output 并对比：

```bash
python3 main.py -i "test_data/error/naxml-posjournal 10477 035502 1.xml"
```

输出文件：`output/10477 035502 1/_pos_data.json`
