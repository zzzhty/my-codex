# Long-Run Goal: Subagent Model Routing V1

Status: Closed

整体状态：Closed

当前轮次：Closed

目标 owner：`Max / my-codex agents`

目标路径：`docs/todo/archive/subagent-model-routing-v1.md`

Planning root：`docs`

Goal directory：`docs/todo`

## 目标摘要

本 goal 将 subagent model-routing 方案收口为 v1：先落地 read-only custom agents、全局 `$CODEX_HOME/agents/` 受控同步，以及 orchestration fallback。它把 `docs/todo/subagent-model-routing-notes.md` 中的开放设计收敛成可执行的阶段计划。

最终目标态：

1. `my-codex` 管理一组 M1 read-only custom agents：`code_mapper`、`reviewer`、`docs_researcher`。
2. custom-agent source of truth 位于 repo 内 `codex-home/agents/`，通过受控脚本同步到 `$CODEX_HOME/agents/`。
3. `$orchestrate-subagents` 仍是唯一 runtime orchestration contract；recipes 优先使用 custom agents，缺失时 fallback 到 built-in `explorer`、`default`、`worker`。
4. write-capable custom agents、全局 AGENTS auto-gate、自动 router 和隐式 delegation 不属于 M1。

## M1 Decision

M1 adopts read-only custom agents only.

Chosen scope:

- Add source-of-truth custom-agent TOML under `codex-home/agents/`.
- Sync those files into `$CODEX_HOME/agents/` with a managed, non-destructive sync script.
- Add only read-only roles in M1:
  - `code_mapper`
  - `reviewer`
  - `docs_researcher`
- Do not add write-capable custom agents in M1:
  - no `impl_worker`
  - no `test_runner`
- Keep `$orchestrate-subagents` as the runtime orchestration contract.
- Update orchestration recipes to prefer custom agents when available, and fall back to built-in `explorer`, `default`, and `worker` roles when unavailable.
- Do not add a global AGENTS.md auto-gate.
- Add an optional explicit `$subagent-fit-check` skill only if advisor behavior is needed after M1.

Rationale:

- Codex only spawns subagents when explicitly asked, so this is not an automatic router.
- Custom agents can pin `model`, `model_reasoning_effort`, and `sandbox_mode`, which is enough for role-based model routing.
- Read-only agents provide most of the context-pollution benefit with lower write-conflict risk.
- Write-capable agents need separate validation for disjoint ownership, rollback, conflict handling, and final parent integration.

## M0 执行前基线

当前事实：

1. [README.md](../../../README.md) currently points open custom-agent TOML and `$CODEX_HOME/agents/` sync design at the TODO area, and forbids adding `codex-home/agents/` or `scripts/sync_codex_agents.py` until the TODO records chosen design and validation evidence.
2. [docs/agents/agent-operating-model.md](../../agents/agent-operating-model.md) says `$orchestrate-subagents` is the current runtime contract, with unresolved custom-agent routing decisions kept in TODO.
3. [docs/todo/subagent-model-routing-notes.md](subagent-model-routing-notes.md) is the background design note and records the external `cast-subagents` reference, advisor-gate idea, work modes, and initial role sketches.
4. [plugins/orchestration/skills/orchestrate-subagents/SKILL.md](../../../plugins/orchestration/skills/orchestrate-subagents/SKILL.md) already defines bounded assignment, one-task-per-subagent, evidence, failure handling, and parent consolidation.
5. [plugins/orchestration/skills/orchestrate-subagents/references/subagent-recipes.md](../../../plugins/orchestration/skills/orchestrate-subagents/references/subagent-recipes.md) currently uses built-in roles and assignment labels, not custom-agent TOML names.
6. [requirements-tools.txt](../../../requirements-tools.txt) currently includes `PyYAML` only; agent TOML validation may need `tomli` fallback for Python before 3.11.

已读取的当前事实源：

1. Root `AGENTS.md` and repo-specific [docs/agents/agent-operating-model.md](../../agents/agent-operating-model.md).
2. Root [README.md](../../../README.md).
3. Current TODO index [docs/todo/README.md](../README.md).
4. Background design note [docs/todo/subagent-model-routing-notes.md](subagent-model-routing-notes.md).
5. Orchestration skill and recipe files under [plugins/orchestration/skills/orchestrate-subagents/](../../../plugins/orchestration/skills/orchestrate-subagents/).
6. GPT-Pro v1 proposal, consolidated into this goal document.

## Goal 执行合同

如果本计划被作为 long-running goal 执行，必须按以下合同推进：

