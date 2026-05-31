# MVP Acceptance Checklist

本清单对照 `README.md` 中的 audit-first MVP workflow 和验收目标。每完成一个 milestone 后更新状态。

| # | 验收标准 | 目标 Milestone | 当前状态 | 验证方式 |
| --- | --- | --- | --- | --- |
| 1 | 有有效的 Codex plugin manifest | M0 | 已完成 | plugin validator |
| 2 | 有 audit skill 入口 | M0 | 已完成 | `skills/doc-alignment/SKILL.md` 存在且 validator 可读 |
| 3 | 可以对单个本地 repo 做只读 audit | M1 | 已完成 | `python3 scripts/audit_repo.py --repo ../.. --name my-codex --print-report` |
| 4 | 可以按配置生成 daily report | M3/M4 | 已完成 | `python3 scripts/daily_report.py --config config/repos.example.json --print-report` |
| 5 | 可以检查 commit-dependent due 状态 | M4 | 已完成 | `python3 scripts/commit_counter.py --config config/repos.example.json` |
| 6 | 可以建立 last audited baseline | M4 | 已完成 | `python3 scripts/commit_counter.py --config config/repos.example.json --mark-current` |
| 7 | doctor 能检查插件、脚本、配置和 state dir | M0 | 已完成 | `python3 scripts/doctor.py --config config/repos.example.json` |
| 8 | report 包含 evidence、findings、recommendations | M2/M3 | 已完成 | 查看生成的 Markdown report |
| 9 | 失败 repo 会进入 failure section 并导致非零退出 | M3 | 已完成 | 使用不存在的 repo path 运行 daily report |
| 10 | active roadmap 仅保留 dashboard/webhook 作为复用资产 | M5 | 已完成 | README 和 `06-dashboard-webhook-reuse.md` |

## Milestone Completion Gates

### M0 Engineering Baseline

- [x] `.codex-plugin/plugin.json` 存在。
- [x] `skills/doc-alignment/SKILL.md` 存在。
- [x] `scripts/*.py` 可编译。
- [x] plugin validator 通过。

### M1 Local Readonly Loop

- [x] Repo config 示例存在。
- [x] audit command 不写目标 repo。
- [x] missing paths、broken links、watch terms 能进入 findings。
- [x] changed files 和 recent commits 能进入 report。

### M2 Semantic Audit Loop

- [x] Skill 内置 alignment 语义。
- [x] Skill 明确 audit-only 默认边界。
- [x] Findings 有 severity、evidence、recommendation。
- [x] Output 包含 operator choices。

### M3 Audit Summary And Operator Decision

- [x] 单 repo audit 写入 `audits/`。
- [x] Daily report 写入 `reports/`。
- [x] Daily report 显示 audited/skipped/failed counts。
- [x] 失败不伪装成成功。

### M4 Plugin Audit Runner

- [x] Daily mode 可运行。
- [x] Commit-dependent mode 可运行。
- [x] `--mark-audited` 可更新 state。
- [x] Doctor 可运行。

### M5 Dashboard And Webhook Reuse

- [x] Active docs 明确 dashboard 是未来 audit 展示面。
- [x] Active docs 明确 webhook 是未来 audit 触发面。
- [x] 旧 app 不再定义当前 MVP 主线。
