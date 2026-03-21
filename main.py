import argparse
import os
import re


from utils.file_writer import write_json
from extractors.transaction_extractor import TransactionExtractor
from extractors.shift_summary_extractor import ShiftSummaryExtractor
from utils import xslt_processor



def parse_output_id(filename):
    """Extract id from filename: naxml-posjournal 10477 035502 1.xml -> 10477 035502 1"""
    basename = os.path.basename(filename)
    match = re.match(r"naxml-posjournal\s+(.+)\.xml$", basename, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return basename.replace(".xml", "")


def is_shift_summary(filename):
    """Shift: naxml-posjournal xxxx.xml (2 segments). Transaction: naxml-posjournal xxxx xxx x.xml (4 segments)."""
    basename = os.path.basename(filename)
    match = re.match(r"naxml-posjournal\s+(.+)\.xml$", basename, re.IGNORECASE)
    if not match:
        return False
    segments = match.group(1).split()
    return len(segments) == 2


def choose_extractor(source_file):
    if is_shift_summary(source_file):
        return ShiftSummaryExtractor(source_file)
    return TransactionExtractor(source_file)


def _resolve_default_input_path():
    candidate_paths = [
        os.path.join("test_data", "ERROR", "naxml-posjournal 10477 035502 1.xml"),
        os.path.join("test_data", "error", "naxml-posjournal 10477 035502 1.xml"),
        os.path.join("TaxData", "ERROR", "naxml-posjournal 10477 035502 1.xml"),
        os.path.join("TaxData", "error", "naxml-posjournal 10477 035502 1.xml"),
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            return p
    return candidate_paths[0]


def process_file(input_file, output_file=None):
    with open(input_file, "rb") as f:
        content = f.read()
    root = xslt_processor.apply(content)
    extractor = choose_extractor(input_file)

    if output_file is None:
        output_id = parse_output_id(input_file)
        output_file = os.path.join("output", output_id, "_pos_data.json")

    result = extractor.extract(root)
    write_json(result, output_file)
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Parse NA XML posjournal into JSON.")
    parser.add_argument(
        "-i",
        "--input",
        default=_resolve_default_input_path(),
        help="Input XML path (transaction or shift summary).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output JSON path (default: output/<id>/_pos_data.json).",
    )
    parser.add_argument(
        "-d",
        "--directory",
        default=None,
        help="Process all XML files in directory.",
    )
    args = parser.parse_args()

    if args.directory:
        for filename in sorted(os.listdir(args.directory)):
            if filename.lower().endswith(".xml"):
                input_path = os.path.join(args.directory, filename)
                out_path = process_file(input_path)
                print("Done:", input_path, "->", out_path)
    else:
        out_path = process_file(args.input, args.output)
        print("Done. JSON written to", out_path)


if __name__ == "__main__":
    main()
