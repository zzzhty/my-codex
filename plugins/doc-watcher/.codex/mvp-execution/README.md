# DocWatcher MVP Execution Pack

本目录把 `README.md` 中的 audit-first 产品方向转成可执行工程计划。执行主线固定为 **local repos -> semantic audit -> report-only summary -> operator decision**。

## 文档索引

| 文件 | 用途 |
| --- | --- |
| `00-scope-and-decisions.md` | MVP 范围、默认决策、非目标和状态主线 |
| `01-engineering-baseline.md` | Milestone 0：插件、脚本和旧 app 的验证基线 |
| `02-local-readonly-loop.md` | Milestone 1：本地 repo 配置、只读 inventory 和 evidence pack |
| `03-impact-analysis-loop.md` | Milestone 2：语义漂移 audit 和内置 alignment 语义 |
| `04-patch-preview-quality-gate.md` | Milestone 3：audit summary、操作者决策和状态记录 |
| `05-plugin-audit-runner.md` | Milestone 4：source-only plugin、daily report 和 commit-dependent scan |
| `06-dashboard-webhook-reuse.md` | Milestone 5：dashboard 与 webhook 的可复用边界 |
| `acceptance-checklist.md` | 对照 audit-first MVP workflow 的验收清单 |

## 执行顺序

1. 完成 `01-engineering-baseline.md`，保证插件 manifest、脚本和现有测试命令可验证。
2. 完成 `02-local-readonly-loop.md`，让配置中的本地 repo 能被只读扫描并生成 evidence pack。
3. 完成 `03-impact-analysis-loop.md`，用 `doc-alignment` 内置语义判断文档漂移。
4. 完成 `04-patch-preview-quality-gate.md`，把结果收敛成 report-only summary 和可操作决策。
5. 完成 `05-plugin-audit-runner.md`，支持 daily 和 commit-dependent 两种触发方式。
6. 完成 `06-dashboard-webhook-reuse.md`，仅把 dashboard/webhook 作为后续可复用面。

## 全局执行约束

- MVP 不修改目标 repo，不生成默认补丁。
- MVP 不引入远端代码托管写入流程。
- Runtime state 只写入 `$CODEX_HOME/doc-watcher/` 或显式输出路径。
- 配置默认使用 JSON，避免增加个人工作流依赖。
- 每个 report 必须包含证据路径、失败原因、推荐动作和未解决 blocker。
- 每个 milestone 完成后更新 `acceptance-checklist.md` 对应项。

## 完成定义

每个 milestone 必须同时满足：

- 相关命令按文档要求通过，或记录明确阻塞原因。
- 新增脚本对失败直接退出，不制造空成功。
- audit 输出能被操作者直接用于判断下一步。
- active docs 不把历史实现当作当前路线。
