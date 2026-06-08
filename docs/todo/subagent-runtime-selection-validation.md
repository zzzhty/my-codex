# Long-Run Goal: Subagent Runtime Selection Validation

Status: Ready

整体状态：Ready

当前轮次：M0 Ready

目标 owner：`Max / my-codex agents`

目标路径：`docs/todo/subagent-runtime-selection-validation.md`

Planning root：`docs`

Goal directory：`docs/todo`

## 目标摘要

本 goal 收口 v1 custom-agent routing 中唯一仍带 partial coverage 的 runtime 证据问题：当前仓库已经管理并同步 `code_mapper`、`reviewer`、`docs_researcher` 三个 read-only custom agents，但上一轮运行时验证只能证明 subagent threads 被派生并带有 assignment labels，不能证明 Codex runtime 实际加载的 agent type 正是这些 custom-agent TOML。

最终目标态：

1. 明确当前 Codex runtime 是否提供可调用、可验证的 custom-agent selector。
2. 若提供 selector，记录可复现命令、事件证据和每个 M1 custom agent 的加载证据。
3. 若不提供 selector，更新 current docs 和 orchestration contract，把 custom-agent-first 降级为配置准备态，并明确 built-in fallback 是当前可验证 runtime 行为。
4. 不把 write-capable agents、advisor skill 或 project-scoped `.codex/agents/` 混入本 goal。

## M0 执行前基线

当前事实：

1. [docs/agents/subagent-roster.md](../agents/subagent-roster.md) 是当前 custom subagent roster source of truth，M1 只包含 `code_mapper`、`reviewer`、`docs_researcher` 三个 read-only agents。
2. [codex-home/agents/](../../codex-home/agents/) 是 repo-managed source TOML；`scripts/sync_codex_agents.py` 将 managed copies 同步到 `$CODEX_HOME/agents/`。
3. [plugins/orchestration/skills/orchestrate-subagents/SKILL.md](../../plugins/orchestration/skills/orchestrate-subagents/SKILL.md) 已经采用 custom-agent-first + built-in fallback 的文档合同。
4. [docs/todo/archive/subagent-model-routing-v1.md](archive/subagent-model-routing-v1.md) 记录 v1 已关闭，但 runtime role coverage 仍是 partial：当时 `multi_agent_v1.spawn_agent` API 没有暴露 custom-agent selector。
5. `python3 scripts/sync_codex_agents.py --check --prune --codex-home "${CODEX_HOME:-$HOME/.codex}"` 已在创建本 goal 前通过，说明 managed target 当前同步。

已读取的当前事实源：

1. Root `AGENTS.md` and [README.md](../../README.md).
2. [docs/agents/agent-operating-model.md](../agents/agent-operating-model.md).
3. [docs/agents/subagent-roster.md](../agents/subagent-roster.md).
4. [docs/todo/README.md](README.md).
5. [docs/todo/archive/subagent-model-routing-v1.md](archive/subagent-model-routing-v1.md).
6. [plugins/orchestration/skills/orchestrate-subagents/SKILL.md](../../plugins/orchestration/skills/orchestrate-subagents/SKILL.md).

## Goal 执行合同

如果本计划被作为 long-running goal 执行，必须按以下合同推进：

1. 阶段必须顺序执行：`M0 -> M1 -> M2 -> M3 -> Close`。
2. 每个阶段开始前必须把阶段状态改为 `In Progress`。
3. 每个阶段完成后必须记录代码证据、行为证据、测试证据、文档证据、回滚证据和剩余风险。
4. 每个阶段必须记录 checkpoint evidence。若用户要求提交，使用 `subagent-runtime-selection-validation M1: runtime selector surface` 这类格式；否则记录文档修订、diff evidence 或明确写 `Not applicable: no checkpoint commit requested`。
5. 未满足当前阶段 review gate 时，不得进入下一阶段。
6. 失败必须停在失败点，记录 root cause、失败命令或路径、已知 breakpoint 和下一步诊断。
7. 不允许用 assignment label、generic subagent success、silent fallback、兼容假成功、alternate backend 或隐藏 partial success 来伪装 exact custom-agent selection 已验证。
8. 任何涉及 `$CODEX_HOME/agents/`、Codex plugin cache、runtime logs、subagent thread output 或 hook trust 的动作都必须有显式命令输出作为证据。
9. 如果执行中发现 Codex runtime surface 与当前文档假设不一致，必须先更新本计划或 current docs，再继续验证。
10. Close 只能在 runtime selector 状态被明确证明或明确否定、current docs 同步、最终验证通过之后执行。

## 状态定义

