from line_extractors.base import get_text, get_attr, LineExtractor, register
from utils.xml_loader import ns


def extract_item_line(item_line_node, transaction_id, sequence_number):
    """Extract item line data from ItemLine element."""
    item_code = item_line_node.find("n:ItemCode", namespaces=ns)
    pos_code = ""
    pos_format = ""
    pos_modifier = ""
    inventory_item_id = ""
    if item_code is not None:
        pos_code = get_text(item_code, "POSCode")
        inv = item_code.find("n:InventoryItemID", namespaces=ns)
        if inv is not None and inv.text:
            inventory_item_id = inv.text.strip()
        pos_format_elem = item_code.find("n:POSCodeFormat", namespaces=ns)
        if pos_format_elem is not None:
            pos_format = pos_format_elem.get("format", "") or ""
        pos_mod_elem = item_code.find("n:POSCodeModifier", namespaces=ns)
        if pos_mod_elem is not None and pos_mod_elem.text:
            pos_modifier = pos_mod_elem.text.strip()
        elif pos_mod_elem is not None:
            pos_modifier = pos_mod_elem.get("name", "") or "0"

    entry_method = get_attr(item_line_node, "EntryMethod", "method") or ""

    return {
        "DESCRIPTION": get_text(item_line_node, "Description"),
        "INVENTORYITEMID": inventory_item_id,
        "SALESAMOUNT": get_text(item_line_node, "SalesAmount"),
        "REGULARSELLPRICE": get_text(item_line_node, "RegularSellPrice"),
        "ACTUALSALESPRICE": get_text(item_line_node, "ActualSalesPrice"),
        "SALESQUANTITY": get_text(item_line_node, "SalesQuantity"),
        "TRANSACTIONID": transaction_id,
        "TRANSACTIONLINESEQUENCENUMBER": sequence_number,
        "ENTRYMETHOD": entry_method,
        "POSCODE": pos_code,
        "POSCODEFORMAT": pos_format,
        "POSCODEMODIFIER": pos_modifier,
        "ITEMTYPECODE": get_text(item_line_node, "ItemTypeCode"),
        "ITEMTYPESUBCODE": get_text(item_line_node, "ItemTypeSubCode"),
        "MERCHANDISECODE": get_text(item_line_node, "MerchandiseCode"),
        "charge_lines": _extract_charge_lines(item_line_node),
        "discount_lines": _extract_discount_lines(item_line_node),
    }


def _extract_charge_lines(item_line_node):
    """Extract ItemTax as charge_lines."""
    result = []
    for item_tax in item_line_node.findall("n:ItemTax", namespaces=ns) or []:
        tax_id = item_tax.find("n:TaxLevelID", namespaces=ns)
        amount = item_tax.find("n:TaxCollectedAmount", namespaces=ns)
        result.append({
            "TAXLEVELID": tax_id.text.strip() if tax_id is not None and tax_id.text else "",
            "TAXCOLLECTEDAMOUNT": amount.text.strip() if amount is not None and amount.text else "",
        })
    return result


def _extract_discount_lines(item_line_node):
    """Extract Promotion as discount_lines."""
    promo = item_line_node.find("n:Promotion", namespaces=ns)
    if promo is None:
        return []
    return [{
        "PromotionID": get_text(promo, "PromotionID"),
        "PromotionReason": get_text(promo, "PromotionReason"),
        "PromotionAmount": get_text(promo, "PromotionAmount"),
    }]


@register
class ItemLineExtractor(LineExtractor):
    TAG_LOCALNAME = "ItemLine"
    RESULT_KEY = "regular_lines"

    def extract(self, node, transaction_id: str, sequence_number: str):
        return extract_item_line(node, transaction_id, sequence_number)