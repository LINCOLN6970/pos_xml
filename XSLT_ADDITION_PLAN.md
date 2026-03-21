# 七龙项目添加 XSLT 转换层 - 修改计划

---

## 一、两种方案概览

| 方案 | XSLT 作用 | extractors 改动 | 工作量 |
|------|-----------|-----------------|--------|
| **A：预处理型** | 去除 namespace、统一空白等，输出仍为 NAXML 结构 | 小（可简化 ns 处理） | 小 |
| **B：全转换型** | 复用張經 XSLT，输出 RBOBULLOCH* 格式 | 大（需重写适配新结构） | 大 |

---

## 二、方案 A：预处理型 XSLT（推荐起步）

### 目标
- 添加可选 XSLT 层，做轻量预处理
- 输出仍为 SaleEvent、FuelLine 等 NAXML 结构
- 现有 extractors 基本不动，或只简化 namespace 处理

### 修改清单

#### 1. 新增 `utils/xslt_processor.py`

```python
# 参考 張經 apply_xslt.py，但简化：
# - 单例可选
# - 从 xslt/ 目录加载 .xsl 文件
# - apply(xml_content: bytes) -> etree._ElementTree
# - 无 XSLT 文件时，直接 parse 返回，不报错
```

**职责**：
- 加载 `xslt/*.xsl`（可配置列表）
- `apply(xml_bytes) -> tree`
- 无 XSLT 时：`etree.parse(BytesIO(xml_bytes))` 直接返回

#### 2. 新增 `xslt/` 目录

- 放置 `StripNamespace.xsl` 或类似预处理 XSLT（可选）
- 若无 XSLT：processor 检测到空目录则跳过转换

#### 3. 修改 `utils/xml_loader.py`

```python
# 新增函数
def load_xml_with_xslt(file_path: str, use_xslt: bool = False) -> etree._Element:
    with open(file_path, 'rb') as f:
        content = f.read()
    if use_xslt:
        tree = xslt_processor.apply(content)
    else:
        tree = etree.parse(BytesIO(content))
    return tree.getroot()
```

或保持 `load_xml` 不变，在调用方决定是否先走 XSLT。

#### 4. 修改 `main.py`

```python
# 新增参数
parser.add_argument("--xslt", action="store_true", help="Apply XSLT before extraction")

# process_file 中
def process_file(input_file, output_file=None, use_xslt=False):
    if use_xslt:
        with open(input_file, 'rb') as f:
            content = f.read()
        tree = xslt_processor.apply(content)
        root = tree.getroot()
    else:
        root = load_xml(input_file)
    # 后续不变
```

#### 5. extractors

- **方案 A 下**：若 XSLT 只做 strip namespace，输出无 ns，extractors 需支持「无 ns」的 find
- 可选：在 `get_text`、`find` 中同时尝试带 ns 和不带 ns 的查找，兼容两种输入

---

## 三、方案 B：全转换型（复用張經 XSLT）

### 目标
- 复用 張經 的 Transform001.xsl、Transform002.xsl
- 输出 RBOBULLOCHSHIFTENTITY、RBOBULLOCHTRANSACTIONENTITY、RBOBULLOCHTRANSACTIONLINEENTITY
- extractors 全部改为适配新结构

### 修改清单

#### 1. 新增 `utils/xslt_processor.py`

- 与 張經 `apply_xslt.py` 逻辑一致
- 加载 `xslt/Transform001.xsl`、`xslt/Transform002.xsl`
- `apply(xml_content: bytes) -> etree._ElementTree`

#### 2. 复制 XSLT 文件

```
pos_xml_qilong/
  xslt/
    Transform001.xsl   # 从 張經 复制
    Transform002.xsl   # 从 張經 复制
```

#### 3. 修改数据流

```
当前：文件 → load_xml → root → extractors
改为：文件 → read bytes → xslt_processor.apply → root → extractors（新结构）
```

#### 4. 重写 extractors 以适配 RBOBULLOCH* 结构

| 文件 | 改动 |
|------|------|
| `transaction_extractor.py` | 用 `.//RBOBULLOCHTRANSACTIONENTITY` 替代 `.//n:SaleEvent`；用 `entity.findtext("TAG")` 替代 `get_text(node, "n:TAG", ns)` |
| `shift_summary_extractor.py` | 用 `.//RBOBULLOCHSHIFTENTITY`；从 shift entity 取 BEGINDATE 等 |
| line extractors | 适配 `RBOBULLOCHTRANSACTIONLINEENTITY`，用 `LINETYPE` 区分 FuelLine/ItemLine |

#### 5. 可选：引入 張經 的声明式 line extractor

- 用 `FIELDS`、`COLL`、`@register` 模式
- 需新增 `line_extractors/header.py`、`shift_summary.py` 等
- 或保持当前函数式，只改 XPath 和标签名

#### 6. 移除或简化 namespace

- 转换后 XML 无 namespace
- 删除 `utils/xml_loader.py` 中的 `ns`、`NAXML_NS`
- 所有 `find("n:XXX", namespaces=ns)` 改为 `find("XXX")` 或 `findtext("XXX")`

---

## 四、实施顺序建议

### 若选方案 A（预处理型）

1. 新增 `utils/xslt_processor.py`（支持空 XSLT 列表时直通）
2. 新增 `xslt/` 目录（可先为空）
3. 修改 `main.py` 增加 `--xslt` 参数
4. 修改 `process_file`，在 `use_xslt=True` 时走 XSLT
5. 视需要编写简单预处理 XSLT（如 strip namespace）

### 若选方案 B（全转换型）

1. 新增 `utils/xslt_processor.py`（参考 張經）
2. 复制 `Transform001.xsl`、`Transform002.xsl` 到 `xslt/`
3. 修改 `main.py`、`process_file`，统一走 XSLT
4. 重写 `transaction_extractor.py` 适配 RBOBULLOCHTRANSACTIONENTITY
5. 重写 `shift_summary_extractor.py` 适配 RBOBULLOCHSHIFTENTITY
6. 重写各 line extractor 适配 RBOBULLOCHTRANSACTIONLINEENTITY
7. 移除 namespace 相关代码

---

## 五、需要先确认的点

1. **XSLT 目标**：预处理（方案 A）还是全转换到 張經 格式（方案 B）？
2. **XSLT 是否可选**：是否保留「不走 XSLT、直接解析原始 NAXML」的模式？
3. **張經 XSLT 兼容性**：Transform001/002 是否与当前 NAXML 样本完全兼容，需实测验证。

---

## 六、方案 A 最小实现（仅加框架）

若先只加 XSLT 框架、不改变现有提取逻辑：

1. 新增 `utils/xslt_processor.py`：有 XSLT 就转换，没有就直通
2. 修改 `main.py`：增加 `--xslt`，`process_file` 支持 `use_xslt`
3. 暂不添加实际 XSLT 文件，保持行为与现在一致
4. 后续再按需添加预处理或全转换 XSLT
