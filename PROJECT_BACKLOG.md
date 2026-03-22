# pos_xml 项目 Backlog（与 ADO 对应）

---

## Epic: POS XML 提取与下游集成

**目标**：从 NAXML 提取交易数据，支持 payload 转换与下游 API 对接。

---

## Story 与 Task

### Story 1: 注册机制改造 ✅

| Task | 说明 | 状态 |
|------|------|------|
| base.py 增加 REGISTERED、register、get_line_extractors、LineExtractor | 统一 line 接口与注册表 | Done |
| 各 line extractor 加 @register 类 | FuelLine、ItemLine、TenderInfo、FuelPrepayLine | Done |
| transaction_extractor 改用 get_line_extractors | 替代 if/elif 硬编码 | Done |

**Acceptance Criteria**：新增 line 类型只需加类 + @register，无需改 transaction_extractor。

---

### Story 2: CI 流水线 ✅

| Task | 说明 | 状态 |
|------|------|------|
| 新建 scripts/validate.py | 运行 main 并检查输出 | Done |
| 新建 .github/workflows/ci.yml | push 触发验证 | Done |
| 验证 push 触发通过 | GitHub Actions 绿色 ✓ | Done |

**Acceptance Criteria**：push 到 main 后 GitHub Actions 自动运行并通过。

---

### Story 3: _pos_data → _payload 转换

| Task | 说明 | 状态 |
|------|------|------|
| 设计 pos_to_payload 字段映射 | 参考 POS_TO_PAYLOAD_PLAN.md | To Do |
| 实现 utils/payload_builder.py | 转换逻辑 | To Do |
| main 输出 _payload.json | 与 _pos_data.json 并存 | To Do |

**Acceptance Criteria**：main 输出 _payload.json，格式符合下游 API 要求。

---

### Story 4: Azure 部署（可选）

| Task | 说明 | 状态 |
|------|------|------|
| Function App 配置与 Terraform | IaC 部署 | Backlog |

---

## 层级关系

```
Epic
 └── Story
      └── Task
```

每个 Task 应可独立完成，预估工时可填在 ADO 的「Original Estimate」字段。
