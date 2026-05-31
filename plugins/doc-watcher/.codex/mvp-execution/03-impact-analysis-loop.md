# 03. Semantic Audit Loop

## Goal

在 deterministic evidence 基础上，使用 `doc-alignment` 内置语义对 active docs 做漂移审查，判断当前口径是否和实际代码、脚本、配置、入口文件一致。

## Current State

第一版由 `doc-alignment` skill 承接：脚本负责收集证据，agent 负责按 `doc-alignment` 内置的 current source of truth、active/history separation、naming、references、validation gates 规则做语义判断。

## Deliverables

- Skill 明确 audit-only 默认模式。
- Skill 内置 alignment 判断维度。
- Findings 按 High/Medium/Low 分级。
- 输出必须引用具体路径和证据。
- 未运行或失败的命令必须作为 blocker 报告。

## Task Breakdown

### P0

- 在 skill 中定义 audit trigger 和只读边界。
- 规定 source-of-truth 文件优先级。
- 规定 High/Medium/Low 分类。
- 规定最终输出结构。

### P1

- 增加 per-repo audit template。
- 增加 stale command detection。
- 增加 archive/current mixed guidance detection。

## Interfaces

- `skills/doc-alignment/SKILL.md` 是 agent workflow 入口。
- `audit_repo.py` 的 report 是 skill 的输入证据。
- `daily_report.py` 的 report 是定时运行产物。

## Acceptance Criteria

- Skill 不会在 audit 默认路径中修改目标 repo。
- Summary 能区分 deterministic findings 和 semantic review findings。
- 每条 finding 包含 severity、evidence、recommendation。
- 输出末尾给出 operator choices。

## Risks

- 不要把脚本能检测的断链等同于完整语义审查。
- 不要没有证据地推断文档过期。
- 不要在用户只要求 audit 时推进 implementation。
