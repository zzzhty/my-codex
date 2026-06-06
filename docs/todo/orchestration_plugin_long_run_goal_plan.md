# Orchestration Plugin Long Run Goal Plan

整体状态：`In Progress`

Status: `In Progress`

## Goal 摘要

目标名称：`Add orchestration plugin to my-codex`

目标描述：

1. 在 `my-codex` marketplace 中新增 `orchestration` plugin，作为 Codex-facing orchestration workflow 的分发单元。
2. MVP 交付一个显式调用的 `$orchestrate-subagents` skill，让复杂 review、debugging、migration planning、impact analysis、test discovery 和 multi-file planning 能稳定地拆分、派发、等待并汇总 subagent 结果。
3. 本 goal 不引入外部 orchestration runtime，不把 `zzzhty/orchestration` 仓库作为依赖，不实现 control-plane、worker registry、durable assignment state、hooks、MCP server 或自动修改用户级 Codex 配置。

目标状态：`In Progress`

目标 owner：`my-codex / local Codex configuration owner`

目标路径：`docs/todo/orchestration_plugin_long_run_goal_plan.md`

Planning root：`docs/`

Goal directory：`docs/todo/`

## M0 执行前基线

M0 设计冻结时的当前基线：

1. `README.md` 定义本仓库是本地 Codex marketplace，当前已发布 `skill-watcher`、`doc-watcher`、`personal-skills` 和 `mattpocock-skills`。
2. `AGENTS.md` 已有 delegation policy 和 subagent failure handling，但它是全局原则，不应承载完整 orchestration prompt。
3. `docs/agents/agent-operating-model.md` 要求长期或重复工作落在可检查的 repo 文件、skill、automation memory、report 或 TODO 中。
4. `.agents/plugins/marketplace.json` 当前使用 local plugin entries，每个 plugin 指向 `./plugins/插件名` 形态。
5. `scripts/refresh_my_codex.py` 用 `PLUGIN_NAMES` 定义默认 refresh/install plugin 集合，并支持 `--plugin` 选择单个 plugin。
6. `scripts/check_my_codex.py` 复用 `PLUGIN_NAMES`，并检查 marketplace file、tooling Python、`codex plugin list`、plugin cache、hook config、plugin validator 和 Skill Watcher doctor。
7. 现有 plugin manifest 位于 `plugins/插件名/.codex-plugin/plugin.json`，并以 `"skills": "./skills/"` 指向 bundled skills。
8. `plugins/personal-skills/skills/long-run-goal/templates/long_run_goal_template.md` 是本计划格式的本地模板。
9. 当前可调用 subagent 工具暴露的 agent roles 是 `default`、`explorer`、`worker`；本 MVP 不能假设自定义 TOML agent 名称一定能作为 runtime `agent_type` 直接调用。
10. 本地 `$CODEX_HOME/agents/` 目录当前未作为本仓库 source of truth 存在；写入用户级 agent 配置属于独立 mutation 边界。

已读取的当前事实源：

1. `AGENTS.md`
2. `README.md`
3. `docs/agents/agent-operating-model.md`
4. `.agents/plugins/marketplace.json`
5. `scripts/refresh_my_codex.py`
6. `scripts/check_my_codex.py`
7. `plugins/*/.codex-plugin/plugin.json`
8. `plugins/personal-skills/skills/long-run-goal/SKILL.md`
9. `plugins/personal-skills/skills/long-run-goal/templates/long_run_goal_template.md`
10. `plugins/doc-watcher/skills/doc-alignment/SKILL.md`
11. `/Users/max/.codex/vendor_imports/skills/skills/.curated/migrate-to-codex/references/differences.md`

本地化可行性结论：

1. 目标 plugin id 冻结为 `orchestration`。旧 GPT 计划中的 `orchestration-codex` 是被替换的旧名，不再作为目标 plugin name、目录名、manifest name、install selector 或 checkpoint prefix 使用。
2. 目标目录应为 `plugins/orchestration/`，marketplace selector 应为 `orchestration@my-codex`。
3. 已验证现有 refresh helper 能生成目标 selector：

```bash
python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo --plugin orchestration
```

结果：

```text
+ /bin/echo plugin add orchestration@my-codex
dry-run only; no changes written
```

