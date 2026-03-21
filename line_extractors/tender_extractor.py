from line_extractors.base import get_text, LineExtractor, register
from utils.xml_loader import ns


def extract_tender_line(tender_info_node, transaction_id, sequence_number):
    """Extract tender line data from TenderInfo element."""
    tender = tender_info_node.find("n:Tender", namespaces=ns)
    tender_code = ""
    tender_subcode = ""
    if tender is not None:
        tender_code = get_text(tender, "TenderCode")
        tender_subcode = get_text(tender, "TenderSubCode")

    amount_elem = tender_info_node.find("n:TenderAmount", namespaces=ns)
    amount = amount_elem.text.strip() if amount_elem is not None and amount_elem.text else ""

    return {
        "TENDERAMOUNT": amount,
        "TENDERCODE": tender_code,
        "TENDERSUBCODE": tender_subcode,
        "TRANSACTIONID": transaction_id,
        "TRANSACTIONLINESEQUENCENUMBER": sequence_number,
    }

@register
class TenderLineExtractor(LineExtractor):
    TAG_LOCALNAME = "TenderInfo"
    RESULT_KEY = "tender_lines"

    def extract(self, node, transaction_id: str, sequence_number: str):
        return extract_tender_line(node, transaction_id, sequence_number)