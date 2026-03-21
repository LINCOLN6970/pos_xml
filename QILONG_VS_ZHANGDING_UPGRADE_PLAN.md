# 七龙 vs 張經：差异对比与升级计划

**目的**：列出两项目在标准化、注册机制、输入输出等方面的异同，并给出七龙向張經靠拢的修改计划。**本文档仅做计划，不修改代码。**

---

## 一、相同点

| 维度 | 相同之处 |
|------|----------|
| **最终输出** | 都是 `_pos_data.json` 结构（Transactions、fuel_lines、regular_lines、tender_lines 等） |
| **业务目标** | 都是 NAXML → JSON 提取 |
| **大 extractor 分层** | 都有 TransactionExtractor、ShiftSummaryExtractor，继承 BaseExtractor |
| **XSLT 入口** | 都接受 bytes 输入，经 XSLT 后再提取 |
| **registry 存在** | 七龙已有 `extractors/registry.py`（但未使用） |

---

## 二、不同点

### 2.1 标准化（XSLT）

| 项目 | XSLT 位置 | XSLT 作用 | 输出 XML 结构 |
|------|-----------|-----------|---------------|
| **張經** | `apply_xslt.py`，在 BaseExtractor 内部 | Transform001/002 把 NAXML 转成 **RBOBULLOCH***  schema（另一套标签） | `RBOBULLOCHTRANSACTIONENTITY`、`RBOBULLOCHTRANSACTIONLINEENTITY`、`RBOBULLOCHSHIFTENTITY` |
| **七龙** | `utils/xslt_processor.py`，在 main 中调用 | Normalize001 仅做 **标准化**，保持 NAXML 结构 | `SaleEvent`、`TransactionLine`、`FuelLine`、`ItemLine`、`TenderInfo` |

| 项目 | XSLT 加载方式 | 单例/复用 |
|------|---------------|-----------|
| **張經** | `GlobalXsltProcessor` 单例，每个 BaseExtractor 实例持有一份 | 单例 + 线程锁 |
| **七龙** | `xslt_processor.apply()` 模块级函数，懒加载 `_TRANSFORMS` | 模块级缓存，无显式单例 |

---

### 2.2 注册机制

| 项目 | 注册表 | 使用方式 | line extractor 调度 |
|------|--------|----------|---------------------|
| **張經** | `line_extractors/base.py` 的 `REGISTERED` | `get_extractors()` 返回所有 `@register` 的实例 | BaseExtractor 初始化时 `self.line_extractors = [e for e in all_extractors if ...]`，遍历调用 |
| **七龙** | `extractors/registry.py` 的 `REGISTERED` | **未被调用** | `transaction_extractor` 内 `if localname == "FuelLine":` 硬编码分发 |

| 项目 | line extractor 形式 | 扩展方式 |
|------|---------------------|----------|
| **張經** | 类 + `@register` + `FIELDS`/`COLL` 声明式 | 新增文件 + 类 + `@register`，无需改 transaction_extractor |
| **七龙** | 函数（`extract_fuel_line` 等） | 新增函数 + 在 transaction_extractor 里加 `elif` |

---

### 2.3 输入

| 项目 | 入口输入 | extract 方法签名 |
|------|----------|------------------|
| **張經** | `extract(blob_content: bytes, blob_name: str)` | 直接收 bytes，内部做 XSLT |
| **七龙** | `process_file(input_file, output_file)`，main 读文件得 bytes | `extract(root)` 收已解析的 root，XSLT 在 main 中完成 |

| 项目 | 输入来源 |
|------|----------|
| **張經** | 设计为 Azure Blob（bytes + 文件名），无 main，由外部调用 |
| **七龙** | 本地文件路径，main 负责读文件、选 extractor、写 JSON |

---

### 2.4 输出

| 项目 | 输出方式 |
|------|----------|
| **張經** | 返回 `Dict`，由调用方写文件 |
| **七龙** | main 直接 `write_json(result, output_file)` 写文件 |

---

### 2.5 其他差异

| 维度 | 張經 | 七龙 |
|------|------|------|
| **日志** | `logging.info`、`logging.error`、`logging.debug` | 无 |
| **异常** | `TransactionExtractionError`、`XsltApplyError`、`XsltLoadError` | 无自定义异常 |
| **类型注解** | `Dict[str, Any]`、`etree._Element` 等 | 基本无 |
| **Line 覆盖** | FuelLine、ItemLine、TenderLine、FuelPrepayLine、PayoutLine、DriveOffLine、PumpTestLine、SafeDropLine、DealLine、Header、ShiftSummary | FuelLine、ItemLine、TenderInfo、FuelPrepayLine、deal_lines |
| **特殊逻辑** | `_consolidate_drive_offs_and_pump_tests` | 无 |
| **Header** | 独立 `HeaderExtractor` | 在 transaction 层内联 |

---

## 三、七龙向張經靠拢的修改计划