4. GPT 计划中的 custom agent TOML sync 不适合作为 MVP 默认范围。原因是本地可调用 subagent role 与自定义 TOML agent name 的运行时映射未在当前工具面中验证，并且默认同步 `$CODEX_HOME/agents/` 会写用户级状态。
5. MVP 应使用 explicit skill invocation 加 prompt-scoped subagent roles。`$orchestrate-subagents` 可以要求 parent agent 显式 spawn bounded subagents，并在 subagent 不可用或未被用户明确允许时停止或降级为清晰的 partial coverage report。
6. Custom agent TOML、`sync_codex_agents.py`、`[agents]` 全局配置片段和 `$CODEX_HOME/agents/` 写入只进入 Future gate，除非后续 milestone 先验证当前 Codex surface 的真实支持边界。

本次计划对齐验证证据：

1. `python3 plugins/personal-skills/skills/long-run-goal/scripts/check_goal_ready.py docs/todo/orchestration_plugin_long_run_goal_plan.md` 通过，输出 `goal readiness checks OK`。
2. `python3 plugins/doc-watcher/skills/doc-alignment/scripts/check_planning_tree.py docs/todo` 通过，输出 `planning tree OK (2 active md, 0 archive md, 1 index md)`。
3. `python3 plugins/personal-skills/skills/long-run-goal/scripts/check_md_links.py docs/todo` 通过，输出 `markdown relative links OK`。
4. `python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo --plugin orchestration` 通过，输出 `plugin add orchestration@my-codex`。
5. 未跟踪 Markdown 文件通过 `git diff --check --no-index` 补充检查；普通 `git diff --check -- docs/todo` 对未跟踪目录不展示 diff。
6. 已扫描 GPT 粘贴说明、source citation residue 和四反引号围栏残留；未发现实际残留。
7. 旧名 audit 只剩本文件中的 rejected-name 说明和审计命令示例；目标 install、manifest、marketplace、script 和 current docs 语义均使用 `orchestration`。

## Goal 执行合同

如果本计划被作为 long-running goal 执行，必须按以下合同推进：

1. 阶段必须顺序执行：`M0 -> M1 -> M2 -> M3 -> M4 -> Close`。
2. 每个阶段开始前必须把该阶段状态改为 `In Progress`。
3. 每个阶段完成后必须记录 review 结论、运行命令、通过证据、失败断点和未解决风险。
4. 每个阶段必须有 checkpoint evidence。若项目使用 Git checkpoint，优先使用 `orchestration M1: summary` 这类格式，或使用本 repo 既有 commit 约定。
5. 未满足当前阶段 Review gate 时，不得进入下一阶段。
6. 任何阶段失败必须停在失败点，记录 root cause、失败命令、文件路径、已知 breakpoint 和下一步修复建议。
7. 不允许用 silent fallback、兼容假成功、部分成功包装、alternate backend、隐藏错误或 silent degradation 来绕过 gate。
8. 不允许把 legacy 或 deprecated surface 重新包装成当前产品语义，除非本 goal 明确要求并完成文档更新。
9. 若执行中发现 gate、验证规则、回滚路径、阶段边界或 strategy 不够严谨，必须先暂停实现，记录暴露该问题的证据，更新本计划合同，再完成相关验证后回到原阶段继续。
10. 若上下文压缩、中断或用户新请求改变任务方向，必须先按最新请求重新确认是否继续本 goal。
11. Close 只能在所有阶段 `Done` 且完成标准全部有代码、测试和文档证据后执行。

## 状态定义

| 状态 | 含义 |
|---|---|
| `Draft` | 设计仍需补充，不能执行实现 |
| `Ready` | 设计与验收指标已明确，可以开始该阶段 |
| `Not Started` | 该阶段尚未开始，且必须等待前置阶段 Done |
| `In Progress` | 当前阶段正在实现或验证 |
| `Blocked` | 当前阶段因明确失败或未决设计被阻塞 |
| `Done` | 阶段 Review gate、验证和 checkpoint evidence 均已完成 |
| `Closed` | 整体计划完成并从 active TODO/goal 导航移除或归档 |

## 全局验收规则

每个阶段的验收至少包含：

