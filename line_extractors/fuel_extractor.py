from line_extractors.base import get_text, get_attr, LineExtractor, register
from utils.xml_loader import ns


def extract_fuel_line(fuel_line_node, transaction_id, sequence_number):
    """Extract fuel line data from FuelLine element."""
    entry_method = get_attr(fuel_line_node, "EntryMethod", "method") or "other"
    return {
        "DESCRIPTION": get_text(fuel_line_node, "Description"),
        "FUELGRADEID": get_text(fuel_line_node, "FuelGradeID"),
        "FUELPOSITIONID": get_text(fuel_line_node, "FuelPositionID"),
        "SERVICELEVELCODE": get_text(fuel_line_node, "ServiceLevelCode"),
        "REGULARSELLPRICE": get_text(fuel_line_node, "RegularSellPrice"),
        "ACTUALSALESPRICE": get_text(fuel_line_node, "ActualSalesPrice"),
        "SALESAMOUNT": get_text(fuel_line_node, "SalesAmount"),
        "SALESQUANTITY": get_text(fuel_line_node, "SalesQuantity"),
        "TRANSACTIONID": transaction_id,
        "TRANSACTIONLINESEQUENCENUMBER": sequence_number,
        "ENTRYMETHOD": entry_method,
        "discount_lines": _extract_fuel_discount_lines(fuel_line_node),
    }


def _extract_fuel_discount_lines(fuel_line_node):
    """Extract promotion/discount from FuelLine if present."""
    promo = fuel_line_node.find("n:Promotion", namespaces=ns)
    if promo is None:
        return []
    return [{
        "PromotionID": get_text(promo, "PromotionID"),
        "PromotionReason": get_text(promo, "PromotionReason"),
        "PromotionAmount": get_text(promo, "PromotionAmount"),
    }]

@register
class FuelLineExtractor(LineExtractor):
    TAG_LOCALNAME = "FuelLine"
    RESULT_KEY = "fuel_lines"

    def extract(self, node, transaction_id, sequence_number):
        return extract_fuel_line(node, transaction_id, sequence_number)


