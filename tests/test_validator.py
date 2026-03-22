"""
Unit tests for utils.validator.
运行: pytest tests/test_validator.py -v
"""
import tempfile
from pathlib import Path

import pytest

# 将项目根目录加入 path
import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.validator import validate_payload, validate_pos_data


# ----- 你用临时文件填充，或指向实际 JSON 路径 -----
# 可选：用项目内真实输出作为 fixture
SAMPLE_POS_DATA_DIR = PROJECT_ROOT / "output" / "10477 035502 1"
SAMPLE_POS_DATA = SAMPLE_POS_DATA_DIR / "_pos_data.json"
SAMPLE_PAYLOAD = SAMPLE_POS_DATA_DIR / "_payload.json"


class TestValidatePosData:
    """validate_pos_data 的测试。"""

    def test_valid_pos_data_succeeds(self):
        """【你来填】有效的 _pos_data.json 应返回 (True, '')。"""
        # 方式 A：用临时文件
        # with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        #     f.write('{"Transactions": [{}], "ProcessingStatus": "Success"}')
        #     path = Path(f.name)
        # try:
        #     ok, err = validate_pos_data(path)
        #     assert ok is True
        #     assert err == ""
        # finally:
        #     path.unlink()

        # 方式 B：用项目内已有输出（需先跑过 main.py）
        if not SAMPLE_POS_DATA.exists():
            pytest.skip("需要先运行 main.py 生成 _pos_data.json")
        ok, err = validate_pos_data(SAMPLE_POS_DATA)
        assert ok is True, err
        assert err == ""

    def test_missing_transactions_fails(self):
        """【你来填】没有 Transactions 应返回 (False, error_msg)。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # TODO: 写一个缺少 Transactions 的 JSON
            f.write('{"ProcessingStatus": "Success"}')
            path = Path(f.name)
        try:
            ok, err = validate_pos_data(path)
            assert ok is False
            assert "Transactions" in err or "empty" in err.lower()
        finally:
            path.unlink(missing_ok=True)

    def test_non_success_status_fails(self):
        """【你来填】ProcessingStatus != Success 应返回 (False, error_msg)。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # TODO: 写一个 ProcessingStatus 为 Error 的 JSON
            f.write('{"Transactions": [{}], "ProcessingStatus": "Error"}')
            path = Path(f.name)
        try:
            ok, err = validate_pos_data(path)
            assert ok is False
            assert "Success" in err or "ProcessingStatus" in err
        finally:
            path.unlink(missing_ok=True)

    def test_file_not_found_fails(self):
        """文件不存在应返回 (False, error_msg)。"""
        path = Path("/nonexistent/path/_pos_data.json")
        ok, err = validate_pos_data(path)
        assert ok is False
        assert "not found" in err.lower() or "File" in err


class TestValidatePayload:
    """validate_payload 的测试。"""

    def test_valid_payload_succeeds(self):
        """【你来填】有效的 _payload.json 应返回 (True, '')。"""
        if not SAMPLE_PAYLOAD.exists():
            pytest.skip("需要先运行 main.py 生成 _payload.json")
        ok, err = validate_payload(SAMPLE_PAYLOAD)
        assert ok is True, err
        assert err == ""

    def test_missing_required_field_fails(self):
        """【你来填】缺少 Id / StoreId / TotalAmount 应返回 (False, error_msg)。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # TODO: 写一个缺少 Id 的 payload
            f.write('{"StoreId": "ac4_123", "TotalAmount": 1.0, "SalesLines": [], "TenderLines": []}')
            path = Path(f.name)
        try:
            ok, err = validate_payload(path)
            assert ok is False
            assert "Id" in err or "Missing" in err or "required" in err.lower()
        finally:
            path.unlink(missing_ok=True)

    def test_saleslines_not_list_fails(self):
        """【你来填】SalesLines 不是 list 应返回 (False, error_msg)。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"Id":"x","StoreId":"y","TotalAmount":0,"SalesLines":null,"TenderLines":[]}')
            path = Path(f.name)
        try:
            ok, err = validate_payload(path)
            assert ok is False
            assert "SalesLines" in err
        finally:
            path.unlink(missing_ok=True)