1. 代码证据：列出新增、修改或删除的关键文件。
2. 行为证据：说明 Codex plugin、skill、refresh/check 或 docs 行为是否变化。
3. 测试证据：列出实际执行命令和结果；不能只写“应当通过”。
4. 文档证据：同步更新本文件状态表，并按需更新 active current docs。
5. 回滚证据：说明该阶段如何回滚；涉及用户级状态的阶段必须说明 source 和 target 的回滚边界。
6. 风险证据：列出仍保留的 compatibility、runtime、Codex surface 或 validation 风险。

默认验证命令：

```bash
git diff --check -- AGENTS.md README.md .agents/plugins/marketplace.json scripts plugins docs
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
```

按改动类型追加验证：

```bash
python3 -m json.tool plugins/orchestration/.codex-plugin/plugin.json >/dev/null
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/orchestration"
python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo --plugin orchestration
python3 scripts/check_my_codex.py --plugin orchestration --skip-doctor
```

说明：

1. `check_my_codex.py` 没有 dry-run；只有在 plugin 已安装或本 milestone 明确要求验证安装态时运行。
2. `--codex /bin/echo` 只用于 dry-run 验证 selector 生成，不证明真实 Codex CLI 安装成功。
3. Plugin validator 只能验证 plugin/skill 结构，不能证明 runtime subagent behavior；runtime behavior 必须由 M4 acceptance prompt 记录。

## 设计原则

1. `my-codex` 是 source of truth：plugin source、skill source、marketplace metadata、refresh/check scripts 和 current docs 都从本 repo 维护。
2. `orchestration` 是 thin plugin：MVP 只承载 reusable Codex orchestration workflow，不引入 control-plane runtime、worker scheduler、durable assignment state 或外部仓库依赖。
3. `$orchestrate-subagents` 是 explicit-only workflow。它不能依赖 `AGENTS.md` 的软提示自动触发 subagent。
4. Parent agent 负责拆分任务、选择 subagent roles、等待结果、汇总证据、做最终判断和执行集成。
5. Subagent failure 是 first-class failure。timeout、缺工具、权限不足、不完整发现和 blocker 都必须在 parent summary 中显式报告。
6. 默认不让 subagents 编辑同一批文件。实现类任务必须给每个 worker 明确 disjoint write scope；review/exploration/test discovery 默认 read-only。
7. MVP 不自动修改 `$CODEX_HOME/config.toml`，不默认写 `$CODEX_HOME/agents/`。
8. 当前 docs 只保留简短入口，完整 orchestration workflow 放在 `SKILL.md` 和 skill references 中。

## 目标结构

### Plugin 结构

目标新增：

```text
plugins/
  orchestration/
    .codex-plugin/
      plugin.json
    README.md
    skills/
      orchestrate-subagents/
        SKILL.md
        agents/
          openai.yaml
        references/
          subagent-recipes.md
```

目标 skill：

```text
$orchestrate-subagents
```

### Marketplace 和脚本结构

目标修改：

```text
.agents/plugins/marketplace.json
README.md
AGENTS.md
scripts/refresh_my_codex.py
scripts/check_my_codex.py
```

`scripts/check_my_codex.py` 当前已复用 `PLUGIN_NAMES`。如果新增 plugin 只需要进入默认 check 集合，优先通过更新 `PLUGIN_NAMES` 完成；只有发现 checker 无法表达新验证边界时再扩展 checker。

### Future custom-agent 结构

以下内容不属于 MVP，只有在 future gate 通过后才允许进入实现：

```text
codex-home/
  agents/
    orchestration-planner.toml
    code-explorer.toml
    implementation-reviewer.toml
    test-verifier.toml
    failure-triager.toml
    api-schema-inspector.toml
scripts/
  sync_codex_agents.py
```

Future gate 必须先证明：

1. 当前 Codex surface 支持这些 custom agent TOML 的 source 和 target path。
2. 这些 custom agent 能被 parent agent 或 subagent runtime 明确选择。
3. 同步脚本默认 dry-run，默认 conflict-safe，不自动修改 `$CODEX_HOME/config.toml`。
4. `--apply` 只在用户明确同意时写 `$CODEX_HOME/agents/`，且内容冲突时先备份或失败。

## 非目标 / Future 边界

本 goal 不处理：

