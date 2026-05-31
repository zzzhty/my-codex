# 00. Scope And Decisions

## Goal

本 MVP 的目标是跑通 `README.md` 定义的 audit-first 文档漂移闭环：

`配置本地 repos -> 触发扫描 -> 收集只读 evidence -> 语义 audit -> 写入 summary -> 操作者决定是否修改`

## Current State

项目已从旧的远端评审平台口径 pivot 到个人工作流插件口径。当前 active surface 包含 plugin manifest、`doc-alignment` skill、repo audit 脚本、daily report 脚本、commit counter 和 doctor。

旧 backend/frontend 代码仍留在仓库中，但不再定义 MVP 主线。后续只复用 dashboard 和 webhook 思路。

## In Scope

- 本地 Git repo 配置和只读扫描。
- README、AGENTS、docs、scripts、配置和 recent commits 的 evidence pack。
- 基于 `doc-alignment` 内置语义的漂移审查。
- Report-only audit summary。
- Daily scan。
- Commit-dependent scan。
- Runtime state：`$CODEX_HOME/doc-watcher/reports/`、`audits/`、`repo-state.json`。
- Dashboard 和 webhook 的复用设计边界。

## Out Of Scope

- 自动修改目标 repo。
- 默认生成文档补丁。
- 远端代码托管写入闭环。
- 团队权限、多租户、secret vault、复杂 provider 体系。
- 生产级后台服务。
- 对旧 backend/frontend 做大规模删除或重写。

## Locked Decisions

- 默认模式：只读 audit，先 report。
- 配置格式：`config/repos.json`，示例为 `config/repos.example.json`。
- 触发路线：daily 和 commit-dependent 并行支持。
- 状态路线：`never_audited -> due -> audited -> needs_operator_decision`。
- 修改路线：只有用户明确要求 implementation 时才进入 `doc-alignment` 修改流程。
- Runtime 目录：默认 `$CODEX_HOME/doc-watcher/`。
- 可复用旧资产：dashboard、webhook。

## Shared Acceptance Criteria

- 用户可以配置至少一个本地 repo 并生成 audit report。
- report 包含 evidence、findings、recommended actions 和 unresolved blockers。
- commit-dependent mode 能根据 last audited revision 判断是否 due。
- daily mode 能汇总多个 repos。
- 目标 repo 在默认 workflow 中没有文件写入。
