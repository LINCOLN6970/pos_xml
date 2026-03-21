from line_extractors.base import LineExtractor, register, get_text


def extract_fuel_prepay_line(node, transaction_id: str, sequence_number: str):
    """Stub for FuelPrepayLine - returns minimal structure."""
    return {
        "TRANSACTIONID": transaction_id,
        "TRANSACTIONLINESEQUENCENUMBER": sequence_number,
        "SALESAMOUNT": get_text(node, "SalesAmount"),
    }


@register
class FuelPrepayLineExtractor(LineExtractor):
    TAG_LOCALNAME = "FuelPrepayLine"
    RESULT_KEY = "fuel_prepay_lines"

    def extract(self, node, transaction_id: str, sequence_number: str):
        return extract_fuel_prepay_line(node, transaction_id, sequence_number)