# 01. Engineering Baseline

## Goal

建立可验证的插件和脚本基线，让 audit-first MVP 的后续改动可以用稳定命令检查。旧 backend/frontend 的命令保留为回归参考，但不再代表当前产品主线。

## Current State

- `.codex-plugin/plugin.json` 已存在，并指向 `skills/`。
- `skills/doc-alignment/SKILL.md` 已存在。
- `scripts/audit_repo.py`、`daily_report.py`、`commit_counter.py`、`doctor.py` 已存在。
- 旧 backend/frontend 测试和构建命令仍可按需运行。

## Deliverables

- 插件 manifest 可被 plugin validator 接受。
- 所有 plugin scripts 可 `py_compile`。
- `doctor.py` 能检查 manifest、skill、scripts、state dir 和 repo config。
- 示例配置可用于 `my-codex` monorepo 的 smoke audit。

## Task Breakdown

### P0

- 新增 `.codex-plugin/plugin.json`。
- 新增 `doc-alignment` skill。
- 新增 `config/repos.example.json`。
- 新增只依赖标准库的 audit/report/counter/doctor 脚本。
- 验证脚本 help 和基础运行路径。

### P1

- 给脚本增加 focused unit tests。
- 将 private `config/repos.json` 加入本地使用说明。
- 梳理旧 app 命令，仅作为 legacy validation。

## Interfaces

- `python3 scripts/audit_repo.py --repo <path> --name <name> --print-report`
- `python3 scripts/daily_report.py --config <path> --print-report`
- `python3 scripts/commit_counter.py --config <path>`
- `python3 scripts/doctor.py --config <path>`

## Acceptance Criteria

- `python3 -m py_compile scripts/*.py` 通过。
- `python3 scripts/doctor.py --config config/repos.example.json` 通过。
- `python3 scripts/audit_repo.py --repo ../.. --name my-codex --print-report` 生成 report。
- plugin validator 通过；使用 `PLUGIN_VALIDATOR="${PLUGIN_VALIDATOR:-${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py}" && (cd backend && uv run python "$PLUGIN_VALIDATOR" ..)`，因为 validator 需要 PyYAML。

## Risks

- 不要把 private repo 列表提交到共享配置。
- 不要给脚本引入隐式第三方依赖。
- 失败必须带出具体路径、命令和原因。
