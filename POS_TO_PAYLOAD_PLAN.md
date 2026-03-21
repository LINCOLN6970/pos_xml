# _pos_data.json → _payload.json 转换计划

**目标**：在现有 `_pos_data.json` 基础上，生成面向下游 API 的 `_payload.json` 格式。

---

## 一、格式对比

| 维度 | _pos_data.json（当前输出） | _payload.json（目标） |
|------|---------------------------|------------------------|
| **顶层结构** | `Transactions[]` + `SourceFile` 等 | 扁平结构，单笔交易 |
| **字段风格** | 全大写（BULLOCHSHIFTID） | PascalCase（BullochShiftId） |
| **数值类型** | 字符串（"20.00"） | 数字（20.0） |
| **时间** | "18:53:42" | Unix 秒（1772416422）或 IntegerValue（68022） |
| **行类型** | fuel_lines, tender_lines 分开 | SalesLines, TenderLines 统一 |
| **扩展数据** | 直接字段 | ExtensionProperties（Key + Value） |
| **ID 格式** | "035502" | "000000000-035502" |

---

## 二、主要字段映射（pos → payload）

### 2.1 交易头

| _pos_data.json | _payload.json | 转换规则 |
|----------------|---------------|----------|
| TRANSACTIONID | Id | 前缀补零："000000000-" + TRANSACTIONID |
| STORELOCATIONID | StoreId | "ac4_" + STORELOCATIONID |
| REGISTERID | TerminalId | STORELOCATIONID + "-" + REGISTERID |
| BULLOCHSHIFTID | ExtensionProperties.BullochShiftId | 直接映射 |
| TRANSACTIONTOTALGRANDAMOUNT | TotalAmount, GrossAmount 等 | 字符串 → float |
| BUSINESSDATE | TransactionDate, BusinessDate | 日期格式转换 |
| RECEIPTTIME | ReceiptTime (IntegerValue) | "18:53:42" → 秒数（如 68022） |
| CASHIERID | ExtensionProperties.CashierId | 直接映射 |
| LPELOYALTYTRANSACTIONID | ExtensionProperties.LpeLoyaltyTransactionId | 直接映射 |
| MOBILAINVOICENUMBER | ExtensionProperties.MobilaInvoiceNumber | 直接映射 |

### 2.2 fuel_lines → SalesLines

| _pos_data (fuel_lines) | _payload (SalesLines) | 转换规则 |
|------------------------|------------------------|----------|
| DESCRIPTION | Description | 直接映射 |
| SALESAMOUNT | TotalAmount, NetAmount 等 | 字符串 → float |
| SALESQUANTITY | Quantity, QuantityOrdered | 字符串 → float |
| REGULARSELLPRICE / ACTUALSALESPRICE | Price, OriginalPrice | 字符串 → float |
| FUELGRADEID | ExtensionProperties.FuelGradeId | 直接映射 |
| FUELPOSITIONID | ExtensionProperties.FuelPositionId | 直接映射 |
| SERVICELEVELCODE | ExtensionProperties.ServiceLevelCode | 直接映射 |
| ENTRYMETHOD | ExtensionProperties.EntryMethod | 直接映射 |
| TRANSACTIONLINESEQUENCENUMBER | LineId, LineNumber | 直接映射 |
| （需新增） | ProductId, ListingId | **需外部映射**（FuelGradeID → 产品目录） |
| （需新增） | ItemId | **需外部映射**（如 "000006056"） |
| （需新增） | UnitOfMeasureSymbol | 从 XML 取或默认 "L" |
| （需新增） | LineType (IntegerValue: 4) | 固定值（燃料行） |

### 2.3 tender_lines → TenderLines

| _pos_data (tender_lines) | _payload (TenderLines) | 转换规则 |
|--------------------------|-------------------------|----------|
| TENDERAMOUNT | Amount | 字符串 → float |
| TENDERCODE | TenderTypeId | 直接映射 |
| TENDERSUBCODE | ExtensionProperties.TenderSubCode | 直接映射 |
| TRANSACTIONLINESEQUENCENUMBER | TenderLineId, LineNumber | 直接映射 |

