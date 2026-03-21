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
        raw = fpath.read_bytes().lstrip()
        root = etree.XML(raw)
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