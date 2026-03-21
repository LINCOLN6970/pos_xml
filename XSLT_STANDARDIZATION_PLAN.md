# 七龙项目：自定义 XSLT 标准化方案与计划

**约束**：输出结构（_pos_data.json）不变；编写一套独立的 XSLT；本文档仅提供方案与计划，不修改代码。

---

## 一、目标

```
Azure Blob / 本地文件
    → 原始 XML（可能含变体）
    → 自定义 XSLT 标准化
    → 标准化 NAXML（与现有 extractors 兼容）
    → Extractors 提取
    → _pos_data.json（结构不变）
```

---

## 二、XSLT 输出结构约束

XSLT 输出必须与**当前 extractors 的预期**一致，才能保证输出 JSON 不变。

### 2.1 Extractors 依赖的 XML 结构

| 层级 | 元素/路径 | 用途 |
|------|-----------|------|
| 根 | `NAXML-POSJournal` | 根元素 |
| 命名空间 | `xmlns="http://www.naxml.org/POSBO/Vocabulary/2003-10-16"` | 所有 find 使用 `n:` 前缀 |
| 顶层 | `TransmissionHeader/StoreLocationID` | STORELOCATIONID |
| | `JournalReport/JournalHeader` | BULLOCHSHIFTID, PRIMARYREPORTPERIOD |
| | `JournalReport/SaleEvent` | 交易 |
| SaleEvent | `TransactionID`, `BusinessDate`, `ReceiptDate`, `ReceiptTime`, `RegisterID`, `CashierID` | 交易头 |
| | `TransactionSummary/TransactionTotalGrandAmount` 等 | 金额汇总 |
| | `Extension/LoyaltyTransactionID`, `MobilaInvoiceNumber` | 扩展 |
| | `TransactionDetailGroup/TransactionLine` | 行 |
| TransactionLine | `TransactionLineSequenceNumber` | 行号 |
| | 子元素：`FuelLine`, `ItemLine`, `TenderInfo`, `FuelPrepayLine` | 行类型 |
| FuelLine | `Description`, `FuelGradeID`, `FuelPositionID`, `ServiceLevelCode`, `RegularSellPrice`, `ActualSalesPrice`, `SalesAmount`, `SalesQuantity` | fuel_lines |
| | `EntryMethod` 的 `method` 属性 | ENTRYMETHOD |
| | `Promotion`（可选） | discount_lines |
| ItemLine | `Description`, `SalesAmount`, `RegularSellPrice`, `ActualSalesPrice`, `SalesQuantity` | regular_lines |
| | `ItemCode/InventoryItemID`, `ItemCode/POSCode`, `ItemCode/POSCodeFormat`, `ItemCode/POSCodeModifier` | |
| | `ItemTax`（多个） | charge_lines |
| | `Promotion`（可选） | discount_lines |
| | `EntryMethod` 的 `method` 属性 | |
| TenderInfo | `Tender/TenderCode`, `Tender/TenderSubCode` | tender_lines |
| | `TenderAmount` | |
| Shift | `OtherEvent`（含 `ShiftDetail detailType="close"`） | ShiftSummary |
| | `Extension/Statistics/CustomerCount` 等 | |
| Deal | `Extension/DealGroups/DealGroup` | deal_lines |

### 2.2 XSLT 输出必须满足

- 保留上述元素与层级
- 保留默认命名空间 `http://www.naxml.org/POSBO/Vocabulary/2003-10-16`
- 属性如 `EntryMethod method="xxx"`、`currency="CAD"` 等保持可用
- 元素顺序可调整，但父子关系不变

---

## 三、XSLT 标准化内容（建议）

### 3.1 建议处理的项

| 类别 | 内容 | 说明 |
|------|------|------|
| 命名空间 | 统一为 NAXML 默认 ns | 处理多 ns、错误 ns、无 ns |
| 空白 | 去除多余空白、统一换行 | `normalize-space`、`indent` |
| 编码 | 统一为 UTF-8 | `xsl:output encoding="utf-8"` |
| 缺失可选元素 | 不补全 | 保持与现有逻辑一致，由 extractors 处理空值 |
| 元素顺序 | 可调整 | 不影响提取 |
| 属性 | 保留 `method`、`currency`、`uom` 等 | extractors 依赖这些属性 |

