# 04. Audit Summary And Operator Decision

## Goal

把 repo audit 结果收敛成操作者能直接判断的 summary：哪些文档可能漂移、为什么、风险级别、建议动作、是否需要进入 `doc-alignment` implementation mode。

## Current State

`audit_repo.py` 和 `daily_report.py` 已生成 Markdown summary。当前默认结束点是 report，不自动进入修改。

## Deliverables

- Report 写入 `~/.codex/doc-watcher/reports/` 或 `audits/`。
- Summary 包含 reviewed repos、source-of-truth、recent commits、changed files、findings 和 review focus。
- Daily report 汇总 audited/skipped/failed repos。
- Failure 不隐藏：至少一个 repo 失败时 daily command 退出非零。
- Operator choices 明确：保留报告、运行 bounded alignment、调整配置。

## Task Breakdown

### P0

- 单 repo audit report。
- 多 repo daily report。
- Failure section。
- Skipped section。
- Findings count。

### P1

- 增加 status update 脚本，记录 accepted/ignored/deferred findings。
- 增加 rejected/accepted audit buffer。
- 增加 report retention 策略。

## Interfaces

- `audit_repo.py` 默认写 `~/.codex/doc-watcher/audits/`。
- `daily_report.py` 默认写 `~/.codex/doc-watcher/reports/`。
- `DOC_WATCHER_STATE_DIR` 可覆盖 runtime state。

## Acceptance Criteria

- 单 repo audit 可打印和写入 report。
- Daily report 可汇总至少一个 repo。
- 失败 repo 会显示具体失败原因。
- Report 不包含自动修改承诺。

## Risks

- 不要把 skipped repo 当作 audited repo。
- 不要在失败时更新 last audited revision。
- 不要让 report 缺少证据路径。
