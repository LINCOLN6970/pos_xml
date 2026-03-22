#!/usr/bin/env python3
"""
CI validation: run main.py and verify output JSON files exist and are valid.
支持命令行参数指定输入 XML 和输出目录。
"""
import argparse
import subprocess
import sys
from pathlib import Path

# Ensure project root is on path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.validator import EXIT_FAIL, EXIT_OK, validate_payload, validate_pos_data

# 默认测试配置（无参数时使用）
DEFAULT_INPUT_XML = "test_data/error/naxml-posjournal 10477 035502 1.xml"
DEFAULT_OUTPUT_ID = "10477 035502 1"  # 对应 output/<id>/


def parse_output_id(filename: str) -> str:
    """从文件名解析输出 id，如 naxml-posjournal 10477 035502 1.xml -> 10477 035502 1"""
    import re
    basename = Path(filename).name
    match = re.match(r"naxml-posjournal\s+(.+)\.xml$", basename, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return basename.replace(".xml", "")


def run_main(input_xml: Path, project_root: Path) -> int:
    """Run main.py with given input. Returns exit code (0 = success)."""
    result = subprocess.run(
        [sys.executable, "main.py", "-i", str(input_xml)],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("main.py failed:", result.stderr or result.stdout)
        return EXIT_FAIL
    return EXIT_OK


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run main.py and validate output JSON (pos_data + payload).",
    )
    parser.add_argument(
        "-i", "--input",
        default=PROJECT_ROOT / DEFAULT_INPUT_XML,
        type=Path,
        help=f"Input XML path (default: {DEFAULT_INPUT_XML})",
    )
    parser.add_argument(
        "-o", "--output-id",
        default=None,
        help="Output id (e.g. '10477 035502 1'). 若不指定，则从 -i 文件名解析",
    )
    args = parser.parse_args()

    input_xml = args.input if args.input.is_absolute() else PROJECT_ROOT / args.input
    if not input_xml.exists():
        print(f"Input XML not found: {input_xml}")
        return EXIT_FAIL

    # 输出目录：output/<output_id>/
    output_id = args.output_id or parse_output_id(input_xml.name)
    output_dir = PROJECT_ROOT / "output" / output_id
    pos_data_path = output_dir / "_pos_data.json"
    payload_path = output_dir / "_payload.json"

    if run_main(input_xml, PROJECT_ROOT) != EXIT_OK:
        return EXIT_FAIL

    ok, err = validate_pos_data(pos_data_path)
    if not ok:
        print(f"_pos_data.json: {err}")
        return EXIT_FAIL

    ok, err = validate_payload(payload_path)
    if not ok:
        print(f"_payload.json: {err}")
        return EXIT_FAIL

    print("Validation OK")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