### 3.2 不建议在 XSLT 中做的

- 改变元素名、层级、命名空间 URI
- 改变业务数据（金额、日期等）
- 删除 extractors 依赖的元素或属性

---

## 四、XSLT 设计方案

### 4.1 方案 A：最小标准化（推荐起步）

**作用**：仅做结构整理，不改变业务数据。

- 输入：任意 NAXML 3.6 兼容 XML
- 输出：与当前 test_data 样本结构一致的 NAXML
- 步骤：
  1. 复制整树，保留命名空间
  2. 规范化空白
  3. 统一 `xsl:output`

**适用**：输入已基本符合 NAXML，只需轻度整理。

### 4.2 方案 B：命名空间标准化

**作用**：处理命名空间变体。

- 输入：可能有不同 ns、多前缀、无 ns
- 输出：统一使用 `http://www.naxml.org/POSBO/Vocabulary/2003-10-16`
- 步骤：
  1. 用 `local-name()` 匹配元素
  2. 输出时写入统一默认 ns
  3. 保持元素与属性不变

**适用**：不同来源的 NAXML 存在 ns 差异。

### 4.3 方案 C：结构修复

**作用**：修复已知结构问题。

- 输入：可能有缺失、错位、别名
- 输出：符合 extractors 预期的结构
- 步骤：
  1. 定义「元素 → 标准路径」映射
  2. 缺失可选节点：可输出空元素或省略（与现有逻辑一致）
  3. 错误层级：按规则重排

**适用**：有明确的结构问题需要修复。

---

## 五、XSLT 文件规划

### 5.1 文件组织

```
pos_xml_qilong/
  xslt/
    Normalize001.xsl    # 方案 A：最小标准化
    Normalize002.xsl    # 方案 B：命名空间标准化（可选，按需启用）
```

- 可先只实现 `Normalize001.xsl`，验证通过后再考虑 002。

### 5.2 执行顺序

```
原始 XML → Normalize001 → [Normalize002] → 标准化 XML → Extractors
```

- 若 001 已满足需求，可不使用 002。

### 5.3 与張經 XSLT 的差异

| 项目 | 張經 Transform001/002 | 七龙 Normalize001/002 |
|------|------------------------|------------------------|
| 输出结构 | RBOBULLOCH*（另一套 schema） | NAXML（SaleEvent、FuelLine 等） |
| 用途 | 转换为下游系统格式 | 标准化后仍由现有 extractors 处理 |
| Extractors | 需适配新结构 | 无需改动 |

---

## 六、实施计划（仅规划，不写代码）

### 阶段 1：需求与样本

1. 收集 Blob 中实际 XML 样本（至少 3–5 个）
2. 与当前 test_data 样本对比，列出差异：
   - 命名空间
   - 元素/属性缺失或多余
   - 结构差异
3. 确定 XSLT 需要处理的变体清单

### 阶段 2：XSLT 编写

1. 编写 `Normalize001.xsl`（最小标准化）
2. 用 lxml 或 xsltproc 在样本上测试
3. 确认输出可被现有 extractors 正确解析
4. 若需要，再编写 `Normalize002.xsl` 并测试

### 阶段 3：集成（后续，本文档不涉及代码修改）

1. 新增 `utils/xslt_processor.py`
2. 修改 `main.py` / `process_file`，在 Blob 或文件输入后插入 XSLT 步骤
3. 增加 Azure Blob 下载与调用入口
4. 端到端测试

---

## 七、验证清单

XSLT 完成后，需验证：

- [ ] 用当前 test_data 样本经 XSLT 后，`_pos_data.json` 与不经 XSLT 时一致
- [ ] 用 Blob 中的变体样本经 XSLT 后，能正确提取并生成 `_pos_data.json`
- [ ] Transaction、Shift Summary 两种格式均通过
- [ ] fuel_lines、regular_lines、tender_lines、deal_lines 等结构完整

---

## 八、风险与注意

1. **过度转换**：XSLT 若改变 extractors 依赖的结构，会导致提取失败，需严格对照 2.1 节约束。
2. **性能**：大文件（如 shift summary）经 XSLT 可能增加耗时，需在真实数据上测试。
3. **版本**：NAXML 若有 3.5 / 3.6 / 3.7 等版本差异，XSLT 需考虑兼容或分版本处理。
