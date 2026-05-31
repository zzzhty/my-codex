# 06. Dashboard And Webhook Reuse

## Goal

明确旧 app 中仅 dashboard 和 webhook 思路进入未来路线：dashboard 用于展示 audit backlog/trends，webhook 用于触发 audit event。二者都不承担默认写入职责。

## Current State

旧 backend/frontend 已有 dashboard 和 webhook 代码，但它们围绕旧状态模型设计。当前 MVP 不继续沿用旧状态模型，只把交互形态和事件入口作为未来可复用资产。

## Deliverables

- Dashboard 未来展示 audit reports、findings severity、due repos、drift trend。
- Webhook 未来只触发 read-only audit 或记录 event。
- 旧写入状态模型不进入新路线。
- README 中明确旧 app 不是当前 MVP 主线。

## Task Breakdown

### P0

- 在 README 和 scope docs 中标明 dashboard/webhook 是可复用资产。
- 移除 active roadmap 中的远端写入路线。
- 保留旧 app 命令作为 legacy validation。

### P1

- 设计 audit dashboard schema。
- 设计 webhook event schema。
- 将 report index 暴露给 dashboard。
- 将 webhook 触发接入 daily/commit-dependent runner。

## Interfaces

- Dashboard future inputs：report path、repo name、finding severity、generated_at、status。
- Webhook future inputs：repo identity、event type、revision range、received_at。
- Runtime state remains under `$CODEX_HOME/doc-watcher/`.

## Acceptance Criteria

- Active docs 中 dashboard/webhook 只作为 audit 辅助面出现。
- Future route 不依赖远端写入流程。
- Webhook 触发失败必须可见，不静默跳过。
- Dashboard 不展示过时状态为当前产品事实。

## Risks

- 不要把旧数据库状态直接映射成新 audit 状态。
- 不要让 webhook 成为隐式写入口。
- 不要让 dashboard 掩盖 report command 的失败。