### 2.4 固定 / 需配置字段

| 字段 | 示例值 | 来源 |
|------|--------|------|
| ChannelId | 5637192654 | 配置或外部映射 |
| DocumentStatusValue | 0 | 枚举/固定 |
| StatusValue | 4 | 枚举/固定 |
| CurrencyCode | "CAD" | 配置或 XML |
| LanguageId | "en-CA" | 配置 |
| InternalTransactionId | UUID | 新生成 |

---

## 三、需要完成的工作

### 阶段 A：基础转换（可纯从 _pos_data 实现）

| 步骤 | 内容 | 说明 |
|------|------|------|
| A.1 | 新建 `utils/payload_builder.py` 或 `transformers/pos_to_payload.py` | 转换逻辑模块 |
| A.2 | 实现 pos → payload 的字段映射 | 按上表逐字段转换 |
| A.3 | 实现类型转换 | 字符串 → float、日期格式、时间 → 秒数 |
| A.4 | 实现 ExtensionProperties 构建 | 把 BULLOCHSHIFTID、CashierId 等放入 Key-Value |
| A.5 | 实现 fuel_lines → SalesLines | 含 LineType、ExtensionProperties |
| A.6 | 实现 tender_lines → TenderLines | 含 ExtensionProperties |
| A.7 | 在 main 或 process_file 中调用转换 | `payload = build_payload(pos_data)` |
| A.8 | 写第二个 JSON 文件 | `output/<id>/_payload.json` |

### 阶段 B：外部依赖（需配置或接口）

| 步骤 | 内容 | 说明 |
|------|------|------|
| B.1 | ProductId / ListingId 映射 | FuelGradeID → 产品目录 ID，需配置表或 API |
| B.2 | ItemId 映射 | 产品项 ID，同上 |
| B.3 | ChannelId | 门店/渠道 ID，需配置 |
| B.4 | InternalTransactionId | 可本地生成 UUID，或从上游获取 |

### 阶段 C：特殊处理

| 步骤 | 内容 | 说明 |
|------|------|------|
| C.1 | ReceiptTime 转 IntegerValue | "18:53:42" → 当日秒数（或参考现有 payload 的计算方式） |
| C.2 | TransactionTime (Unix) | 1772416422，需从日期+时间计算 |
| C.3 | regular_lines (ItemLine) | 若有，需类似 fuel_lines 的 SalesLines 转换 |
| C.4 | deal_lines、discount_lines | 映射到 DiscountLines、PeriodicDiscount 等 |

---

## 四、实施顺序建议

1. **阶段 A.1–A.4**：搭建转换模块，先做交易头和 ExtensionProperties。
2. **阶段 A.5–A.6**：实现 fuel_lines、tender_lines 转换。
3. **阶段 A.7–A.8**：接入 main 流程，输出 `_payload.json`。
4. **阶段 B**：根据是否有产品目录/配置，实现或占位 ProductId、ChannelId 等。
5. **阶段 C**：处理时间、ItemLine、折扣等边缘情况。

---

## 五、参考：payload 顶层结构

```json
{
  "DocumentStatusValue": 0,
  "StatusValue": 4,
  "Id": "000000000-035502",
  "StoreId": "ac4_33370",
  "TerminalId": "33370-1",
  "TotalAmount": 20.0,
  "TransactionDate": "2026-03-01",
  "SalesLines": [...],
  "TenderLines": [...],
  "ExtensionProperties": [...]
}
```

---

## 六、预估工作量

| 阶段 | 预估时间 |
|------|----------|
| A（基础转换） | 2–4 小时 |
| B（外部映射） | 视配置/接口而定 |
| C（边缘情况） | 1–2 小时 |
