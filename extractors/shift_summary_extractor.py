from extractors.base_extractor import BaseExtractor, get_text
from extractors.transaction_extractor import extract_single_transaction
from utils.xml_loader import ns


class ShiftSummaryExtractor(BaseExtractor):
    def _process_extraction(self, root):
        journal_header = root.find(".//n:JournalHeader", namespaces=ns)
        transmission_header = root.find(".//n:TransmissionHeader", namespaces=ns)

        result = {
            "BULLOCHSHIFTID": get_text(journal_header, "n:SecondaryReportPeriod", ns),
            "STORELOCATIONID": get_text(transmission_header, "n:StoreLocationID", ns),
            "BEGINDATE": get_text(journal_header, "n:BeginDate", ns),
            "BEGINTIME": get_text(journal_header, "n:BeginTime", ns),
            "ENDDATE": get_text(journal_header, "n:EndDate", ns),
            "ENDTIME": get_text(journal_header, "n:EndTime", ns),
            "PRIMARYREPORTPERIOD": get_text(journal_header, "n:PrimaryReportPeriod", ns),
            "ShiftSummary": self._extract_shift_summary(root),
            "Transactions": [],
        }

        for sale_event in root.findall(".//n:SaleEvent", namespaces=ns):
            tx = extract_single_transaction(sale_event, root)
            result["Transactions"].append(tx)

        return result

    def _extract_shift_summary(self, root):
        """Extract ShiftSummary from OtherEvent with ShiftDetail detailType='close'."""
        other_events = root.findall(".//n:OtherEvent", namespaces=ns)
        for oe in other_events:
            shift_detail = oe.find("n:ShiftDetail", namespaces=ns)
            if shift_detail is not None and shift_detail.get("detailType") == "close":
                stats = oe.find(".//n:Extension/n:Statistics", namespaces=ns)
                ext = oe.find("n:Extension", namespaces=ns)
                return {
                    "CUSTOMERCOUNT": get_text(stats, "n:CustomerCount", ns),
                    "DRAWERMANUALLYOPENED": get_text(stats, "n:DrawerManuallyOpened", ns),
                    "NUMBEROFCASHDRAWEROPENS": get_text(stats, "n:NumberOfCashDrawerOpens", ns),
                    "NUMBEROFUNDOKEYSHIT": get_text(stats, "n:NumberOfUndoKeysHit", ns),
                    "NUMBEROFCLEARKEYSHIT": get_text(stats, "n:NumberOfClearKeysHit", ns),
                    "NUMBEROFVOIDTRANSACTIONS": get_text(stats, "n:NumberOfVoidTransactions", ns),
                    "ENDOFSHIFT": get_text(oe, "n:EventEndTime", ns),
                    "CASHIERID": get_text(oe, "n:CashierID", ns),
                    "ENDOFDAY": get_text(oe, "n:EventEndDate", ns),
                    "SHIFTDETAIL": shift_detail.get("detailType", "close"),
                }
        return {}
