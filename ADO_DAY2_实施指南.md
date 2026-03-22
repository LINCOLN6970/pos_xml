# Day 2：用 Azure DevOps (ADO) 做敏捷协作

---

## 一、前置条件

- [ ] 已有 Azure DevOps 账号（可访问 dev.azure.com）
- [ ] 组织或项目创建权限（若为个人试用，可自建 Organization）

---

## 二、操作步骤

### 步骤 2.1：创建或进入项目

1. 打开 https://dev.azure.com
2. 登录后，若尚无组织，点击 **Create new organization**
3. 点击 **New project**
4. 填写：
   - **Project name**：`pos_xml` 或 `pos_xml_qilong`
   - **Visibility**：Private 或 Public
   - **Version control**：Git
   - **Work item process**：Agile（推荐）或 Scrum
5. 点击 **Create**

**为什么**：项目是 Epic、Story、Task 的容器，所有工作项都在项目内管理。

---

### 步骤 2.2：创建 Epic

1. 进入项目后，左侧点击 **Boards** → **Work items**
2. 点击 **New work item**，选择 **Epic**
3. 填写：
   - **Title**：`POS XML 提取与下游集成`
   - **Description**：简要说明项目目标，如「从 NAXML 提取交易数据，支持 payload 转换与 API 对接」
4. 保存（Ctrl+S 或右上角 ✓）

**为什么**：Epic 代表大目标，后续的 Story 和 Task 都挂在 Epic 下。

---

### 步骤 2.3：创建 User Story

1. 在 **Work items** 中，点击 **New work item** → **User Story**
2. 在 **Parent** 中关联刚建的 Epic
3. 创建以下 Story（可分批创建）：

| Story 标题 | 说明 | 状态 |
|-------------|------|------|
| 注册机制改造 | line extractor 用 @register 替代 if/elif | Done |
| CI 流水线 | GitHub Actions 自动验证 | Done |
| _pos_data → _payload 转换 | 生成下游 API 所需 payload | To Do |
| Azure 部署（可选） | Function App / Terraform | Backlog |

4. 每个 Story 的 **Description** 中写清验收标准（Acceptance Criteria）

**为什么**：Story 是可交付的功能单元，PO 据此验收。

---

### 步骤 2.4：为每个 Story 创建 Task

以 **「注册机制改造」** 为例：

1. 打开该 Story，在 **Child** 区点击 **Add link** → **New item** → **Task**
2. 创建 Task：
   - Task 1：`base.py 增加 REGISTERED、register、get_line_extractors、LineExtractor`
   - Task 2：`各 line extractor 加 @register 类`
   - Task 3：`transaction_extractor 改用 get_line_extractors 循环`

3. 每个 Task 的 **Acceptance Criteria** 示例：
   - Task 1：base.py 中有 REGISTERED、register、get_line_extractors、LineExtractor 定义
   - Task 2：fuel_extractor、item_extractor、tender_extractor、fuel_prepay_extractor 均有 @register 类
   - Task 3：transaction_extractor 中无 if/elif，改为 for extractor in get_line_extractors()

**为什么**：Task 是可执行的开发任务，便于分配和跟踪工时。

---

### 步骤 2.5：设置状态与看板

1. 进入 **Boards** → **Boards**，选择 **pos_xml** 对应的看板
2. 将已完成的 Story/Task 拖到 **Done**
3. 将「_pos_data → _payload 转换」拖到 **To Do** 或 **In Progress**

**为什么**：看板可视化进度，团队一目了然。

---

### 步骤 2.6：关联代码仓库（可选）

1. 进入 **Repos** → **Repositories**
2. 若代码在 GitHub，可：
   - 点击 **Import**，输入 `https://github.com/LINCOLN6970/pos_xml`
   - 或使用 **Service connection** 连接 GitHub，在 Pipelines 中关联

**为什么**：便于在 ADO 中查看代码、关联 PR、或在 Pipelines 中跑 CI（若后续迁移到 Azure Pipelines）。

---

## 三、Epic / Story / Task 结构（供录入参考）

```
Epic: POS XML 提取与下游集成
│
├── Story: 注册机制改造 ✅
│   ├── Task: base.py 增加 REGISTERED、register 等
│   ├── Task: 各 line extractor 加 @register 类
│   └── Task: transaction_extractor 改用 get_line_extractors
│
├── Story: CI 流水线 ✅
│   ├── Task: 新建 scripts/validate.py
│   ├── Task: 新建 .github/workflows/ci.yml
│   └── Task: 验证 push 触发通过
│
├── Story: _pos_data → _payload 转换
│   ├── Task: 设计 pos_to_payload 字段映射
│   ├── Task: 实现 utils/payload_builder.py
│   └── Task: main 输出 _payload.json
│
└── Story: Azure 部署（可选）
    └── Task: Function App 配置与 Terraform
```

---

## 四、验收标准（Acceptance Criteria）示例

| 工作项 | Acceptance Criteria |
|--------|---------------------|
| 注册机制改造 | 新增 line 类型只需加类 + @register，无需改 transaction_extractor |
| CI 流水线 | push 到 main 后 GitHub Actions 自动运行并通过 |
| payload 转换 | main 输出 _payload.json，格式符合下游 API 要求 |

---

## 五、Day 2 完成标准

- [ ] ADO 项目已创建
- [ ] 至少有 1 个 Epic、3+ Story、若干 Task
- [ ] 每个 Task 有可执行的 Acceptance Criteria
- [ ] 看板能反映当前进度（Done/To Do）