1. 不把 `zzzhty/orchestration` repo 合并进 `my-codex`。
2. 不新增 `plan-control-plane-assignments` skill。
3. 不实现 control-plane job/assignment state、worker registry、worker result ingestion 或 outbox channel。
4. 不增加 Codex hooks。
5. 不增加 MCP server。
6. 不自动编辑或 merge `$CODEX_HOME/config.toml`。
7. 不默认写 `$CODEX_HOME/agents/`。
8. 不要求 subagents 隐式自动触发；MVP 成功标准是显式 `$orchestrate-subagents` 可复用、可验证。
9. 不支持 recursive subagent fan-out；MVP depth 固定为 parent -> direct subagents。
10. 不让 subagents 默认编辑同一批文件；parent agent 保持最终集成责任。

## 阶段计划

### M0 - Contract review / design freeze

状态：`Done`

范围：

1. 确认本 goal 使用 `orchestration` 作为唯一目标 plugin id。
2. 确认 MVP scope：`orchestration` plugin、`$orchestrate-subagents` skill、marketplace entry、refresh/check integration、README/AGENTS 短入口和 runtime acceptance。
3. 确认 custom agent TOML sync 不属于 MVP 默认范围。
4. 确认不与外部 orchestration repo 建立强依赖。
5. 确认 `AGENTS.md` 后续只保留短入口，不复制完整 orchestration workflow。

Review gate：

1. Goal plan 中没有未替换的模板占位符。
2. 旧 plugin name `orchestration-codex` 不作为目标语义保留。
3. MVP、Future、非目标边界已冻结。
4. 每个后续阶段都有明确文件范围、验证命令、回滚方式。
5. 本地 feasibility evidence 已记录。

执行证据：

1. 代码证据：
   - `docs/todo/orchestration_plugin_long_run_goal_plan.md`：冻结 `orchestration` plugin MVP 合同、MVP/Future 边界、验证 gate 和执行顺序。
   - `docs/todo/README.md`：将 active goal plan 纳入 TODO index。
2. 行为证据：
   - 本阶段无运行时行为变化；只确认 active goal contract 可执行。
3. 测试证据：
   - `python3 plugins/personal-skills/skills/long-run-goal/scripts/check_goal_ready.py docs/todo/orchestration_plugin_long_run_goal_plan.md` 通过，输出 `goal readiness checks OK`。
   - `python3 plugins/doc-watcher/skills/doc-alignment/scripts/check_planning_tree.py docs/todo` 通过，输出 `planning tree OK (2 active md, 0 archive md, 1 index md)`。
   - `python3 plugins/personal-skills/skills/long-run-goal/scripts/check_md_links.py docs/todo` 通过，输出 `markdown relative links OK`。
   - `python3 plugins/personal-skills/skills/long-run-goal/scripts/check_todo_index.py docs/todo/orchestration_plugin_long_run_goal_plan.md docs/todo/README.md` 通过，输出 `referenced by 1 index file(s)`。
   - `git diff --check -- docs/todo` 通过，无输出。
4. 文档证据：
   - 本文件成为 active goal contract；`docs/todo/README.md` 是 active TODO index。
5. 回滚证据：
   - 还原本文件和 `docs/todo/README.md` 即可回滚 M0。
6. 剩余风险：
   - 后续阶段可能发现 Codex plugin validator 或 runtime subagent behavior 与静态计划不同。

推荐验证：

```bash
python3 plugins/personal-skills/skills/long-run-goal/scripts/check_goal_ready.py docs/todo/orchestration_plugin_long_run_goal_plan.md
python3 plugins/doc-watcher/skills/doc-alignment/scripts/check_planning_tree.py docs/todo
git diff --check -- docs/todo
```

Checkpoint evidence：

```text
orchestration M0: goal contract frozen
```

### M1 - Add orchestration plugin skeleton and marketplace entry

状态：`Not Started`

范围：

1. 新增 plugin 目录：

```text
plugins/orchestration/
```

2. 新增 manifest：

```text
plugins/orchestration/.codex-plugin/plugin.json
```

3. 新增 plugin README：

```text
plugins/orchestration/README.md
```

4. 更新 marketplace：

```text
.agents/plugins/marketplace.json
```

5. 更新 `scripts/refresh_my_codex.py` 的 `PLUGIN_NAMES`，新增 `orchestration`。
6. 更新 root README 的 plugin list 和 install commands。

