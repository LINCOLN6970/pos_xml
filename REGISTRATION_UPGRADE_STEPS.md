# 阶段 1：注册机制 — 分步操作手册

**目标**：用 `@register` 替代 transaction_extractor 中的 if/elif 硬编码，新增 line 类型时只需加类 + 装饰器，无需改主逻辑。

**预估总时长**：约 **45–60 分钟**（熟悉代码后约 30–40 分钟）

---

## 步骤 1.1：在 line_extractors/base.py 中增加 LineExtractor 基类和注册表

**为什么要做**：统一 line extractor 的接口（`matches`、`extract`），方便用循环替代 if/elif；注册表用于收集所有 `@register` 的类。

**怎么做**：

1. 打开 `line_extractors/base.py`
2. 在文件末尾（`get_attr` 函数之后）添加以下内容：

```python
# --- 注册机制 ---
REGISTERED = []


def register(cls):
    """装饰器：将类加入 REGISTERED，供 get_line_extractors() 使用。"""
    REGISTERED.append(cls)
    return cls


def get_line_extractors():
    """返回所有已注册的 line extractor 实例。"""
    return [cls() for cls in REGISTERED]


class LineExtractor:
    """Line extractor 基类。子类需定义 TAG_LOCALNAME、RESULT_KEY，并实现 extract。"""

    TAG_LOCALNAME = ""   # 如 "FuelLine"
    RESULT_KEY = ""      # 如 "fuel_lines"

    @classmethod
    def matches(cls, localname: str) -> bool:
        return localname == cls.TAG_LOCALNAME

    def extract(self, node, transaction_id: str, sequence_number: str):
        """子类实现，或委托给现有 extract_*_line 函数。"""
        raise NotImplementedError
```

3. 保存文件。

**预估时间**：5 分钟

---

## 步骤 1.2：为 FuelLine 创建 @register 类

**为什么要做**：把现有 `extract_fuel_line` 包装成可注册的类，作为第一个示例。

**怎么做**：

1. 打开 `line_extractors/fuel_extractor.py`
2. 在文件顶部 import 后增加：

```python
from line_extractors.base import LineExtractor, register
```

3. 在文件末尾（`_extract_fuel_discount_lines` 函数之后）添加：

```python
@register
class FuelLineExtractor(LineExtractor):
    TAG_LOCALNAME = "FuelLine"
    RESULT_KEY = "fuel_lines"

    def extract(self, node, transaction_id: str, sequence_number: str):
        return extract_fuel_line(node, transaction_id, sequence_number)
```

4. 保存文件。

**预估时间**：3 分钟

---

## 步骤 1.3：为 ItemLine 创建 @register 类

**为什么要做**：与 FuelLine 同理，扩展注册机制。

**怎么做**：

1. 打开 `line_extractors/item_extractor.py`
2. 在文件顶部 import 后增加：

```python
from line_extractors.base import LineExtractor, register
```

3. 在文件末尾添加：

```python
@register
class ItemLineExtractor(LineExtractor):
    TAG_LOCALNAME = "ItemLine"
    RESULT_KEY = "regular_lines"

    def extract(self, node, transaction_id: str, sequence_number: str):
        return extract_item_line(node, transaction_id, sequence_number)
```

4. 保存文件。

**预估时间**：3 分钟

---

## 步骤 1.4：为 TenderInfo 创建 @register 类

**为什么要做**：同上。

**怎么做**：

1. 打开 `line_extractors/tender_extractor.py`
2. 在文件顶部 import 后增加：

```python
from line_extractors.base import LineExtractor, register
```

3. 在文件末尾添加：

```python
@register
class TenderLineExtractor(LineExtractor):
    TAG_LOCALNAME = "TenderInfo"
    RESULT_KEY = "tender_lines"

    def extract(self, node, transaction_id: str, sequence_number: str):
        return extract_tender_line(node, transaction_id, sequence_number)
```

4. 保存文件。

**预估时间**：3 分钟

---

## 步骤 1.5：为 FuelPrepayLine 创建 @register 类

**为什么要做**：`_extract_fuel_prepay_line` 在 transaction_extractor 中，需要单独建类并注册。可选方案：  
A) 把函数移到 `line_extractors/fuel_prepay_extractor.py`；  
B) 在 transaction_extractor 中建类并 import 到 line_extractors。  
为简单起见，建议新建 `fuel_prepay_extractor.py`。

**怎么做**：

1. 新建文件 `line_extractors/fuel_prepay_extractor.py`
2. 写入以下内容：

```python
from line_extractors.base import LineExtractor, register, get_text


def extract_fuel_prepay_line(node, transaction_id: str, sequence_number: str):
    """Stub for FuelPrepayLine - returns minimal structure."""
    return {
        "TRANSACTIONID": transaction_id,
        "TRANSACTIONLINESEQUENCENUMBER": sequence_number,
        "SALESAMOUNT": get_text(node, "SalesAmount"),
    }


@register
class FuelPrepayLineExtractor(LineExtractor):
    TAG_LOCALNAME = "FuelPrepayLine"
    RESULT_KEY = "fuel_prepay_lines"

    def extract(self, node, transaction_id: str, sequence_number: str):
        return extract_fuel_prepay_line(node, transaction_id, sequence_number)
```