| 状态 | 含义 |
|---|---|
| `Ready` | 设计与验收指标已明确，可以开始该阶段 |
| `Not Started` | 阶段尚未开始，且必须等待前置阶段完成 |
| `In Progress` | 当前阶段正在实现或验证 |
| `Blocked` | 当前阶段因明确失败或未决设计被阻塞 |
| `Done` | 阶段 review gate、验证和 checkpoint evidence 均已完成 |
| `Closed` | 整体计划完成，并已从 active TODO 导航移除或归档 |

## Owner Boundaries

### Runtime selection evidence

本 goal 只负责证明或否定当前 Codex runtime 是否能选择并证明 M1 custom-agent TOML。它不改变 Codex upstream runtime。

### `orchestration` plugin

`orchestration:orchestrate-subagents` 继续负责 assignment、ownership、evidence、failure handling 和 parent consolidation。若 runtime selector 不可用，orchestration docs 必须明确使用 built-in fallback 的真实运行边界。

### custom-agent source

`codex-home/agents/` 和 `$CODEX_HOME/agents/` 的 sync 机制保持现状。本 goal 可以读取和检查这些文件，但不新增 write-capable agent。

### parent agent

parent agent 继续负责规划、是否派生、写范围控制、最终整合、验证和用户结论。即使 runtime selector 可用，custom agents 也不替代 parent judgment。

## Compatibility Surface

1. Existing M1 custom-agent source files and managed sync must continue to pass.
2. Built-in roles `explorer`、`default`、`worker` remain supported fallbacks.
3. `$orchestrate-subagents` remains the explicit invocation path.
4. Current recipes must not require custom-agent selector availability unless this goal proves and documents the exact selector.
5. If a pinned model is unavailable, fallback behavior must be explicit and reported as partial coverage rather than hidden model substitution.

## 非目标 / Future 边界

本 goal 不处理：

1. 不新增 `impl_worker` 或 `test_runner`。
2. 不新增 `$subagent-fit-check` advisor skill。
3. 不引入 project-scoped `.codex/agents/` dogfood。
4. 不修改 external Codex runtime 或伪造 runtime selector。
5. 不把 generic subagent assignment label 当成 exact custom-agent type evidence。
6. 不修改 Skill Watcher runtime logs、generated reports 或 hook trust 状态。

## 目标结构

### Runtime Surface Discovery

1. 检查当前 Codex CLI、runtime events、subagent tool schema 和官方文档是否暴露 custom-agent selector。
2. 记录 selector 名称、参数、限制和不可用时的错误。
3. 区分三类证据：selector exists、selector absent、selector exists but current account/model unavailable。

### Empirical Validation Matrix

1. 对 `code_mapper`、`reviewer`、`docs_researcher` 分别尝试可复现的 read-only runtime validation。
2. 每个尝试必须记录命令、exit code、thread id、subagent output、是否能证明 exact custom-agent type。
3. 验证不能只依赖 prompt label，例如 `reviewer as risk-reviewer` 不能单独算作 `reviewer.toml` 已加载。

### Contract Sync

1. 若 exact selector 已验证，更新 roster、orchestration skill、recipes 和 README 中的调用规则。
2. 若 exact selector 未提供或不可证明，更新 current docs，把 custom-agent-first 说明限定为 "when runtime exposes custom agents"，并把 built-in fallback 标为当前可验证路径。
3. 保留 write-capable/advisor/project-scoped work as Future。

## 阶段计划

### M0 - Baseline And Contract Freeze

状态：Ready

范围：

1. 确认本 goal 的 active TODO 位置、当前事实源和非目标边界。
2. 更新 active TODO index 和 current docs，让这个 runtime selector 缺口有 durable home。
3. 不运行破坏性命令，不修改 `$CODEX_HOME/agents/` 内容。

Review gate：

1. 本文件无未替换占位符，并能通过 long-run-goal readiness check。
2. [docs/todo/README.md](README.md) indexes this file as an active long-running goal。
3. Current docs point runtime selector validation at this goal, not archive-only history。
4. `scripts/sync_codex_agents.py --check --prune` still passes against intended `$CODEX_HOME`。

执行证据：

1. 代码证据：
   - 待执行时填写。
2. 行为证据：
   - 待执行时填写。
3. 测试证据：
   - 待执行时填写。
4. 文档证据：
   - 待执行时填写。
5. 回滚证据：
   - Revert this active goal file and TODO/current-doc pointer edits.
6. 剩余风险：
   - Runtime selector surface may change between planning and execution, so M1 must re-check live docs and local CLI/tool schema.

推荐验证：

