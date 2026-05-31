# 05. Plugin Audit Runner

## Goal

把 DocWatcher 包装成 source-only Codex plugin，支持 daily scan 和 commit-dependent scan，贴近日常个人工作流。

## Current State

已新增 `.codex-plugin/plugin.json`、`skills/doc-alignment/SKILL.md` 和四个标准库脚本。插件默认写 runtime reports，不修改目标 repo。

## Deliverables

- Plugin manifest 通过 validator。
- Daily mode 可扫描所有 configured repos。
- Commit-dependent mode 可基于 `repo-state.json` 判断 due/skip。
- `--mark-audited` 只在 successful audits 后更新 state。
- Doctor 可检查基本安装状态。

## Task Breakdown

### P0

- 创建 plugin manifest。
- 创建 audit skill。
- 创建 daily report script。
- 创建 commit counter script。
- 创建 doctor script。

### P1

- 增加 Codex automation 建议配置。
- 增加 per-repo thresholds。
- 增加 state migration/version 字段。
- 增加 local report index。

## Interfaces

- `.codex-plugin/plugin.json`
- `skills/doc-alignment/SKILL.md`
- `scripts/daily_report.py --mode daily`
- `scripts/daily_report.py --mode commit-dependent --mark-audited`
- `scripts/commit_counter.py --mark-current`

## Acceptance Criteria

- 插件 validator 通过。
- `daily_report.py --config config/repos.example.json --print-report` 可运行。
- `daily_report.py --mode commit-dependent` 能跳过未 due repos。
- `commit_counter.py --mark-current` 能建立 baseline。

## Risks

- 不要在 plugin manifest 中声明 unsupported hook fields。
- 不要让 automation 默认修改目标 repo。
- 不要在失败时写入 misleading state。
