# 張經 vs 七龙 代码对比

两个项目都做 NAXML → JSON 提取，但**输入 XML 格式不同**，架构和写法差异较大。

---

## 一、输入 XML 格式差异（关键）

| 项目 | 输入 XML 格式 | 说明 |
|------|---------------|------|
| **張經** | 已转换的 XML（`RBOBULLOCHTRANSACTIONENTITY`、`RBOBULLOCHTRANSACTIONLINEENTITY`） | 先经 XSLT 转换，再提取 |
| **七龙** | 原始 NAXML（`SaleEvent`、`TransactionLine`、`FuelLine`、`ItemLine`） | 直接解析原始 NAXML |

**張經** 的 XML 是 XSLT 转换后的结构，标签名、层级与 NAXML 不同。

---

## 二、架构设计对比

### 1. 目录结构

| 張經 | 七龙 |
|------|------|
| 根目录直接放 extractors | `extractors/` + `line_extractors/` 分离 |
| 无 `utils/` | 有 `utils/xml_loader.py`、`utils/file_writer.py` |
| 有 `xslt/` 目录 | 无 XSLT |
| 有 `common/error_handler` | 无统一异常处理 |
| 无独立 `main.py`（可能由外部调用） | 有 `main.py` 入口 |

### 2. 数据流

**張經：**
```
blob_content (bytes) → XSLT 转换 → 转换后 XML 树 → extractors → JSON
```

**七龙：**
```
文件路径 → load_xml → 原始 XML 树 → extractors → write_json → 文件
```

### 3. 入口与调用方式

| 项目 | 入口 | 输入 | 输出 |
|------|------|------|------|
| **張經** | 无 main，由外部调用 `extract(blob_content, blob_name)` | bytes + 文件名 | Dict（由调用方写文件） |
| **七龙** | `main.py`，支持 `-i`、`-d` | 文件路径 | 直接写 `output/<id>/_pos_data.json` |

---

## 三、Line Extractor 设计对比

### 張經：声明式 + 注册模式

```python
# 用 FIELDS、COLL 声明字段映射，基类统一提取
@register
class FuelLineExtractor(Extractor):
    TAG = "RBOBULLOCHTRANSACTIONLINEENTITY"
    LINETYPE = "FuelLine"
    GROUP = "fuel_lines"
    FIELDS = [
        ("DESCRIPTION", "DESCRIPTION", None),
        ("FUELGRADEID", "FUELGRADEID", None),
        ...
    ]
    COLL = [("", PROMO_FIELDS, "discount_lines")]
```

- **特点**：字段映射用 `FIELDS`、`COLL` 声明，基类 `extract()` 统一遍历
- **优点**：新增 line 类型只需加类 + 声明，扩展简单
- **缺点**：依赖转换后 XML 结构，嵌套复杂时 `COLL` 配置会变复杂

### 七龙：命令式 + 函数

```python
# 手写提取逻辑，按 NAXML 结构逐字段取
def extract_fuel_line(fuel_line_node, transaction_id, sequence_number):
    return {
        "DESCRIPTION": get_text(fuel_line_node, "Description"),
        "FUELGRADEID": get_text(fuel_line_node, "FuelGradeID"),
        ...
    }
```

- **特点**：每个 line 类型一个函数，显式处理 NAXML 的命名空间和嵌套
- **优点**：逻辑清晰，易调试，适配原始 NAXML
- **缺点**：新增 line 类型要写新函数，重复代码稍多

---

## 四、代码写法对比

### 1. 命名空间

| 張經 | 七龙 |
|------|------|
| 不处理命名空间（XSLT 输出通常无 ns） | 显式 `ns = {"n": NAXML_NS}`，所有 `find` 传 `namespaces=ns` |

### 2. 类型注解

| 張經 | 七龙 |
|------|------|
| 使用 `typing`（`Dict[str, Any]`、`etree._Element`） | 基本无类型注解 |

### 3. 日志与异常

| 張經 | 七龙 |
|------|------|
| `logging.info`、`logging.error` | 无日志 |
| 自定义 `TransactionExtractionError`、`XsltApplyError` | 无自定义异常 |

### 4. 注册 / 调度

| 張經 | 七龙 |
|------|------|
| `@register` 装饰器，`get_extractors()` 返回所有 line extractor 实例 | 无注册，在 `transaction_extractor` 里按 `tag_localname` 硬编码分发 |

### 5. 特殊逻辑

| 張經 | 七龙 |
|------|------|
| `_consolidate_drive_offs_and_pump_tests`：合并 drive-off、pump test 到对应销售交易 | 无此逻辑 |
| 区分 `RBOBULLOCHTRANSACTIONLINEENTITY` 和 `RBOBULLOCHTRANSACTIONDEALENTITY` | 统一从 `TransactionLine` 子元素提取 |

---

## 五、Line 类型覆盖

| Line 类型 | 張經 | 七龙 |
|-----------|------|------|
| FuelLine | ✅ | ✅ |
| ItemLine | ✅ | ✅ |
| TenderLine | ✅ | ✅ |
| FuelPrepayLine | ✅ | ✅ |
| PayoutLine | ✅ | ❌ |
| DriveOffLine | ✅ | ❌ |
| PumpTestLine | ✅ | ❌ |
| SafeDropLine | ✅ | ❌ |
| DealLine | ✅ | ✅（在 transaction 层从 Extension 提取） |
| Header | ✅ 独立 HeaderExtractor | ❌ 在 transaction 层内联 |
| ShiftSummary | ✅ 独立 ShiftSummaryExtractor | ✅ 在 shift_summary_extractor 内联 |

---

## 六、总结表

| 维度 | 張經 | 七龙 |
|------|------|------|
| **输入** | XSLT 转换后的 XML（bytes） | 原始 NAXML（文件路径） |
| **预处理** | XSLT 标准化 | 无 |
| **Line 设计** | 声明式 + 注册 | 命令式 + 函数 |
| **扩展方式** | 加类 + 声明 | 加函数 + 分发 |
| **类型/日志** | 有 | 无 |
| **入口** | 库模式（被调用） | 独立 CLI（main.py） |
| **Line 覆盖** | 更全（含 payout、drive_off 等） | 核心类型（fuel、item、tender、deal） |

---

## 七、可借鉴点

1. **張經 → 七龙**：声明式 FIELDS/COLL、注册模式、日志与异常处理
2. **七龙 → 張經**：若需支持原始 NAXML，可参考七龙的命名空间和 XPath 写法；若需 CLI，可参考 main.py 设计