```bash
python3 /Users/max/.codex/plugins/cache/my-codex/workflow/0.1.0/skills/long-run-goal/scripts/check_goal_ready.py docs/todo/subagent-runtime-selection-validation.md
python3 /Users/max/.codex/plugins/cache/my-codex/workflow/0.1.0/skills/long-run-goal/scripts/check_todo_index.py docs/todo/subagent-runtime-selection-validation.md docs/todo/README.md
python3 /Users/max/.codex/plugins/cache/my-codex/workflow/0.1.0/skills/long-run-goal/scripts/check_md_links.py docs
python3 /Users/max/.codex/plugins/cache/my-codex/doc-watcher/0.2.0/skills/doc-alignment/scripts/check_planning_tree.py docs/todo
python3 scripts/sync_codex_agents.py --check --prune --codex-home "${CODEX_HOME:-$HOME/.codex}"
git diff --check -- README.md docs/agents/agent-operating-model.md docs/todo/README.md docs/todo/subagent-runtime-selection-validation.md
```

Checkpoint evidence：

```text
Not applicable until M0 is executed; planning file created and indexed in active TODO.
```

### M1 - Runtime Selector Surface Discovery

状态：Not Started

范围：

1. Inspect current Codex CLI help, available subagent tooling schema, official custom-agent docs, and runtime JSON events for any custom-agent selector surface.
2. Record exact command/tool field names if a selector exists.
3. Record exact absence evidence if no selector exists.
4. Do not edit source TOML, orchestration docs, or `$CODEX_HOME` in M1.

Review gate：

1. Evidence distinguishes assignment labels from custom-agent type selection.
2. At least one local runtime command or tool schema inspection result is recorded.
3. Any web/official-doc claim uses dated source links or local cached docs evidence.
4. If selector is absent, the absent-surface conclusion is tied to concrete commands/schema output rather than inference.

执行证据：

1. 代码证据：
   - 待执行时填写。
2. 行为证据：
   - 待执行时填写。
3. 测试证据：
   - 待执行时填写。
4. 文档证据：
   - 待执行时填写。
5. 回滚证据：
   - M1 is read-only discovery; revert only evidence edits in this file if needed.
6. 剩余风险：
   - 待执行时填写。

推荐验证：

```bash
codex --help
codex exec --help
python3 scripts/sync_codex_agents.py --check --prune --codex-home "${CODEX_HOME:-$HOME/.codex}"
```

Checkpoint evidence：

```text
Not started.
```

### M2 - Empirical Custom-Agent Validation Matrix

状态：Not Started

范围：

1. Build a read-only validation matrix for `code_mapper`、`reviewer`、`docs_researcher`。
2. If selector exists, run one minimal task per custom agent and capture command, exit code, thread id, output, and exact custom-agent evidence.
3. If selector does not exist, run one controlled fallback validation and record why it cannot prove custom-agent type.
4. Do not edit files from subagents; validation tasks must be read-only.

Review gate：

1. Each M1 custom agent has a row with result: `Verified`, `Unavailable`, or `Not Provable With Current Runtime`。
2. Evidence includes command output or runtime event output, not just narrative.
3. Pinned model failures, selector failures, or sandbox/read-only limitations are reported directly.
4. No write-capable custom agent or advisor behavior is introduced.

执行证据：

1. 代码证据：
   - 待执行时填写。
2. 行为证据：
   - 待执行时填写。
3. 测试证据：
   - 待执行时填写。
4. 文档证据：
   - 待执行时填写。
5. 回滚证据：
   - M2 should not change source files beyond evidence; revert this file's M2 evidence if invalid.
6. 剩余风险：
   - 待执行时填写。

推荐验证：

```bash
python3 scripts/sync_codex_agents.py --check --prune --codex-home "${CODEX_HOME:-$HOME/.codex}"
codex -a never exec --json -C /Users/max/Projects/my-codex -s read-only --output-last-message /tmp/my-codex-runtime-selector-validation.md "<M2 prompt from this goal>"
```

M2 prompt skeleton：

```text
Use $orchestrate-subagents.

Task: Validate whether the current runtime can select exact custom agents, without editing files.

For each available selector path, try bounded read-only validation for:
- code_mapper
- reviewer
- docs_researcher

For each attempt, report:
- command or tool call shape
- thread id if present
- whether exact custom-agent type is proved
- evidence path or output excerpt
- fallback used, if any

Do not treat assignment labels as custom-agent proof.
Do not edit files.
```

Checkpoint evidence：

```text
Not started.
```

### M3 - Runtime Contract Sync

状态：Not Started

范围：

1. Update current docs to match M1/M2 evidence.
2. If selector is verified, document exact usage in roster and orchestration guidance.
3. If selector is not provable, document current verified behavior as built-in fallback with custom-agent TOML ready but not runtime-proven.
4. Archive or close this active goal only after current docs and TODO index are synchronized.

Review gate：

1. No current doc claims exact custom-agent runtime selection unless M2 proves it.
2. Orchestration skill continues to tell agents to report partial coverage when custom agents or pinned models are unavailable.
3. README, agent operating model, roster, TODO index, and archive index agree on current state.
4. `scripts/check_my_codex.py` passes or every skipped check has a concrete reason.

