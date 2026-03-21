from abc import ABC, abstractmethod
from datetime import datetime, timezone
import time

from utils.xml_loader import ns


class BaseExtractor(ABC):
    def __init__(self, source_file: str):
        self.source_file = source_file

    def extract(self, root):
        start = time.perf_counter()
        result = self._process_extraction(root)
        duration = time.perf_counter() - start

        result["SourceFile"] = self.source_file
        result["ProcessedAt"] = datetime.now(timezone.utc).isoformat()
        result["ProcessingStatus"] = "Success"
        result["ExtractionDuration"] = duration
        return result

    @abstractmethod
    def _process_extraction(self, root):
        pass


def get_text(node, xpath, namespaces=None):
    """Get text from first node matching xpath."""
    if node is None:
        return ""
    found = node.find(xpath, namespaces=namespaces or ns)
    if found is not None and found.text:
        return found.text.strip()
    return ""