1. 阶段必须顺序执行：`M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> Close`。
2. 每个阶段开始前必须把阶段状态改为 `In Progress`。
3. 每个阶段完成后必须记录代码证据、行为证据、测试证据、文档证据、回滚证据和剩余风险。
4. 每个阶段必须记录 checkpoint evidence。若项目使用 Git 且用户允许 checkpoint commit，使用 `subagent-model-routing-v1 M1: summary` 这类格式；否则记录文档修订、diff evidence 或明确写 `Not applicable: no checkpoint commit requested`。
5. 未满足当前阶段 review gate 时，不得进入下一阶段。
6. 失败必须停在失败点，记录 root cause、失败命令或路径、已知 breakpoint 和下一步诊断。
7. 不允许用 silent fallback、兼容假成功、alternate backend、隐藏 partial success、临时 alias 或修改假设来绕过 gate。
8. 任何涉及 `$CODEX_HOME`、agent sync target、Codex plugin cache、hook trust 或旧 runtime 状态的动作都必须有显式命令输出作为证据。
9. 如果执行中发现 sync schema、验证规则、回滚路径或阶段边界不够严谨，必须先更新本计划或相关 reusable strategy，再继续实现。
10. Close 只能在所有阶段 `Done`、所有 review gate `Passed`、active docs 同步、最终验证通过之后执行。

## 状态定义

| 状态 | 含义 |
|---|---|
| `Ready` | 设计与验收指标已明确，可以开始该阶段 |
| `Not Started` | 阶段尚未开始，且必须等待前置阶段完成 |
| `In Progress` | 当前阶段正在实现或验证 |
| `Blocked` | 当前阶段因明确失败或未决设计被阻塞 |
| `Done` | 阶段 review gate、验证和 checkpoint evidence 均已完成 |
| `Closed` | 整体计划关闭，并已从 active TODO 导航移除 |

## Owner Boundaries

### `workflow` plugin

`workflow` 继续负责 long-running goal 和 SOP。它不负责 subagent runtime orchestration、custom-agent sync 或 role selection。

### `orchestration` plugin

`orchestration:orchestrate-subagents` 继续负责 runtime delegation contract：assignment、ownership、evidence、failure handling 和 parent consolidation。

### custom-agent source

`codex-home/agents/` 是 M1 custom-agent source of truth。`$CODEX_HOME/agents/` 是 sync target，不应手工编辑 managed target 文件。

### parent agent

parent agent 继续负责规划、是否派生、写范围控制、最终整合、验证和用户结论。custom agents 不替代 parent judgment。

## Compatibility Surface

1. Built-in roles `explorer`、`default`、`worker` remain supported fallback roles.
2. M1 custom agents must not override built-in names: `default`、`worker`、`explorer`。
3. `$orchestrate-subagents` remains the explicit invocation path.
4. Existing recipes must continue to work when custom agents are unavailable.
5. `sync_codex_agents.py --check` must fail clearly when managed target files drift.

## 非目标 / Future 边界

本 goal 不处理：

1. M1 不新增 `impl_worker` 或 `test_runner` custom-agent TOML。
2. M1 不新增全局 AGENTS.md auto-gate。
3. M1 不把 Codex 变成自动 model router；subagents 仍需显式请求或显式 workflow 调用。
4. M1 不默认启用 write-capable custom agents；M2 需要独立 ownership、rollback、conflict handling 和 validation evidence。
5. M1 不修改外部 Codex cloud task model behavior。
6. M1 不修改 plugin cache、runtime logs、generated reports 或 `$CODEX_HOME` 状态来伪装成功。

## M1 Agent Roster

M1 includes read-only agents only.

| Agent | Work mode | Model | Reasoning | Sandbox | Fallback |
|---|---|---|---|---|---|
| `code_mapper` | read-only | `gpt-5.4-mini` | medium | read-only | `explorer as code-mapper` |
| `reviewer` | read-only | `gpt-5.5` | high | read-only | `default as implementation-reviewer` |
| `docs_researcher` | read-only | `gpt-5.4-mini` | medium | read-only | `default as docs-researcher` |

Deferred:

| Deferred agent | Reason |
|---|---|
| `impl_worker` | needs disjoint write ownership, rollback policy, conflict handling, and parent integration gate |
| `test_runner` | test execution can write caches, snapshots, coverage, temp files, or generated artifacts |

Safety policy:

1. M1 custom agents must use `sandbox_mode = "read-only"`.
2. M1 custom agents must not edit files, run destructive commands, or claim success without evidence.
3. If a pinned model is unavailable, fallback to the built-in recipe role instead of silently changing TOML.

## 目标结构

### Source and roster

1. Add `docs/agents/subagent-roster.md` as the current roster and model policy.
2. Add source TOML under `codex-home/agents/`.
3. Keep source names aligned with agent names: `code_mapper.toml`、`reviewer.toml`、`docs_researcher.toml`。

### Sync and validation

1. Add `scripts/sync_codex_agents.py`.
2. Integrate sync into `scripts/refresh_my_codex.py`.
3. Integrate sync check into `scripts/check_my_codex.py`.
4. Update `requirements-tools.txt` only if Python < 3.11 TOML fallback is needed.

### Orchestration integration

1. Update orchestration role selection to prefer M1 custom read-only agents.
2. Update recipes to show custom-agent-first assignments and built-in fallbacks.
3. Keep `worker` rules unchanged for implementation subtasks.

## 阶段计划

### M0 - Contract Review And Design Freeze

状态：`Done`

范围：