建议 `plugin.json` 最小内容：

```json
{
  "name": "orchestration",
  "version": "0.1.0",
  "description": "Codex orchestration skills for explicit subagent delegation and result consolidation.",
  "author": {
    "name": "Local developer"
  },
  "skills": "./skills/",
  "interface": {
    "displayName": "Orchestration",
    "shortDescription": "Explicit Codex subagent orchestration",
    "longDescription": "Reusable Codex skills for decomposing complex work, explicitly spawning focused subagents, waiting for results, and consolidating evidence, risks, tests, blockers, and next actions.",
    "developerName": "Local developer",
    "category": "Productivity",
    "capabilities": [
      "Interactive",
      "Write"
    ],
    "defaultPrompt": [
      "Use $orchestrate-subagents to review this branch against main.",
      "Use $orchestrate-subagents to decompose this task and spawn focused subagents."
    ]
  }
}
```

Review gate：

1. Plugin manifest validates as JSON.
2. `.agents/plugins/marketplace.json` includes `orchestration` with source path `./plugins/orchestration`.
3. README install examples include `codex plugin add orchestration@my-codex` for Unix and Windows.
4. `refresh_my_codex.py --dry-run --plugin orchestration` prints a plugin add command for `orchestration@my-codex`.
5. No runtime skill behavior is claimed before M2.

执行证据：

1. 代码证据：
   - 完成后填写 `plugins/orchestration/.codex-plugin/plugin.json`、`plugins/orchestration/README.md`、`.agents/plugins/marketplace.json`、`README.md`、`scripts/refresh_my_codex.py`。
2. 行为证据：
   - `orchestration` becomes installable through the existing `my-codex` marketplace flow after refresh.
3. 测试证据：
   - 完成后填写实际命令和结果。
4. 文档证据：
   - README plugin list and install snippets synchronized.
5. 回滚证据：
   - Remove plugin entry from marketplace and `PLUGIN_NAMES`, delete `plugins/orchestration/`, revert README edits.
6. 剩余风险：
   - Plugin validator may require real skill content, so full plugin validation belongs to M2.

推荐验证：

```bash
python3 -m json.tool plugins/orchestration/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo --plugin orchestration
git diff --check -- README.md .agents/plugins/marketplace.json scripts/refresh_my_codex.py plugins/orchestration
```

Checkpoint evidence：

```text
orchestration M1: plugin skeleton and marketplace integration
```

### M2 - Implement `$orchestrate-subagents` MVP skill

状态：`Not Started`

范围：

1. 新增:

```text
plugins/orchestration/skills/orchestrate-subagents/SKILL.md
plugins/orchestration/skills/orchestrate-subagents/agents/openai.yaml
plugins/orchestration/skills/orchestrate-subagents/references/subagent-recipes.md
```

2. Skill frontmatter 只包含 `name` 和 `description`。
3. Description 前置触发词：complex Codex tasks、explicitly spawn subagents、PR review、architecture review、debugging、failure triage、migration、refactor planning、impact analysis、test discovery、API/schema inspection、multi-file implementation planning。
4. Skill body 必须明确：只有用户显式调用 `$orchestrate-subagents` 或明确要求 subagents 时才 spawn。
5. Skill body 必须提供 parent workflow：triage task、choose bounded subagents、spawn selected subagents、wait for all results、reject incomplete reports、consolidate coverage and risks。
6. Skill body 必须包含 subagent prompt template，字段包括 input, ownership, expected output, stop condition, file/write boundary, evidence requirements, blocker reporting。
7. Skill body 必须包含 failure handling：subagent timeout、missing tools、partial coverage、conflicting results、unsafe overlap、unavailable subagent tool。
8. MVP recipes 优先使用当前可用 role 语义：`explorer` 做 codebase mapping，`worker` 做 bounded implementation only when user requested edits，`default` 做 review/triage/test planning when no narrower role is available。

建议 `SKILL.md` frontmatter：

```md
---
name: orchestrate-subagents
description: Use for complex Codex tasks that should explicitly spawn subagents, including PR review, architecture review, debugging, failure triage, migration, refactor planning, impact analysis, test discovery, API/schema inspection, and multi-file implementation planning.
---
```

