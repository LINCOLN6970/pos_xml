# XSLT 标准化层 - 实施步骤（你来操作，我来检查）

**原则**：所有 input 必须先经 XSLT，再进入 extractors。输出结构不变。

---

## 步骤 1：创建 `xslt/` 目录

**操作**：在项目根目录下新建文件夹 `xslt`

**原因**：集中存放 XSLT 文件，便于维护和加载。

---

## 步骤 2：创建 `xslt/Normalize001.xsl`

**操作**：在 `xslt/` 下新建 `Normalize001.xsl`，内容如下（身份转换，保持结构不变）：

```xml
<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>
</xsl:stylesheet>
```

**原因**：先用身份转换打通流程，保证行为与当前一致。之后可替换为真正的标准化逻辑。

---

## 步骤 3：创建 `utils/xslt_processor.py`

**操作**：新建文件，内容如下：

```python
from io import BytesIO
from pathlib import Path
from lxml import etree

_XSLT_DIR = Path(__file__).resolve().parent.parent / "xslt"
_TRANSFORMS = []
_LOADED = False


def _load_transforms():
    global _LOADED, _TRANSFORMS
    if _LOADED:
        return
    for fpath in sorted(Path(_XSLT_DIR).glob("*.xsl")):
        root = etree.XML(fpath.read_bytes())
        _TRANSFORMS.append(etree.XSLT(root))
    _LOADED = True


def apply(xml_content: bytes):
    """Apply XSLT to XML bytes. Returns root element."""
    _load_transforms()
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(BytesIO(xml_content), parser)
    for transform in _TRANSFORMS:
        tree = transform(tree)
    return tree.getroot()
```

**原因**：统一负责 XSLT 加载和执行，入口为 `apply(bytes)`，返回 `root`，供 extractors 使用。

---

## 步骤 4：修改 `main.py` 的 `process_file`

**操作**：把 `process_file` 里的 `root = load_xml(input_file)` 改成：

```python
with open(input_file, "rb") as f:
    content = f.read()
root = xslt_processor.apply(content)
```

并在文件顶部添加：

```python
from utils import xslt_processor
```

**原因**：所有 input 先读成 bytes，再经 XSLT 转换，再交给 extractors。不再直接调用 `load_xml`。

---

## 步骤 5：验证

**操作**：在项目根目录执行：

```bash
python3 main.py -i "test_data/error/naxml-posjournal 10477 035502 1.xml"
```

**预期**：能正常生成 `output/10477 035502 1/_pos_data.json`，内容与之前一致。

**原因**：身份转换不改变 XML，用于确认流程正确。

---

## 步骤 6（可选）：替换为真正的标准化 XSLT

**操作**：在确认步骤 5 通过后，按实际需求修改 `Normalize001.xsl`，实现命名空间、空白、结构等标准化。

**原因**：先保证流程正确，再逐步增强 XSLT 逻辑。

---

## 总结

| 步骤 | 动作 | 目的 |
|------|------|------|
| 1 | 建 `xslt/` | 存放 XSLT |
| 2 | 建 `Normalize001.xsl` | 身份转换，打通流程 |
| 3 | 建 `xslt_processor.py` | 加载并执行 XSLT |
| 4 | 改 `process_file` | 所有 input 先走 XSLT |
| 5 | 跑测试 | 验证流程 |
| 6 | 按需改 XSLT | 实现真实标准化 |

---

## 完成后告诉我

你完成上述步骤后，告诉我，我会帮你检查代码和运行结果。