3. 注意：`base.py` 中的 `get_text` 签名是 `get_text(node, tag_name)`，这里 `node` 是 FuelPrepayLine 节点，需用 `get_text(node, "SalesAmount")`。  
4. 检查 `line_extractors/base.py` 的 `get_text` 是否支持 `node` 为 `FuelPrepayLine` 这种根节点——当前 `get_text` 用 `node.find(f"n:{tag_name}", ...)`，对 `SalesAmount` 子元素有效。  
5. 保存文件。

**预估时间**：5 分钟

---

## 步骤 1.6：创建 line_extractors/__init__.py 并触发注册

**为什么要做**：import 时执行各模块的 `@register`，保证 `REGISTERED` 在调用 `get_line_extractors()` 前已填满。

**怎么做**：

1. 新建文件 `line_extractors/__init__.py`
2. 写入：

```python
from line_extractors.base import (
    tag_localname,
    get_text,
    get_attr,
    get_line_extractors,
    LineExtractor,
    register,
)

# 触发注册：import 各 line 模块，使 @register 装饰器执行
from line_extractors import fuel_extractor
from line_extractors import item_extractor
from line_extractors import tender_extractor
from line_extractors import fuel_prepay_extractor

__all__ = [
    "tag_localname",
    "get_text",
    "get_attr",
    "get_line_extractors",
    "LineExtractor",
    "register",
    "fuel_extractor",
    "item_extractor",
    "tender_extractor",
    "fuel_prepay_extractor",
]
```

3. 保存文件。

**预估时间**：5 分钟

---

## 步骤 1.7：修改 transaction_extractor 使用注册表

**为什么要做**：用 `for extractor in get_line_extractors()` 替代 if/elif 链，实现基于注册的调度。

**怎么做**：

1. 打开 `extractors/transaction_extractor.py`
2. 修改 import 部分：

```python
# 修改前
from line_extractors import fuel_extractor, item_extractor, tender_extractor

# 修改后
from line_extractors import get_line_extractors
```

3. 删除常量 `LINE_TYPES = ("FuelLine", "ItemLine", "TenderInfo", "FuelPrepayLine")`（或保留作注释，后续可删）
4. 找到 `for child in tx_line:` 循环内的 if/elif 块（约第 70–91 行），替换为：

```python
            for child in tx_line:
                localname = tag_localname(child)
                for extractor in get_line_extractors():
                    if extractor.matches(localname):
                        result[extractor.RESULT_KEY].append(
                            extractor.extract(child, tx_id, seq_num)
                        )
                        break
```

5. 删除 `_extract_fuel_prepay_line` 函数（已移到 fuel_prepay_extractor.py）
6. 保存文件。

**预估时间**：8 分钟

---

## 步骤 1.8：验证

**为什么要做**：确认重构后行为与原来一致。

**怎么做**：

1. 在项目根目录执行：

```bash
python3 main.py -i "test_data/error/naxml-posjournal 10477 035502 1.xml"
```

2. 检查是否输出 `Done. JSON written to output/...`
3. 对比 `output/10477 035502 1/_pos_data.json` 与修改前的 JSON（如有备份），确认 fuel_lines、regular_lines、tender_lines、fuel_prepay_lines 等结构一致
4. 若有 shift summary 测试数据，再跑一次验证

**预估时间**：5 分钟

---

## 步骤 1.9：（可选）处理 extractors/registry.py

**为什么要做**：避免与 line 的 `REGISTERED` 混淆。`extractors/registry.py` 目前未被使用，可保留作「大 extractor」注册用，或暂时不动。

**怎么做**：

- 方案 A：不改，保持现状
- 方案 B：在 `registry.py` 顶部加注释：`# 用于大 extractor（Transaction/ShiftSummary）的注册，与 line_extractors 的 REGISTERED 分离`

**预估时间**：1 分钟

---

## 时间汇总

| 步骤 | 内容 | 预估时间 |
|------|------|----------|
| 1.1 | base.py 增加 LineExtractor、REGISTERED、register、get_line_extractors | 5 分钟 |
| 1.2 | fuel_extractor 增加 @register 类 | 3 分钟 |
| 1.3 | item_extractor 增加 @register 类 | 3 分钟 |
| 1.4 | tender_extractor 增加 @register 类 | 3 分钟 |
| 1.5 | 新建 fuel_prepay_extractor.py | 5 分钟 |
| 1.6 | 新建 line_extractors/__init__.py | 5 分钟 |
| 1.7 | 修改 transaction_extractor | 8 分钟 |
| 1.8 | 验证 | 5 分钟 |
| 1.9 | registry 注释（可选） | 1 分钟 |
| **合计** | | **约 38–43 分钟** |

加上理解代码、调试、处理意外问题，整体约 **45–60 分钟**。熟练后可压缩到 **30–40 分钟**。