Review gate：

1. `SKILL.md` has valid frontmatter with only `name` and `description`.
2. Skill explicitly says “spawn selected subagents” and “wait for all results”.
3. Skill forbids relying on implicit inheritance of parent context; prompts must carry the necessary instructions.
4. Skill includes parent consolidation format.
5. Skill treats subagent failures as first-class failures.
6. Plugin validator passes for `plugins/orchestration`.
7. No custom agent TOML sync is introduced in this milestone.

执行证据：

1. 代码证据：
   - 完成后填写 skill files and references.
2. 行为证据：
   - `$orchestrate-subagents` becomes available as an explicit skill after plugin install.
3. 测试证据：
   - 完成后填写实际命令和结果。
4. 文档证据：
   - `plugins/orchestration/README.md` documents usage examples and failure reporting.
5. 回滚证据：
   - Delete `skills/orchestrate-subagents/` and remove usage docs.
6. 剩余风险：
   - Static validation cannot prove runtime subagent behavior; M4 must run acceptance prompt.

推荐验证：

```bash
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/orchestration"
python3 - <<'PY'
from pathlib import Path
path = Path("plugins/orchestration/skills/orchestrate-subagents/SKILL.md")
text = path.read_text(encoding="utf-8")
required = [
    "name: orchestrate-subagents",
    "description:",
    "spawn",
    "wait",
    "consolidate",
    "failure",
]
for item in required:
    assert item.lower() in text.lower(), item
print("ok orchestrate-subagents skill contract")
PY
git diff --check -- plugins/orchestration
```

Checkpoint evidence：

```text
orchestration M2: orchestrate-subagents MVP skill implemented
```

### M3 - Integrate current docs and check scripts

状态：`Not Started`

范围：

1. Update `README.md` with:
   - plugin description
   - install command for `orchestration`
   - validation commands
   - example prompt
   - Future note for custom agents
2. Update `AGENTS.md` with a short pointer to `$orchestrate-subagents` without duplicating the full skill workflow.
3. Confirm `scripts/check_my_codex.py` covers `orchestration` through `PLUGIN_NAMES`.
4. Extend `scripts/check_my_codex.py` only if M1/M2 expose a real gap that cannot be covered by existing marketplace/plugin/cache/validator checks.
5. Do not add `sync_codex_agents.py` in this milestone.

Review gate：

1. README, AGENTS, marketplace, plugin README and skill docs use `orchestration` consistently.
2. Active docs do not instruct users to install `orchestration-codex`.
3. `AGENTS.md` remains a concise global principle file; full orchestration workflow remains in `SKILL.md`.
4. Check script behavior is verified or explicitly left unchanged because `PLUGIN_NAMES` is sufficient.
5. No user-level `$CODEX_HOME` mutation is introduced.

执行证据：

1. 代码证据：
   - 完成后填写 changed docs and scripts.
2. 行为证据：
   - Future sessions see the plugin in install/check docs and the short global delegation pointer.
3. 测试证据：
   - 完成后填写实际命令和结果。
4. 文档证据：
   - README, AGENTS and plugin README synchronized.
5. 回滚证据：
   - Revert README, AGENTS and script edits from this milestone.
6. 剩余风险：
   - Skill list truncation can still hide the skill in very large installations; explicit `$orchestrate-subagents` prompt remains the reliable path.

推荐验证：

```bash
rg --hidden -n "orchestration-codex|plugins/orchestration-codex|orchestration_codex" AGENTS.md README.md .agents plugins scripts docs --glob '!**/.git/**'
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
git diff --check -- AGENTS.md README.md scripts docs plugins .agents/plugins/marketplace.json
```

The `rg` command is an audit command, not a zero-output assertion. Any remaining hit must be explicitly historical, rejected-name, or compatibility text; install commands, manifests, marketplace entries, script defaults and current user-facing docs must use `orchestration`.

Checkpoint evidence：

```text
orchestration M3: current docs and checker integration completed
```

### M4 - End-to-end refresh/check and Codex acceptance

状态：`Not Started`

范围：

1. Run static validation.
2. Run plugin validation.
3. Run refresh dry-run.
4. Run real refresh/check only when the user permits local Codex state mutation.
5. Run one interactive Codex acceptance test using `$orchestrate-subagents`.
6. Record partial coverage clearly if subagent tooling is unavailable or policy blocks spawning.