1. Freeze this v1 goal plan from the GPT-Pro decision proposal.
2. Update TODO index and background design note so this file is the active execution contract.
3. Do not implement custom-agent files, sync scripts, or orchestration recipe changes in M0.

Review gate：

1. This goal passes long-run-goal readiness check.
2. [docs/todo/README.md](../README.md) references this file as an active long-running goal.
3. [docs/todo/subagent-model-routing-notes.md](subagent-model-routing-notes.md) clearly points to this file as the v1 execution contract.

执行证据：

1. 代码证据：
   - Renamed the active execution proposal from `docs/todo/decision-v1.md` to `docs/todo/subagent-model-routing-v1.md`.
   - Renamed the background note from `docs/todo/subagent-model-selection.md` to `docs/todo/subagent-model-routing-notes.md`.
   - Updated [docs/todo/README.md](../README.md), [README.md](../../../README.md), and [docs/agents/agent-operating-model.md](../../agents/agent-operating-model.md) to point at this goal as the active v1 contract.
2. 行为证据：
   - M0 only reorganized and froze planning docs.
   - No custom-agent TOML, `codex-home/agents/`, sync script, orchestration recipe, plugin cache, or `$CODEX_HOME` runtime state was created or modified.
3. 测试证据：
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_goal_ready.py docs/todo/subagent-model-routing-v1.md` passed.
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_todo_index.py docs/todo/subagent-model-routing-v1.md docs/todo/README.md` passed.
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs` passed.
   - `python3 /Users/max/.codex/plugins/cache/my-codex/doc-watcher/0.2.0/skills/doc-alignment/scripts/check_planning_tree.py docs/todo` passed.
   - `git diff --check -- README.md docs/agents/agent-operating-model.md docs/todo/README.md docs/todo/subagent-model-selection.md` passed for tracked and deleted paths.
   - `rg -n '[[:blank:]]+$' docs/todo/subagent-model-routing-v1.md docs/todo/subagent-model-routing-notes.md` returned no matches for new Markdown files.
   - Fence-count checks passed for new Markdown files: `subagent-model-routing-v1.md` has 30 triple-fence lines; `subagent-model-routing-notes.md` has 58 triple-fence lines.
4. 文档证据：
   - [docs/todo/README.md](../README.md) indexes this file under active long-running goals.
   - [docs/todo/subagent-model-routing-notes.md](subagent-model-routing-notes.md) now labels itself as background and points to this file as the v1 execution contract.
   - Root and agent operating docs point custom-agent routing work at this long-running goal instead of the old TODO filename.
5. 回滚证据：
   - Revert the M0 documentation renames and pointer edits to restore the previous TODO pointers.
   - No runtime state exists to roll back because M0 did not write `$CODEX_HOME` or add sync-managed files.
6. 剩余风险：
   - M1-M5 remain unexecuted.
   - `codex-home/agents/`, custom-agent TOML, sync integration, orchestration recipe updates, and runtime validation do not exist yet.

推荐验证：

```bash
python3 plugins/workflow/skills/long-run-goal/scripts/check_goal_ready.py docs/todo/subagent-model-routing-v1.md
python3 plugins/workflow/skills/long-run-goal/scripts/check_todo_index.py docs/todo/subagent-model-routing-v1.md docs/todo/README.md
python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs
git diff --check -- docs/todo/subagent-model-routing-v1.md docs/todo/README.md docs/todo/subagent-model-routing-notes.md README.md docs/agents/agent-operating-model.md
```

Checkpoint evidence：

```text
Worktree documentation diff records the M0 contract freeze and TODO alignment.
Not applicable: no checkpoint commit requested in this turn.
```

### M1 - Roster And Read-Only Agent Source

状态：`Done`

范围：

1. Add `docs/agents/subagent-roster.md` with M1 roster, model policy, safety policy, fallback policy, and deferred write-capable agents.
2. Add `codex-home/agents/README.md`.
3. Add `codex-home/agents/code_mapper.toml`.
4. Add `codex-home/agents/reviewer.toml`.
5. Add `codex-home/agents/docs_researcher.toml`.
6. Do not write to `$CODEX_HOME/agents/` in this milestone.

Review gate：

1. Every M1 TOML has `name`、`description`、`developer_instructions`。
2. Every M1 TOML uses `sandbox_mode = "read-only"`。
3. No M1 TOML uses a built-in name: `default`、`worker`、`explorer`。
4. Roster documents built-in fallback for every M1 custom agent.
5. Roster documents `impl_worker` and `test_runner` as deferred.

执行证据：

1. 代码证据：
   - Added [docs/agents/subagent-roster.md](../../agents/subagent-roster.md).
   - Added [codex-home/agents/README.md](../../../codex-home/agents/README.md).
   - Added [codex-home/agents/code_mapper.toml](../../../codex-home/agents/code_mapper.toml).
   - Added [codex-home/agents/reviewer.toml](../../../codex-home/agents/reviewer.toml).
   - Added [codex-home/agents/docs_researcher.toml](../../../codex-home/agents/docs_researcher.toml).
2. 行为证据：
   - Source TOML now defines exactly the M1 read-only roster: `code_mapper`, `reviewer`, and `docs_researcher`.
   - M1 did not write to `$CODEX_HOME/agents/`.
   - Roster documents built-in fallback roles for each custom agent and keeps parent ownership explicit.
3. 测试证据：
   - `python3 -m py_compile scripts/*.py` passed.
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs` passed.
   - Inline `tomllib` validation passed: all M1 TOML files have `name`, `description`, `developer_instructions`, `sandbox_mode = "read-only"`, and no built-in names.
   - `rg -n '[[:blank:]]+$' docs/agents/subagent-roster.md codex-home/agents/README.md codex-home/agents/code_mapper.toml codex-home/agents/reviewer.toml codex-home/agents/docs_researcher.toml` returned no matches.
4. 文档证据：
   - [docs/agents/subagent-roster.md](../../agents/subagent-roster.md) documents model policy, safety policy, fallback policy, and deferred write-capable agents.
   - [codex-home/agents/README.md](../../../codex-home/agents/README.md) documents source-vs-target ownership and the M1 file list.
5. 回滚证据：
   - Remove `codex-home/agents/` and `docs/agents/subagent-roster.md`.
6. 剩余风险：
   - Sync and runtime validation remain unexecuted until later milestones.
   - Pinned model availability still needs runtime validation and fallback evidence.

推荐验证：

```bash
python3 -m py_compile scripts/*.py
python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs
git diff --check -- docs/agents/subagent-roster.md codex-home/agents
```

Checkpoint evidence：

```text
Worktree diff records M1 source files and roster docs.
Not applicable: no checkpoint commit requested in this turn.
```

### M2 - Managed Agent Sync Script

状态：`Done`

范围：

1. Add `scripts/sync_codex_agents.py`.
2. Validate source TOML before writing.
3. Require `name`、`description`、`developer_instructions`。
4. Reject built-in names: `default`、`worker`、`explorer`。
5. Reject non-read-only agents by default unless a future `--allow-write-capable` flag is explicitly used.
6. Add managed header to target files.
7. Refuse to overwrite unmanaged target files unless `--force`.
8. Support `--dry-run`、`--check`、`--prune`、`--codex-home`、`--target-root`。
9. Update `requirements-tools.txt` if `tomli` fallback is needed.

Review gate：

1. `--dry-run` prints planned writes without modifying target.
2. `--check` returns non-zero when target is missing or out of sync.
3. Managed files can be applied to a temp target root and then pass `--check`.
4. Unmanaged target files are not overwritten by default.
5. Write-capable source TOML is rejected by default.

执行证据：

1. 代码证据：
   - Added [scripts/sync_codex_agents.py](../../../scripts/sync_codex_agents.py).
   - No `requirements-tools.txt` change was needed because the active runtime is Python 3.13 with standard-library `tomllib`.
2. 行为证据：
   - The script validates source TOML, required fields, filename/name alignment, built-in-name rejection, and read-only sandbox policy.
   - The script writes managed headers to target files and refuses to overwrite unmanaged target files unless `--force` is used.
   - The script supports `--dry-run`, `--check`, `--prune`, `--codex-home`, `--target-root`, and `--allow-write-capable`.
3. 测试证据：
   - `python3 -m py_compile scripts/sync_codex_agents.py` passed.
   - `python3 scripts/sync_codex_agents.py --dry-run --target-root /tmp/my-codex-agents-test` printed planned writes and did not create the target directory.
   - Missing-target `--check` returned exit `1` and reported three missing managed files.
   - `python3 scripts/sync_codex_agents.py --target-root /tmp/my-codex-agents-test` wrote three managed target files.
   - `python3 scripts/sync_codex_agents.py --check --target-root /tmp/my-codex-agents-test` passed.
   - Unmanaged overwrite protection returned exit `1` for an unmanaged `code_mapper.toml`.
   - A write-capable temp source returned exit `1` unless `--allow-write-capable` is used.
   - `--check --prune` flagged an old managed target file; `--prune` removed that managed file and kept an unmanaged target file.
   - `git diff --check -- scripts/sync_codex_agents.py requirements-tools.txt codex-home/agents` passed.
   - `rg -n '[[:blank:]]+$' scripts/sync_codex_agents.py codex-home/agents/README.md codex-home/agents/code_mapper.toml codex-home/agents/reviewer.toml codex-home/agents/docs_researcher.toml` returned no matches.
4. 文档证据：
   - [codex-home/agents/README.md](../../../codex-home/agents/README.md) documents the source and managed target boundary.
   - [docs/agents/subagent-roster.md](../../agents/subagent-roster.md) names the sync target and managed source policy.
5. 回滚证据：
   - Remove `scripts/sync_codex_agents.py` and any requirement changes.
6. 剩余风险：
   - `$CODEX_HOME` sync integration remains unexecuted until M3.
   - Runtime availability of custom agents remains unvalidated until M5.

推荐验证：

```bash
python3 -m py_compile scripts/sync_codex_agents.py
python3 scripts/sync_codex_agents.py --dry-run --target-root /tmp/my-codex-agents-test
python3 scripts/sync_codex_agents.py --target-root /tmp/my-codex-agents-test
python3 scripts/sync_codex_agents.py --check --target-root /tmp/my-codex-agents-test
git diff --check -- scripts/sync_codex_agents.py requirements-tools.txt codex-home/agents
```

Checkpoint evidence：

```text
Worktree diff records M2 sync helper and managed-header behavior.
Not applicable: no checkpoint commit requested in this turn.
```

### M3 - Refresh And Check Integration

状态：`Done`

范围：

1. Update `scripts/refresh_my_codex.py` to run agent sync after plugin install and before hooks, unless `--skip-agents` is passed.
2. In refresh dry-run, call `sync_codex_agents.py --dry-run` so the sync plan is visible.
3. Update `scripts/check_my_codex.py` to run `sync_codex_agents.py --check`, unless `--skip-agents` is passed.
4. Update [README.md](../../../README.md) with M1 status, sync behavior, skip flags, and validation commands.

Review gate：

1. Refresh dry-run shows custom-agent sync actions.
2. Check reports whether `$CODEX_HOME/agents/` managed files are synced.
3. `--skip-agents` is available in both refresh and check flows.
4. README explains source path, target path, and write-capable deferral.

执行证据：

1. 代码证据：
   - Updated [scripts/refresh_my_codex.py](../../../scripts/refresh_my_codex.py) to run custom-agent sync after plugin install and before hook refresh.
   - Updated [scripts/check_my_codex.py](../../../scripts/check_my_codex.py) to run `sync_codex_agents.py --check`.
   - Updated [README.md](../../../README.md) with source path, target path, sync behavior, skip flag, and write-capable deferral.
2. 行为证据：
   - `scripts/refresh_my_codex.py --dry-run` executes the sync helper with `--dry-run` so planned agent writes are visible without modifying `$CODEX_HOME`.
   - `scripts/check_my_codex.py` reports missing or synced custom-agent state.
   - `--skip-agents` is available in both refresh and check flows.
   - Check helper now also accepts `--skip-plugins`, `--skip-hooks`, and `--skip-skill-watcher-doctor` for scoped validation.
3. 测试证据：
   - `python3 -m py_compile scripts/refresh_my_codex.py scripts/check_my_codex.py scripts/sync_codex_agents.py` passed.
   - `python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo` passed and printed planned writes for `code_mapper.toml`, `docs_researcher.toml`, and `reviewer.toml`.
   - `python3 scripts/check_my_codex.py --help` showed `--skip-agents`, `--skip-plugins`, `--skip-hooks`, and `--skip-skill-watcher-doctor`.
   - Temp `$CODEX_HOME` check returned exit `1` before agent sync and reported missing managed files.
   - After temp agent sync, the same check returned exit `0` with `custom agents are synced`.
   - `git diff --check -- scripts/refresh_my_codex.py scripts/check_my_codex.py README.md` passed.
   - `rg -n '[[:blank:]]+$' scripts/refresh_my_codex.py scripts/check_my_codex.py README.md` returned no matches.
4. 文档证据：
   - [README.md](../../../README.md) now documents that refresh syncs custom agents into `$CODEX_HOME/agents/` and that check verifies sync state without modifying target files.
5. 回滚证据：
   - Revert refresh/check/README changes; `scripts/sync_codex_agents.py` remains runnable manually if M2 is kept.
6. 剩余风险：
   - Orchestration recipes still reference built-in roles until M4.
   - Actual intended `$CODEX_HOME` sync remains deferred until M5.

推荐验证：

```bash
python3 -m py_compile scripts/refresh_my_codex.py scripts/check_my_codex.py scripts/sync_codex_agents.py
python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo
python3 scripts/check_my_codex.py --skip-plugins --skip-hooks --skip-skill-watcher-doctor
git diff --check -- scripts/refresh_my_codex.py scripts/check_my_codex.py README.md
```

Checkpoint evidence：

```text
Worktree diff records refresh/check integration and README behavior updates.
Not applicable: no checkpoint commit requested in this turn.
```

### M4 - Orchestration Custom-Agent Preference And Fallback

状态：`Done`

范围：

1. Update [plugins/orchestration/skills/orchestrate-subagents/SKILL.md](../../../plugins/orchestration/skills/orchestrate-subagents/SKILL.md) role selection to prefer M1 custom read-only agents when available.
2. Update [plugins/orchestration/skills/orchestrate-subagents/references/subagent-recipes.md](../../../plugins/orchestration/skills/orchestrate-subagents/references/subagent-recipes.md) suggested agents to show custom-agent-first assignments and built-in fallbacks.
3. Keep built-in fallback behavior explicit for every recipe.
4. Keep `worker` rules unchanged for implementation subtasks.
5. Do not add `$subagent-fit-check` in M4 unless this goal is explicitly amended.

Review gate：

1. Role selection says not to assume custom agents exist.
2. Recipes include fallback for each custom-agent-first suggestion.
3. Recipes do not introduce write-capable custom-agent names.
4. Failure handling still treats unavailable roles as partial coverage or blocker.

执行证据：

1. 代码证据：
   - Updated [plugins/orchestration/skills/orchestrate-subagents/SKILL.md](../../../plugins/orchestration/skills/orchestrate-subagents/SKILL.md) role selection to prefer M1 read-only custom agents when available.
   - Updated [plugins/orchestration/skills/orchestrate-subagents/references/subagent-recipes.md](../../../plugins/orchestration/skills/orchestrate-subagents/references/subagent-recipes.md) with custom-agent-first suggestions and built-in fallbacks.
2. 行为证据：
   - Role selection explicitly says not to assume custom agents are installed in every session.
   - Fallbacks are listed for `code_mapper`, `reviewer`, and `docs_researcher`.
   - Built-in `worker` remains the only implementation role in recipes; no write-capable custom-agent names were introduced in recipes.
3. 测试证据：
   - `${MY_CODEX_PYTHON:-/Users/max/.codex/venvs/my-codex/bin/python} ${PLUGIN_VALIDATOR:-/Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py} /Users/max/Projects/my-codex/plugins/orchestration` passed.
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py plugins/orchestration` passed.
   - `git diff --check -- plugins/orchestration/skills/orchestrate-subagents` passed.
   - `rg -n "impl_worker|test_runner" plugins/orchestration/skills/orchestrate-subagents/references/subagent-recipes.md` returned no matches.
   - `rg -n '[[:blank:]]+$' plugins/orchestration/skills/orchestrate-subagents/SKILL.md plugins/orchestration/skills/orchestrate-subagents/references/subagent-recipes.md` returned no matches.
4. 文档证据：
   - Recipes now show custom-agent-first assignments and fallback role names in the suggested subagents and parent prompt skeletons.
5. 回滚证据：
   - Revert orchestration skill and recipe edits to built-in role suggestions.
6. 剩余风险：
   - Manual Codex runtime validation remains for M5.

推荐验证：

```bash
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/orchestration"
python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py plugins/orchestration
git diff --check -- plugins/orchestration/skills/orchestrate-subagents
```

Checkpoint evidence：

```text
Worktree diff records M4 orchestration role-selection and recipe updates.
Not applicable: no checkpoint commit requested in this turn.
```

### M5 - Runtime Validation And Current Docs Closeout

状态：`Done`

范围：

1. Run agent sync against the intended `$CODEX_HOME`.
2. Run full local check unless explicitly skipped with documented reason.
3. Manually validate Codex can spawn M1 custom agents or clearly record fallback behavior.
4. Record validation evidence in this goal.
5. Update current docs and TODO index if the goal status changes.

Review gate：

1. `sync_codex_agents.py --check` passes against the intended `$CODEX_HOME`.
2. `scripts/check_my_codex.py` passes, or every skipped check has a concrete reason.
3. Manual Codex validation records whether `code_mapper`、`reviewer`、`docs_researcher` were available.
4. Fallback behavior is tested or explicitly marked untested with reason.
5. Any sandbox/read-only limitation observed during validation is recorded.

执行证据：

1. 代码证据：
   - Synced source TOML from [codex-home/agents/](../../../codex-home/agents/) into `/Users/max/.codex/agents/`.
   - Strengthened M5-discovered stale-agent handling: [scripts/refresh_my_codex.py](../../../scripts/refresh_my_codex.py) now runs sync with `--prune`, and [scripts/check_my_codex.py](../../../scripts/check_my_codex.py) now runs sync check with `--check --prune`.
   - Tightened managed-target recognition in [scripts/sync_codex_agents.py](../../../scripts/sync_codex_agents.py) to require the full generated header shape instead of a loose marker substring.
2. 行为证据：
   - `/Users/max/.codex/agents/` now contains managed `code_mapper.toml`, `docs_researcher.toml`, and `reviewer.toml`.
   - `scripts/check_my_codex.py` passed after agent sync, plugin validation, hook validation, and Skill Watcher doctor.
   - `scripts/refresh_my_codex.py --skip-bootstrap` refreshed the local marketplace cache from this dirty checkout, reinstalled all selected plugins, kept custom agents up to date, refreshed Skill Watcher hooks, and ran doctor.
   - Runtime validation spawned three read-only subagent threads with the requested assignment labels and waited for all of them.
   - Runtime role coverage is partial: the current `multi_agent_v1.spawn_agent` API did not expose a custom-agent selector, so the run verified generic subagent execution with requested labels and could not prove the loaded agent type was exactly `code_mapper`, `reviewer`, or `docs_researcher`.
3. 测试证据：
   - `python3 scripts/sync_codex_agents.py --codex-home "${CODEX_HOME:-$HOME/.codex}"` wrote three managed target files.
   - `python3 scripts/sync_codex_agents.py --check --prune --codex-home "${CODEX_HOME:-$HOME/.codex}"` passed.
   - `python3 scripts/check_my_codex.py` passed with `0 warning(s)` before and after plugin refresh.
   - `codex -a never exec --json -C /Users/max/Projects/my-codex -s read-only --output-last-message /tmp/my-codex-agent-runtime-validation.md ...` completed with exit `0`.
   - Runtime validation thread `019ea321-8019-7e21-a84a-835de034e9a4` spawned and closed three subagent threads: `019ea322-352c-7e21-a9b4-7bed2ab9e0f8`, `019ea322-576f-72b1-8c78-a395e66f828f`, and `019ea322-7cc3-7ae3-8645-19bf2acacbcc`.
   - `agent-source-mapper` completed with no blockers and mapped source, sync script, orchestration docs, and cache state.
   - `agent-risk-reviewer` completed and reported a medium stale-managed-agent risk; the risk was fixed by default `--prune` integration and stricter managed header detection.
   - `codex-docs-verifier` completed and verified `name`, `description`, `developer_instructions`, `model`, `model_reasoning_effort`, and `sandbox_mode` against official Codex documentation.
   - Temp stale-managed-agent test returned exit `1` for `--check --prune`, then `--prune` removed the stale managed file and left expected files intact.
   - `python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo` now prints `sync_codex_agents.py --codex-home /Users/max/.codex --prune --dry-run`.
   - `rg -n "code_mapper|docs_researcher|reviewer|Do not assume custom" /Users/max/.codex/plugins/cache/my-codex/orchestration/0.1.0/...` confirmed the installed orchestration cache contains the custom-agent-first guidance.
4. 文档证据：
   - Runtime docs verifier used official OpenAI Codex docs and found the TOML fields currently used here are documented for custom agents or Codex config.
   - Current docs were prepared for close: [README.md](../../../README.md), [docs/agents/agent-operating-model.md](../../agents/agent-operating-model.md), [docs/agents/subagent-roster.md](../../agents/subagent-roster.md), and [docs/todo/README.md](../README.md) now describe the landed M1 state instead of an open TODO.
5. 回滚证据：
   - Remove managed files from `$CODEX_HOME/agents/` only when they carry the managed marker; otherwise stop and report blocker.
   - Revert repo changes to remove source TOML, sync integration, and orchestration recipe updates if the feature must be backed out.
6. 剩余风险：
   - The current runtime spawn API did not expose a role/custom-agent selector in `codex exec`, so exact custom-agent type selection remains partial runtime coverage.
   - `codex doctor` failed only on non-interactive `TERM=dumb`; `scripts/check_my_codex.py` passed the goal's local closure checks.
   - Write-capable agents and advisor skill remain Future unless separately planned.

推荐验证：

```bash
python3 scripts/sync_codex_agents.py --codex-home "${CODEX_HOME:-$HOME/.codex}"
python3 scripts/sync_codex_agents.py --check --codex-home "${CODEX_HOME:-$HOME/.codex}"
python3 scripts/check_my_codex.py
python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs
git diff --check -- README.md docs agents plugins scripts codex-home requirements-tools.txt
```

Manual Codex validation prompt:

```text
Use $orchestrate-subagents.

Task: Validate the my-codex custom agent setup without editing files.

Spawn bounded read-only subagents:
- code_mapper as agent-source-mapper: map codex-home/agents, scripts/sync_codex_agents.py, and the orchestration skill references only.
- reviewer as agent-risk-reviewer: review correctness and safety risks in the custom agent sync design only.
- docs_researcher as codex-docs-verifier: verify whether the custom agent TOML fields used here match Codex documentation.

Boundaries:
- Do not edit files.
- Each subagent has one task only.
- Wait for all selected subagents.
- Report partial coverage if a custom agent is unavailable.
```

Checkpoint evidence：

```text
Worktree diff and runtime evidence record M5 sync, refresh, full check, subagent runtime validation, and stale-managed-agent fix.
Not applicable: no checkpoint commit requested in this turn.
```

## 阶段状态表

| Milestone | 状态 | Review gate | Checkpoint |
|---|---|---|---|
| M0 - Contract Review And Design Freeze | `Done` | `Passed` | `Done` |
| M1 - Roster And Read-Only Agent Source | `Done` | `Passed` | `Done` |
| M2 - Managed Agent Sync Script | `Done` | `Passed` | `Done` |
| M3 - Refresh And Check Integration | `Done` | `Passed` | `Done` |
| M4 - Orchestration Custom-Agent Preference And Fallback | `Done` | `Passed` | `Done` |
| M5 - Runtime Validation And Current Docs Closeout | `Done` | `Passed` | `Done` |
| Close | `Closed` | `Passed` | `Done` |

## Close Gate

Close 前必须满足：

1. 所有 milestones 均为 `Done`。
2. 所有 review gates 均为 `Passed`。
3. 所有 checkpoint evidence 均已记录。
4. [docs/todo/README.md](../README.md)、[README.md](../../../README.md)、[docs/agents/agent-operating-model.md](../../agents/agent-operating-model.md) 和 orchestration docs 均反映当前状态。
5. `python3 scripts/sync_codex_agents.py --check --codex-home "${CODEX_HOME:-$HOME/.codex}"` 已记录实际结果。
6. `python3 scripts/check_my_codex.py` 已记录实际结果或明确 skip reason。
7. `python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs` 通过。
8. `git diff --check -- changed paths` 通过。
9. Future risks 明确记录：write-capable custom agents、advisor skill、project `.codex/agents/` dogfood 是否进入后续计划。
10. Close checkpoint evidence 已记录。

Close 执行证据：

1. 代码证据：
   - Moved the closed goal to [docs/todo/archive/subagent-model-routing-v1.md](subagent-model-routing-v1.md).
   - Moved the background design note to [docs/todo/archive/subagent-model-routing-notes.md](subagent-model-routing-notes.md).
   - Updated [docs/todo/README.md](../README.md), [docs/todo/archive/README.md](README.md), [README.md](../../../README.md), [docs/agents/agent-operating-model.md](../../agents/agent-operating-model.md), [docs/agents/subagent-roster.md](../../agents/subagent-roster.md), and [plugins/orchestration/README.md](../../../plugins/orchestration/README.md).
2. 行为证据：
   - Active TODO navigation now has no open design notes or active long-running goals.
   - Archive navigation records the closed v1 goal and historical routing notes.
   - Current docs point to the landed roster and sync commands rather than the old open TODO.
3. 测试证据：
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs` passed.
   - `python3 /Users/max/.codex/plugins/cache/my-codex/doc-watcher/0.2.0/skills/doc-alignment/scripts/check_planning_tree.py docs/todo` passed.
   - `python3 scripts/sync_codex_agents.py --check --prune --codex-home "${CODEX_HOME:-$HOME/.codex}"` passed.
   - `python3 scripts/check_my_codex.py` passed with `0 warning(s)`.
   - `${MY_CODEX_PYTHON:-/Users/max/.codex/venvs/my-codex/bin/python} ${PLUGIN_VALIDATOR:-/Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py} /Users/max/Projects/my-codex/plugins/orchestration` passed.
   - `git diff --check -- README.md docs docs/todo docs/agents plugins/orchestration scripts codex-home requirements-tools.txt` passed.
   - `rg -n '[[:blank:]]+$' README.md docs plugins/orchestration scripts codex-home --glob '*.md' --glob '*.py' --glob '*.toml'` returned no matches.
   - Active-doc stale-path scan found old `subagent-model-selection` / active `subagent-model-routing-*` path references only inside this archived historical file.
4. 文档证据：
   - Current docs, archive index, root README, agent operating model, roster, and orchestration README reflect the closed v1 state.
5. 回滚证据：
   - Revert repo changes and remove only managed `$CODEX_HOME/agents/` target files carrying the managed marker.
6. 剩余风险：
   - Future work remains explicit: write-capable custom agents, advisor skill, project-scoped `.codex/agents/` dogfood, and more rigorous runtime tests for role-selection coverage.

Checkpoint evidence：

```text
Worktree diff records close/archive navigation and current-doc synchronization.
Not applicable: no checkpoint commit requested in this turn.
```

## 当前风险

1. Custom-agent TOML is loaded as a config layer; unsupported or evolving Codex surface may require plan adjustment before implementation.
2. `sandbox_mode = "read-only"` is a default, not a complete safety guarantee; live parent runtime overrides can still matter.
3. Global `$CODEX_HOME/agents/` sync is personal-machine state and must be managed non-destructively.
4. Pinned model names may be unavailable in some accounts; fallback behavior must be explicit.
5. Recipes may become noisy if every task prefers custom roles without a fit check; advisor behavior remains optional.

## Future Candidates

These require separate planning after M1 closes:

1. `impl_worker` and `test_runner` write-capable custom agents.
2. `$subagent-fit-check` explicit advisor skill.
3. Project-scoped `.codex/agents/` dogfood for this repository.
4. More rigorous runtime tests for concurrent workers and write-scope overlap.

## 推荐 Goal Prompt

```text
请按照 docs/todo/subagent-model-routing-v1.md 执行 Subagent Model Routing V1。

执行要求：
1. 阶段必须顺序执行：M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> Close。
2. 每个阶段开始前把该阶段状态改为 In Progress，完成后记录代码证据、行为证据、测试证据、文档证据、回滚证据和剩余风险。
3. 每个阶段都必须有 checkpoint evidence；若项目使用 Git 且用户允许阶段性提交，使用 `subagent-model-routing-v1 M1: summary` 格式。
4. 失败时停在失败点，报告 root cause、失败命令或路径、已知 breakpoint 和下一步诊断。
5. 不允许使用 fallback、兼容假成功、alternate backend、部分成功包装、隐藏错误或 silent degradation 来绕过 gate。
6. M1 只允许 read-only custom agents：code_mapper、reviewer、docs_researcher。
7. Close 前必须运行并记录本 goal 指定的 link check、diff check、agent sync check 和 my-codex check。
```

## 相关文档

1. [Subagent model routing notes](subagent-model-routing-notes.md)
2. [Agent operating model](../../agents/agent-operating-model.md)
3. [Root README](../../../README.md)
4. [Orchestrate subagents skill](../../../plugins/orchestration/skills/orchestrate-subagents/SKILL.md)
5. [Subagent recipes](../../../plugins/orchestration/skills/orchestrate-subagents/references/subagent-recipes.md)
