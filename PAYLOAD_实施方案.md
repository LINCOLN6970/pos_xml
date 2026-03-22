# _payload.json 实施方案（仅方案，无代码）

---

## 一、目标

在现有 `_pos_data.json` 基础上，增加 `_payload.json` 输出，满足下游 API（如 D365 Commerce）所需的格式。

---

## 二、为什么要这样做

| 原因 | 说明 |
|------|------|
| **格式分离** | _pos_data 是内部提取格式；_payload 是下游 API 约定格式，两者职责不同 |
| **最小侵入** | 在 process_file 内复用已有的 result，无需改 extractor 逻辑 |
| **可配置** | ProductId、ChannelId 等可后续从配置或映射表获取，先占位即可 |

---

## 三、需要做什么（按步骤）

### 步骤 1：新建 `utils/payload_builder.py`

**为什么**：把 pos → payload 的转换抽成独立模块，职责清晰，便于单测和修改。

**模块职责**：
- 提供函数 `build_payload(pos_data: dict) -> dict | None`
- 输入：extractor 返回的 result（含 Transactions）
- 输出：符合下游 API 的 payload 结构；无 Transactions 时返回 None

---

### 步骤 2：实现类型转换工具函数

**为什么**：pos 中金额、数量多为字符串，payload 需要数字。

**需要实现的函数**：
- `_float(s, default)`：字符串 → float，无效则返回 default
- `_receipt_time_to_seconds("HH:MM:SS")`：时间 → 当日秒数（payload 的 ReceiptTime IntegerValue）
- `_date_time_to_unix(date_str, time_str)`：日期+时间 → Unix 秒（TransactionTime）
- `_ext_prop_str / _ext_prop_decimal / _ext_prop_int`：构造 ExtensionProperties 的 Key-Value

---

### 步骤 3：实现交易头映射

**为什么**：payload 顶层需要 Id、StoreId、TerminalId、TotalAmount 等。

**映射规则**（示例）：
- `TRANSACTIONID` → `Id`：格式为 `"000000000-" + TRANSACTIONID`
- `STORELOCATIONID` → `StoreId`：格式为 `"ac4_" + STORELOCATIONID`
- `REGISTERID` + `STORELOCATIONID` → `TerminalId`：`"33370-1"`
- `TRANSACTIONTOTALGRANDAMOUNT` → `TotalAmount`：字符串 → float
- `BULLOCHSHIFTID`、`CASHIERID`、`LPELOYALTYTRANSACTIONID` 等 → 放入 `ExtensionProperties`

**为什么用 ExtensionProperties**：下游 API 用 Key-Value 扩展字段，不改主结构即可携带额外信息。

---

### 步骤 4：实现 fuel_lines → SalesLines

**为什么**：fuel 行是销量主数据，下游需 SalesLines 结构。

**映射规则**（示例）：
- `SALESAMOUNT`、`SALESQUANTITY`、`REGULARSELLPRICE` → `TotalAmount`、`Quantity`、`Price`
- `FUELGRADEID`、`FUELPOSITIONID`、`SERVICELEVELCODE`、`ENTRYMETHOD` → 放入该行的 ExtensionProperties
- `LineType` 固定为 4（燃料行）
- `ProductId`、`ListingId`、`ItemId`：先用常量占位，后续接产品目录映射

**为什么先占位**：ProductId 依赖外部产品目录，第一阶段可写死，后面再接入配置或 API。

---

### 步骤 5：实现 tender_lines → TenderLines

**为什么**：支付行是下游对账和结算所需。

**映射规则**（示例）：
- `TENDERAMOUNT` → `Amount`
- `TENDERCODE` → `TenderTypeId`
- `TENDERSUBCODE` → 放入 ExtensionProperties

---

### 步骤 6：在 main.py 的 process_file 中调用

**为什么**：在写完 _pos_data.json 后，用同一 result 生成 payload，避免重复解析。

**调用位置**：在 `write_json(result, output_file)` 之后。

**逻辑**：
- 调用 `payload = build_payload(result)`
- 若 payload 非 None，则 `payload_file = 同目录下的 _payload.json`，调用 `write_json(payload, payload_file)`

**为什么放同目录**：output/<id>/ 下同时有 _pos_data 和 _payload，便于对应和排查。

---

## 四、固定/占位字段

| 字段 | 示例值 | 来源 | 说明 |
|------|--------|------|------|
| ChannelId | 5637192654 | 占位常量 | 后续改为配置 |
| ProductId / ListingId | 5637146394 | 占位常量 | 后续接 FuelGradeID → 产品目录 |
| ItemId | "000006056" | 占位常量 | 同上 |
| InternalTransactionId | UUID | 运行时生成 | 用 `uuid.uuid4()` |
| DocumentStatusValue、StatusValue 等 | 0、4 | 固定 | 按下游枚举填 |

---

## 五、参考

- 字段映射细节见 `POS_TO_PAYLOAD_PLAN.md`
- 目标结构可对照 `output/10477 035502 1/_payload.json`