Static validation:

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/orchestration/.codex-plugin/plugin.json >/dev/null
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/orchestration"
python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo --plugin orchestration
git diff --check -- AGENTS.md README.md .agents/plugins/marketplace.json scripts plugins docs
```

Optional apply:

```bash
python3 scripts/refresh_my_codex.py --plugin orchestration
python3 scripts/check_my_codex.py --plugin orchestration --skip-doctor
```

Codex acceptance prompt:

```text
Use $orchestrate-subagents.

Task: Review this branch against main.

Explicitly use bounded subagents where available:
- code mapping: identify affected files, symbols, call paths, and risky areas
- implementation review: find correctness, security, regression, and contract risks
- test verification: identify missing tests and validation gaps

Wait for all selected subagents. Then consolidate:
1. Subagent coverage
2. Blocking issues
3. Non-blocking risks
4. Missing tests
5. Evidence
6. Unresolved blockers
7. Recommended next action

Do not edit files.
```

Review gate：

1. Marketplace JSON passes.
2. Plugin JSON passes.
3. Plugin validator passes.
4. Refresh dry-run prints `orchestration@my-codex`.
5. If local state mutation is permitted, refresh/check commands pass and exact output is recorded.
6. Acceptance prompt shows Codex either spawns requested subagents and waits for results, or clearly reports why subagents are unavailable or blocked.
7. Final acceptance response includes subagent coverage table or explicit partial coverage report.

执行证据：

1. 代码证据：
   - 完成后填写 all changed files from M1-M3.
2. 行为证据：
   - `orchestration` can be installed from `my-codex`.
   - `$orchestrate-subagents` can be invoked explicitly.
3. 测试证据：
   - Record exact command outputs before marking M4 Done.
4. 文档证据：
   - README, AGENTS, plugin README, skill docs and this goal file synchronized.
5. 回滚证据：
   - Remove `orchestration` from marketplace and `PLUGIN_NAMES`.
   - Delete `plugins/orchestration/`.
   - Revert README/AGENTS/script/docs changes.
   - If refresh was applied, uninstall or disable the plugin through the normal Codex plugin workflow.
6. 剩余风险：
   - Interactive subagent behavior depends on installed Codex version, app/CLI surface, sandbox policy and user permissions.

推荐验证：

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/orchestration/.codex-plugin/plugin.json >/dev/null
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/orchestration"
python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo --plugin orchestration
git diff --check -- AGENTS.md README.md .agents/plugins/marketplace.json scripts plugins docs
```

Checkpoint evidence：

```text
orchestration M4: validation and Codex acceptance completed
```

## 阶段状态表

| 阶段 | 状态 | Review | Checkpoint |
|---|---|---|---|
| M0 Contract review / design freeze | Done | Passed | Done |
| M1 Plugin skeleton and marketplace entry | Not Started | Pending | Pending |
| M2 `$orchestrate-subagents` MVP skill | Not Started | Pending | Pending |
| M3 Current docs and checker integration | Not Started | Pending | Pending |
| M4 End-to-end refresh/check and Codex acceptance | Not Started | Pending | Pending |
| Close | Not Started | Pending | Pending |

## Close Gate

Close 前必须满足：

1. 所有阶段均为 `Done`。
2. 所有 Review gate 均为 `Passed`。
3. 所有 checkpoint evidence 均已完成并记录。
4. `orchestration` plugin 已出现在 `.agents/plugins/marketplace.json`。
5. `orchestration` 已加入 `PLUGIN_NAMES`。
6. README install / refresh / validation / plugin list 已同步。
7. `AGENTS.md` 只保留 `$orchestrate-subagents` 短入口，不复制完整 workflow。
8. `$orchestrate-subagents` skill 已通过 plugin validator。
9. `python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor --codex /bin/echo --plugin orchestration` 通过。
10. `git diff --check -- AGENTS.md README.md .agents/plugins/marketplace.json scripts plugins docs` 通过。
11. 至少完成一次 Codex acceptance prompt，或记录明确 blocker 与 partial coverage。
12. 未解决风险已记录，并明确是否进入 Future。

Close 执行证据：

1. 代码证据：
   - Close 时填写最终关键文件。
