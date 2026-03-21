from lxml.etree import QName

from extractors.base_extractor import BaseExtractor, get_text
from line_extractors.base import tag_localname
from line_extractors import get_line_extractors
from utils.xml_loader import ns


def extract_single_transaction(sale_event, root):
    """Extract one transaction from a SaleEvent node. Shared by TransactionExtractor and ShiftSummaryExtractor."""
    return _TransactionExtractorLogic()._extract(sale_event, root)


class _TransactionExtractorLogic:
    """Internal logic for extracting a single transaction."""

    def _extract(self, sale_event, root):
        """Extract one transaction from a SaleEvent node."""
        tx_id = get_text(sale_event, ".//n:TransactionID", ns)
        journal_header = root.find(".//n:JournalHeader", namespaces=ns)
        transmission_header = root.find(".//n:TransmissionHeader", namespaces=ns)

        bulloch_shift_id = get_text(journal_header, "n:SecondaryReportPeriod", ns)
        store_location_id = get_text(transmission_header, "n:StoreLocationID", ns)
        primary_report_period = get_text(journal_header, "n:PrimaryReportPeriod", ns)

        tx_summary = sale_event.find("n:TransactionSummary", namespaces=ns)

        result = {
            "BULLOCHSHIFTID": bulloch_shift_id,
            "STORELOCATIONID": store_location_id,
            "TRANSACTIONID": tx_id,
            "BUSINESSDATE": get_text(sale_event, "n:BusinessDate", ns),
            "RECEIPTDATE": get_text(sale_event, "n:ReceiptDate", ns),
            "RECEIPTTIME": get_text(sale_event, "n:ReceiptTime", ns),
            "REGISTERID": get_text(sale_event, "n:RegisterID", ns),
            "TRANSACTIONTOTALGRANDAMOUNT": get_text(tx_summary, "n:TransactionTotalGrandAmount", ns),
            "TRANSACTIONTOTALGROSSAMOUNT": get_text(tx_summary, "n:TransactionTotalGrossAmount", ns),
            "TRANSACTIONTOTALNETAMOUNT": get_text(tx_summary, "n:TransactionTotalNetAmount", ns),
            "TRANSACTIONTOTALTAXNETAMOUNT": get_text(tx_summary, "n:TransactionTotalTaxNetAmount", ns),
            "EVENTTYPE": "SalesEvent",
            "LPELOYALTYTRANSACTIONID": get_text(sale_event, ".//n:Extension/n:LoyaltyTransactionID", ns),
            "MOBILAINVOICENUMBER": get_text(sale_event, ".//n:Extension/n:MobilaInvoiceNumber", ns),
            "CASHIERID": get_text(sale_event, "n:CashierID", ns),
            "regular_lines": [],
            "tender_lines": [],
            "fuel_lines": [],
            "fuel_prepay_lines": [],
            "payout_lines": [],
            "drive_off_lines": [],
            "pump_test_lines": [],
            "safe_drop_lines": [],
            "deal_lines": [],
            "PRIMARYREPORTPERIOD": primary_report_period,
        }

        result["deal_lines"] = _extract_deal_lines(sale_event, root, tx_id, bulloch_shift_id)

        detail_group = sale_event.find("n:TransactionDetailGroup", namespaces=ns)
        if detail_group is None:
            return result

        for tx_line in detail_group.findall("n:TransactionLine", namespaces=ns):
            seq_elem = tx_line.find("n:TransactionLineSequenceNumber", namespaces=ns)
            seq_num = seq_elem.text.strip() if seq_elem is not None and seq_elem.text else ""
            for child in tx_line:
                localname = tag_localname(child)
                for extractor in get_line_extractors():
                    if extractor.matches(localname):
                        result[extractor.RESULT_KEY].append(
                            extractor.extract(child, tx_id, seq_num)
                        )
                        break
        return result


def _extract_deal_lines(sale_event, root, transaction_id, bulloch_shift_id):
    """Extract deal_lines from Extension/DealGroups."""
    result = []
    ext = sale_event.find("n:Extension", namespaces=ns)
    if ext is None:
        return result
    deal_groups = ext.find("n:DealGroups", namespaces=ns)
    if deal_groups is None:
        return result
    report_seq = get_text(root.find(".//n:JournalHeader", namespaces=ns), "n:ReportSequenceNumber", ns) or bulloch_shift_id
    for dg in deal_groups.findall("n:DealGroup", namespaces=ns) or []:
        promo_id = get_text(dg, "n:PromotionIDFromNACS", ns)
        times = get_text(dg, "n:TimesTriggered", ns)
        result.append({
            "BULLOCHSHIFTID": bulloch_shift_id,
            "DISCOUNTINFOID": promo_id,
            "REPORTSEQUENCENUMBER": report_seq,
            "TIMESTRIGGERED": times,
            "TRANSACTIONID": transaction_id,
        })
    return result


class TransactionExtractor(BaseExtractor):
    def _process_extraction(self, root):
        sale_event = root.find(".//n:SaleEvent", namespaces=ns)
        if sale_event is None:
            return {"Transactions": []}
        tx = extract_single_transaction(sale_event, root)
        return {"Transactions": [tx]}