### 阶段 1：注册机制（优先）

| 步骤 | 修改内容 | 目的 |
|------|----------|------|
| 1.1 | 在 `line_extractors/` 下建 `registered_base.py`（或扩展现有 `base.py`），定义 `LineExtractor` 基类，含 `TAG_LOCALNAME`、`RESULT_KEY`、`matches(localname)`、`extract(node, tx_id, seq)` | 统一 line 接口，便于注册与调度 |
| 1.2 | 定义 `REGISTERED` 列表和 `register` 装饰器 | 与張經一致 |
| 1.3 | 为 FuelLine、ItemLine、TenderInfo、FuelPrepayLine 各建一个 `@register` 类，内部调用现有 `extract_*_line` 函数 | 最小侵入，先打通注册流程 |
| 1.4 | 在 `line_extractors/__init__.py` 中 import 所有 line 模块，触发 `@register` | 保证注册在 import 时完成 |
| 1.5 | 修改 `transaction_extractor`：用 `for extractor in get_extractors(): if extractor.matches(localname): ...` 替代 `if/elif` 链 | 去掉硬编码分发 |
| 1.6 | 确认 `extractors/registry.py` 与 `line_extractors` 的注册表职责：若 registry 用于「大 extractor」，需与 line 的 `REGISTERED` 分离 | 避免概念混淆 |

---

### 阶段 2：输入统一为 bytes（可选）

| 步骤 | 修改内容 | 目的 |
|------|----------|------|
| 2.1 | 将 `BaseExtractor.extract(root)` 改为 `extract(content: bytes, source_name: str)` | 与張經接口一致，便于接 Azure Blob |
| 2.2 | 在 BaseExtractor 内持有一个 `xslt_processor`（或类似 GlobalXsltProcessor），`extract` 内先 `root = xslt_processor.apply(content)` 再 `_process_extraction(root)` | XSLT 逻辑下沉到 extractor，main 只负责拿 bytes |
| 2.3 | 修改 main：`content = open(...).read()` 后直接 `extractor.extract(content, input_file)`，不再在 main 中调 `xslt_processor` | main 职责简化 |

**注意**：若七龙希望保持「main 负责 XSLT、extractor 只收 root」的现状，可跳过阶段 2，仅做阶段 1。

---

### 阶段 3：日志与异常（可选）

| 步骤 | 修改内容 | 目的 |
|------|----------|------|
| 3.1 | 在 extractors 中加 `logging.info`、`logging.warning`、`logging.error` | 便于排查问题 |
| 3.2 | 建 `common/error_handler`，定义 `TransactionExtractionError`、`XsltApplyError` 等 | 与張經一致，便于上层统一处理 |

---

### 阶段 4：扩展 Line 类型（按需）

| 步骤 | 修改内容 | 目的 |
|------|----------|------|
| 4.1 | 新增 PayoutLine、DriveOffLine、PumpTestLine、SafeDropLine 的 `@register` 类 | 与張經 line 覆盖对齐 |
| 4.2 | 若需要，实现 `_consolidate_drive_offs_and_pump_tests` | 与張經业务逻辑一致 |

---

### 阶段 5：声明式 FIELDS/COLL（可选，工作量大）

| 步骤 | 修改内容 | 目的 |
|------|----------|------|
| 5.1 | 将 line extractor 从「函数 + 手写字段」改为「类 + FIELDS/COLL 声明」 | 与張經声明式风格一致 |
| 5.2 | 基类 `extract()` 按 FIELDS/COLL 自动遍历，适配 NAXML 命名空间 | 需处理 `n:` 前缀、嵌套结构 |

**注意**：七龙当前是 NAXML 结构，張經是 RBOBULLOCH* 结构，FIELDS 的 tag 名、路径会不同，需单独设计映射。

---

## 四、建议实施顺序

1. **阶段 1**（注册机制）：收益高、改动集中，优先做。
2. **阶段 3**（日志与异常）：改动小，可随时加。
3. **阶段 2**（bytes 输入）：若确定要接 Azure Blob，再做。
4. **阶段 4**（扩展 Line）：按业务需求决定。
5. **阶段 5**（声明式）：可选，工作量大，建议在注册机制稳定后再考虑。

---

## 五、总结表

| 维度 | 張經 | 七龙（现状） | 七龙（目标，阶段 1 后） |
|------|------|--------------|-------------------------|
| XSLT | 在 extractor 内，转 RBOBULLOCH* | 在 main 内，标准化 NAXML | 可保持现状 |
| 注册 | 使用，line 全注册 | 未使用 | 使用，line 全注册 |
| 输入 | bytes + 文件名 | 文件路径 → main 读 bytes | 可保持或改为 bytes |
| 调度 | 遍历 line_extractors | if/elif 硬编码 | 遍历 get_extractors() |
| 扩展 | 加类 + @register | 加函数 + elif | 加类 + @register |