2. 行为证据：
   - Close 时填写最终行为结论。
3. 测试证据：
   - Close 时填写最终命令和结果。
4. 文档证据：
   - Close 时填写文档同步。
5. 回滚证据：
   - Close 时填写整体回滚策略。
6. 剩余风险：
   - Close 时填写 Future / residual risk。

Checkpoint evidence：

```text
orchestration close: plugin MVP and orchestrate-subagents skill completed
```

## 当前风险

1. `$orchestrate-subagents` 可以降低 prompt 重复成本，但不能让 Codex 在没有显式请求的情况下可靠自动 spawn subagents。
2. 当前 tool surface 和 custom agent TOML 的运行时映射未在本地验证；custom agents 不属于 MVP。
3. Plugin validator 能验证结构，但不能完全验证 runtime subagent behavior。
4. `check_my_codex.py` 会检查本地 Codex 安装态；在 plugin 尚未 refresh/install 前运行会失败，这是预期 gate，不是可绕过失败。
5. Skill description 过长时可能被 skills list budget 截断；关键 trigger words 必须放在 description 前部。
6. AGENTS 全局 delegation policy 与实际 tool policy 可能存在权限边界差异；skill 必须优先遵守当前 tool policy。

## Future Gate: Custom Agents And Sync

Custom agent source/sync 可以作为后续独立 goal 或本 goal Close 后的新 milestone 处理，但必须先满足：

1. 读取当前官方 Codex docs 或本地 Codex runtime docs，确认 custom agent source path、target path、required TOML keys、sandbox behavior 和 invocation semantics。
2. 本地建立只读 prototype，证明 custom agent names 能在当前 Codex surface 中被 parent agent 选择或触发。
3. 设计 `scripts/sync_codex_agents.py` 时必须默认 `--dry-run`，默认 fail on conflict，只有 `--apply --force` 才允许覆盖并写 backup。
4. `refresh_my_codex.py` 不得默认写 `$CODEX_HOME/agents/`；最多增加显式 `--sync-agents`。
5. `check_my_codex.py` 对 target sync 状态应可选检查，不能把用户级 agent state 和 plugin install state 混成不可恢复流程。

## 推荐 Goal Prompt

```text
请按照 docs/todo/orchestration_plugin_long_run_goal_plan.md 执行 Orchestration Plugin MVP。

执行要求：
1. 阶段必须顺序执行：M0 -> M1 -> M2 -> M3 -> M4 -> Close，不得跳过 gate。
2. 每个阶段开始前把该阶段状态改为 In Progress。
3. 每个阶段完成后记录代码证据、行为证据、测试证据、文档证据、回滚证据和剩余风险。
4. 每个阶段都必须有 checkpoint evidence；若使用 Git checkpoint，使用 orchestration M1: summary 这类格式或本 repo 现有约定。
5. 失败时停在失败点，报告 root cause、失败命令、文件路径、已知 breakpoint 和下一步修复建议。
6. 不允许使用 fallback、兼容假成功、alternate backend、部分成功包装、隐藏错误或 silent degradation 来绕过 gate。
7. 不要引入 zzzhty/orchestration repo 的强依赖；MVP 只完成 my-codex 内的 orchestration plugin、orchestrate-subagents skill、marketplace/refresh/check integration、README/AGENTS 当前文档同步和 runtime acceptance。
8. Custom agent TOML sync 不属于 MVP；除非先通过 Future Gate，不要新增 codex-home/agents 或 sync_codex_agents.py。
9. Close 前必须运行并记录本计划 Close Gate 中列出的验证命令和 Codex acceptance 结果。
```

## 相关文档

1. `README.md`
2. `AGENTS.md`
3. `docs/agents/agent-operating-model.md`
4. `.agents/plugins/marketplace.json`
5. `scripts/refresh_my_codex.py`
6. `scripts/check_my_codex.py`
7. `plugins/personal-skills/skills/long-run-goal/SKILL.md`
8. `plugins/personal-skills/skills/long-run-goal/templates/long_run_goal_template.md`
9. `plugins/doc-watcher/skills/doc-alignment/SKILL.md`
10. `plugins/orchestration/README.md`
11. `plugins/orchestration/skills/orchestrate-subagents/SKILL.md`
