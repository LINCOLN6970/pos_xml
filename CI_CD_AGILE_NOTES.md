# 自动化流程与敏捷协作笔记

团队围绕 GitHub Actions 的 CI/CD 实践与 Terraform 的 IaC 方法进行了系统化讲解，并介绍了 Azure DevOps / Jira 下的敏捷协作方式。

---

## 一、持续集成与自动化部署（GitHub Actions）

### 1.1 部署流程

- 部署通过「流水线」完成：代码提交或满足指定条件后，自动将最新代码部署到云环境（如 GitHub 或 Azure），无需手动执行原先的「function publish」等命令。
- 触发条件可配置：指定分支、指定文件/目录变更即触发；一旦触发，系统会将 Integration 中的全部代码（action、function 等）部署到目标环境。

### 1.2 标准化与安全

- 符合行业通用标准；通过调整流水线参数即可切换环境（production、BOT、QIT），减少人为误操作。
- 出错时会有明确提示，并可查看详细错误日志。

### 1.3 学习建议

- GitHub Actions 是必备技能；可通过 YouTube 或 AI 助手学习。
- 建议从简单应用部署开始，逐步熟悉。

### 1.4 其他说明

- 公司试用 Open Cloud，但目前顾虑数据泄露，建议在本地 localhost 验证后关闭。
- 部署耗时取决于代码规模，通常几分钟内可完成。

---

## 二、基础设施即代码（Terraform）

### 2.1 资源定义

- 使用 Terraform 将 Azure 等云资源抽象为 component（如 function app），通过参数化方式创建，实现可重复的环境搭建。

### 2.2 部署与灾备

- 支持在 US West Two（US Central）等数据中心一键部署整套系统；数据中心故障时可快速迁移至其他区域。
- 常用命令：`terraform plan`、`terraform deploy`、`terraform destroy`（一键删除整个 infra）。

### 2.3 规模与可靠性

- 可一次性部署几十至上百个服务，或在多账号下批量部署。
- 大公司（如 Google、Docker）普遍采用类似方式，实现分钟级恢复。

### 2.4 价值与建议

- 减少手动创建带来的错误，提升速度和可维护性。
- 当前项目框架由 Speaker 3 编写和维护，建议新成员熟悉该 IaC 实践。

---

## 三、敏捷协作：项目管理工具与工作流

团队通过 Azure DevOps（ADO）与 Jira 使用敏捷方法管理任务，保证过程透明、可追踪、可度量。

### 3.1 基本层级与角色

| 层级 | 说明 |
|------|------|
| **Project** | 项目 |
| **Epic** | 大主题（如 Integration） |
| **User Story** | 特性或功能单元 |
| **Task** | 可执行的具体工作 |

| 角色 | 职责 |
|------|------|
| **Scrum Master** | 管理流程与分解 |
| **Product Owner（PO）** | 定义验收标准（Acceptance Criteria）并签收 |
| **开发人员** | 执行任务，记录进度与工时 |

- Task 可设置 Parent/Child/Related 等依赖；附件与链接用于存放数据样例、问题描述、参考文档。

### 3.2 流程与度量

- **状态**：支持 defer、do、block、defer release、done 等。
- **优先级**：Critical 高于 High。
- **验收标准**：PO 定义 Acceptance Criteria，满足后任务可 complete 并 signoff。
- **工时**：预估与实际工时可调整并备注（如 6–8h、8h→16h→24h）；管理层通过报表查看个人/团队工作量、成本与进度。

### 3.3 工具生态

| 工具 | 特点 |
|------|------|
| **ADO** | 与 Azure 生态集成紧密 |
| **Jira** | 通用性强，可接入多种生态 |

- 任务交流、文档和操作均留有记录，形成完整 log。
- 部署规划可拆分为「1-2-3-4 步」放入 Task，便于复用与审计。

### 3.4 面试与实践

- 建议能清晰说明所用管理工具（ADO/Jira）及敏捷概念（Epic、User Story、Task）。
- 这些技能通常被视为必备。