执行证据：

1. 代码证据：
   - 待执行时填写。
2. 行为证据：
   - 待执行时填写。
3. 测试证据：
   - 待执行时填写。
4. 文档证据：
   - 待执行时填写。
5. 回滚证据：
   - Revert M3 doc edits; keep M1/M2 evidence unless it is known invalid.
6. 剩余风险：
   - 待执行时填写。

推荐验证：

```bash
python3 scripts/check_my_codex.py
python3 /Users/max/.codex/plugins/cache/my-codex/workflow/0.1.0/skills/long-run-goal/scripts/check_md_links.py docs
python3 /Users/max/.codex/plugins/cache/my-codex/doc-watcher/0.2.0/skills/doc-alignment/scripts/check_planning_tree.py docs/todo
git diff --check -- README.md docs plugins/orchestration scripts codex-home
```

Checkpoint evidence：

```text
Not started.
```

## 阶段状态表

| Milestone | 状态 | Review gate | Checkpoint |
|---|---|---|---|
| M0 - Baseline And Contract Freeze | `Ready` | `Not Run` | `Not Run` |
| M1 - Runtime Selector Surface Discovery | `Not Started` | `Not Run` | `Not Run` |
| M2 - Empirical Custom-Agent Validation Matrix | `Not Started` | `Not Run` | `Not Run` |
| M3 - Runtime Contract Sync | `Not Started` | `Not Run` | `Not Run` |
| Close | `Not Started` | `Not Run` | `Not Run` |

## Close Gate

Close 前必须满足：

1. 所有 milestones 均为 `Done`。
2. 所有 review gates 均为 `Passed`。
3. 所有 checkpoint evidence 均已记录。
4. Runtime custom-agent selector 状态被明确标为 `Verified`、`Unavailable` 或 `Not Provable With Current Runtime`。
5. Current docs 不再留下 "custom-agent-first" 与 "runtime exact selection" 的歧义。
6. [docs/todo/README.md](README.md)、[README.md](../../README.md)、[docs/agents/agent-operating-model.md](../agents/agent-operating-model.md)、[docs/agents/subagent-roster.md](../agents/subagent-roster.md) 和 orchestration docs 均反映当前状态。
7. `python3 scripts/sync_codex_agents.py --check --prune --codex-home "${CODEX_HOME:-$HOME/.codex}"` 已记录实际结果。
8. `python3 scripts/check_my_codex.py` 已记录实际结果或明确 skip reason。
9. Markdown link check 和 `git diff --check` 已通过。
10. Future risks 明确记录：write-capable custom agents、advisor skill、project `.codex/agents/` dogfood 是否进入后续计划。

## 当前风险

1. Codex runtime selector surface may differ between CLI, Desktop, subagent tools, and account/model availability.
2. Assignment labels can look like custom-agent names but do not prove TOML loading.
3. Pinned model names may be unavailable in some accounts; fallback behavior must stay explicit.
4. Runtime event output may omit enough metadata to prove exact agent type even when selector exists.
5. Current custom-agent TOML sync is personal-machine state and must remain non-destructive.

## Future Candidates

These require separate planning after this goal closes:

1. `impl_worker` and `test_runner` write-capable custom agents.
2. `$subagent-fit-check` explicit advisor skill.
3. Project-scoped `.codex/agents/` dogfood for this repository.
4. Automated runtime regression harness for subagent selection once a stable selector and evidence channel exist.

## 推荐 Goal Prompt

```text
请按照 docs/todo/subagent-runtime-selection-validation.md 执行 Subagent Runtime Selection Validation。

执行要求：

1. 使用 workflow:long-run-goal。
2. 阶段必须顺序执行：M0 -> M1 -> M2 -> M3 -> Close。
3. 每个阶段开始前把状态改为 In Progress，完成后记录代码、行为、测试、文档、回滚和剩余风险证据。
4. 不允许把 assignment label 或 generic subagent success 当作 exact custom-agent type evidence。
5. 如果 runtime selector 不存在或不可证明，更新 current docs 明确 partial coverage，而不是伪装成功。
6. Close 前必须运行并记录本 goal 指定的 link check、planning tree check、agent sync check、my-codex check 和 diff check。
```

## 参考

1. [Subagent roster](../agents/subagent-roster.md)
2. [Agent operating model](../agents/agent-operating-model.md)
3. [Closed Subagent Model Routing V1](archive/subagent-model-routing-v1.md)
4. [Orchestrate subagents skill](../../plugins/orchestration/skills/orchestrate-subagents/SKILL.md)
5. [Subagent recipes](../../plugins/orchestration/skills/orchestrate-subagents/references/subagent-recipes.md)
