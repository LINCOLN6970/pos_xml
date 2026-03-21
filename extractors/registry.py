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