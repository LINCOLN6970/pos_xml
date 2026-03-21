# validate.py 编写指南

按步骤自己编写，每步说明「写什么」和「为什么」。

---

## 步骤 1：写 shebang 和 docstring

**写什么**：
```python
#!/usr/bin/env python3
"""CI 验证：运行 main 并检查输出 JSON 存在且有效。"""
```

**为什么**：`#!/usr/bin/env python3` 让脚本在 Unix 下可直接执行；docstring 说明脚本用途，便于他人理解。

---

## 步骤 2：导入模块

**写什么**：
```python
import json
import subprocess
import sys
from pathlib import Path
```

**为什么**：
- `json`：解析输出 JSON
- `subprocess`：调用 main.py（不直接 import main，避免 argparse 冲突）
- `sys`：用 `sys.executable` 找当前 Python 解释器，用 `sys.exit()` 返回退出码
- `Path`：统一、跨平台处理路径

---

## 步骤 3：定义常量

**写什么**：
```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_XML = "test_data/error/naxml-posjournal 10477 035502 1.xml"
EXPECTED_OUTPUT = PROJECT_ROOT / "output" / "10477 035502 1" / "_pos_data.json"
```

**为什么**：
- `PROJECT_ROOT`：`__file__` 是 validate.py 路径，`.parent.parent` 得到项目根，保证无论从哪里运行都能找到根目录
- `INPUT_XML`：main.py 的测试输入
- `EXPECTED_OUTPUT`：main 处理后生成的 JSON 路径

---

## 步骤 4：运行 main.py

**写什么**：
```python
result = subprocess.run(
    [sys.executable, "main.py", "-i", INPUT_XML],
    cwd=PROJECT_ROOT,
    capture_output=True,
    text=True,
)
```

**为什么**：
- `sys.executable`：用当前激活的 Python（含 venv）
- `cwd=PROJECT_ROOT`：在项目根执行，main.py 才能找到 test_data、utils 等
- `capture_output=True`：捕获 stdout/stderr，失败时可打印
- `text=True`：输出为字符串而非 bytes

---

## 步骤 5：判断 main 是否成功

**写什么**：
```python
if result.returncode != 0:
    print("main.py failed:", result.stderr or result.stdout)
    return 1
```

**为什么**：`returncode != 0` 表示 main 出错；打印 stderr（或 stdout）便于 CI 排查；返回 1 表示验证失败。

---

## 步骤 6：检查输出文件是否存在

**写什么**：
```python
if not EXPECTED_OUTPUT.exists():
    print(f"Output not found: {EXPECTED_OUTPUT}")
    return 1
```

**为什么**：main 可能异常退出但 returncode 为 0，或输出路径不对，需要显式检查文件存在。

---

## 步骤 7：解析 JSON 并检查内容

**写什么**：
```python
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
```

**为什么**：
- `try/except`：捕获 JSON 语法错误
- `data.get("Transactions")`：必须至少有一笔交易
- `ProcessingStatus == "Success"`：确认 main 标记为成功

---

## 步骤 8：成功时输出并退出

**写什么**：
```python
print("Validation OK")
return 0
```

**为什么**：0 表示成功；`print` 方便在 CI 日志中看到通过信息。

---

## 步骤 9：定义 main 并作为入口

**写什么**：
```python
def main():
    # 把步骤 4～8 的代码放在这里
    ...

if __name__ == "__main__":
    sys.exit(main())
```

**为什么**：`main()` 集中逻辑；`if __name__ == "__main__"` 保证直接运行脚本时才执行；`sys.exit(main())` 把返回值作为进程退出码，CI 据此判断成功或失败。
