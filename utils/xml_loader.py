from lxml import etree

NAXML_NS = "http://www.naxml.org/POSBO/Vocabulary/2003-10-16"
ns = {"n": NAXML_NS}


def load_xml(file_path: str):
    tree = etree.parse(file_path)
    return tree.getroot()