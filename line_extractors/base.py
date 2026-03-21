from lxml.etree import QName

from utils.xml_loader import ns


def tag_localname(node):
    """Get local name of element, handling namespace."""
    return QName(node).localname if node is not None else None


def get_text(node, tag_name):
    """Get text content of first child matching tag (with namespace)."""
    if node is None:
        return ""
    child = node.find(f"n:{tag_name}", namespaces=ns)
    if child is not None and child.text:
        return child.text.strip()
    return ""


def get_attr(node, tag_name, attr_name):
    """Get attribute value from first child matching tag."""
    if node is None:
        return ""
    child = node.find(f"n:{tag_name}", namespaces=ns)
    if child is not None:
        return child.get(attr_name, "") or ""
    return ""

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

    TAG_LOCALNAME = ""
    RESULT_KEY = ""

    @classmethod
    def matches(cls, localname: str) -> bool:
        return localname == cls.TAG_LOCALNAME

    def extract(self, node, transaction_id: str, sequence_number: str):
        """子类实现，或委托给现有 extract_*_line 函数。"""
        raise NotImplementedError