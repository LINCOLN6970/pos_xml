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