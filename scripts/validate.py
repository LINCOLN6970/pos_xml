#!/usr/bin/env python3
"""CI 验证：运行 main 并检查输出 JSON 存在且有效。"""
import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_XML = "test_data/error/naxml-posjournal 10477 035502 1.xml"
EXPECTED_OUTPUT = PROJECT_ROOT / "output" / "10477 035502 1" / "_pos_data.json"


def main():
    result = subprocess.run(
        [sys.executable, "main.py", "-i", INPUT_XML],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("main.py failed:", result.stderr or result.stdout)
        return 1

    if not EXPECTED_OUTPUT.exists():
        print(f"Output not found: {EXPECTED_OUTPUT}")
        return 1

    try:
        data = json.loads(EXPECTED_OUTPUT.read_text())
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return 1

    if not data.get("Transactions"):
        print("Transactions is empty or missing")
        return 1

    if data.get("ProcessingStatus") != "Success":
        print(f"ProcessingStatus is not Success: {data.get('ProcessingStatus')}")
        return 1

    print("Validation OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
