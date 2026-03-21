# pos_xml_qilong：自动化与敏捷协作 2 天实施计划

---

## 一、目标

- **自动化**：建立 GitHub Actions 流水线，实现提交即验证/部署
- **敏捷协作**：用 GitHub Projects / Issues（或 ADO/Jira）管理任务，形成 Epic → Story → Task 结构

---

## 二、Day 1：自动化（CI/CD）

### 2.1 前置条件

- [ ] 项目已初始化为 Git 仓库（若无：`git init`）
- [ ] 已推送到 GitHub（若未：创建 repo 并 `git remote add`）
- [ ] 本地 Python 环境可正常运行 `python3 main.py -i "test_data/error/naxml-posjournal 10477 035502 1.xml"`

### 2.2 任务清单

| 序号 | 任务 | 产出 | 预估时间 |
|------|------|------|----------|
| 1.1 | 新增 `scripts/validate.py`：运行 main 并检查输出 JSON 存在且非空 | 可被 CI 调用的验证脚本 | 30 分钟 |
| 1.2 | 新建 `.github/workflows/ci.yml`：`on: push` 触发，执行 `pip install -r requirements.txt`、`python scripts/validate.py` | CI 流水线 | 30 分钟 |
| 1.3 | 添加 `ruff` 或 `flake8` 到 `requirements-dev.txt`（可选），在 workflow 中加入 lint 步骤 | 代码质量检查 | 20 分钟 |
| 1.4 | 提交并推送，观察 Actions 是否通过 | 流水线验证 | 10 分钟 |

### 2.3 关键文件示例

**scripts/validate.py**（示意）：
```python
#!/usr/bin/env python3
"""CI 验证：运行 main 并检查输出存在且有效。"""
import json
import subprocess
import sys
from pathlib import Path

def main():
    subprocess.run(
        [sys.executable, "main.py", "-i", "test_data/error/naxml-posjournal 10477 035502 1.xml"],
        check=True,
        cwd=Path(__file__).resolve().parent.parent,
    )
    out = Path("output/10477 035502 1/_pos_data.json")
    if not out.exists():
        sys.exit(1)
    data = json.loads(out.read_text())
    if not data.get("Transactions"):
        sys.exit(1)
    print("Validation OK")
    return 0

if __name__ == "__main__":
    sys.exit(main() or 0)
```

**.github/workflows/ci.yml**（示意）：
```yaml
name: CI
on:
  push:
    branches: [main, develop]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: python scripts/validate.py
```

### 2.4 Day 1 完成标准

- [ ] `git push` 后 GitHub Actions 自动运行
- [ ] 流水线通过（绿色 ✓）
- [ ] 任一 step 失败时能看到明确错误日志

---

## 三、Day 2：敏捷协作（项目管理）

### 3.1 工具选择

| 选项 | 适用场景 |
|------|----------|
| **GitHub Projects + Issues** | 项目在 GitHub，无需额外账号，可与 CI 关联 |
| **Azure DevOps (ADO)** | 公司已有 Azure 生态，需有 ADO 账号 |
| **Jira** | 公司已有 Jira，需有 Jira 账号 |

**建议**：若暂无 ADO/Jira，先用 **GitHub Projects + Issues** 建立流程，后续可迁移。

### 3.2 任务清单

| 序号 | 任务 | 产出 | 预估时间 |
|------|------|------|----------|
| 2.1 | 在 GitHub 创建 Project（如「pos_xml_qilong」） | 项目看板 | 15 分钟 |
| 2.2 | 建 Epic：如「POS XML 提取与 payload 转换」 | Epic 层级 | 10 分钟 |
| 2.3 | 拆 Story：如「注册机制」「payload 转换」「CI 流水线」 | User Story | 30 分钟 |
| 2.4 | 拆 Task：每个 Story 下 2–5 个可执行 Task，带 Acceptance Criteria | Task 清单 | 45 分钟 |
| 2.5 | 将现有/计划工作录入 Issues，关联到 Project | 可追踪 backlog | 30 分钟 |
| 2.6 | 编写 `PROJECT_BACKLOG.md`：记录 Epic/Story/Task 结构与验收标准 | 文档 | 30 分钟 |

### 3.3 层级示例

```
Epic: POS XML 提取与下游集成
├── Story 1: 注册机制改造 ✅（已完成）
│   ├── Task: base.py 增加 REGISTERED、register
│   ├── Task: 各 line extractor 加 @register
│   └── Task: transaction_extractor 改用 get_line_extractors
├── Story 2: CI 流水线
│   ├── Task: 新建 scripts/validate.py
│   ├── Task: 新建 .github/workflows/ci.yml
│   └── Task: 验证 push 触发通过
├── Story 3: _pos_data → _payload 转换（计划中）
│   ├── Task: 设计 pos_to_payload 字段映射
│   ├── Task: 实现 utils/payload_builder.py
│   └── Task: main 输出 _payload.json
└── Story 4: Azure 部署（可选）
    └── Task: Function App 配置与 Terraform
```

### 3.4 Day 2 完成标准

- [ ] Project 已创建，至少 1 个 Epic、3+ Story、若干 Task
- [ ] 每个 Task 有简洁的 Acceptance Criteria
- [ ] `PROJECT_BACKLOG.md` 已编写，可作团队参考

---

## 四、两天时间分配建议

| 时段 | Day 1 | Day 2 |
|------|-------|-------|
| 上午 | 1.1 验证脚本 + 1.2 CI workflow | 2.1–2.3 Project + Epic + Story |
| 下午 | 1.3 可选 lint + 1.4 验证、排查 | 2.4–2.6 Task 拆分 + 录入 + 文档 |

---

## 五、风险与应对

| 风险 | 应对 |
|------|------|
| 无 GitHub 或无法 push | 先本地完成脚本和 workflow 文件，待有权限后推送 |
| 无 ADO/Jira | 使用 GitHub Projects + Issues 替代 |
| CI 因路径/环境失败 | 在 workflow 中加 `working-directory` 或调整 `scripts/validate.py` 的路径逻辑 |

---

## 六、产出物汇总

| 产出 | 路径 |
|------|------|
| 验证脚本 | `scripts/validate.py` |
| CI 配置 | `.github/workflows/ci.yml` |
| 可选依赖 | `requirements-dev.txt` |
| 项目 backlog | `PROJECT_BACKLOG.md` |
| 本计划 | `AUTOMATION_AGILE_2DAY_PLAN.md` |
