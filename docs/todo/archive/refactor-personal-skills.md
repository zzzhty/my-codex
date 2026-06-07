# Long-Run Goal: Refactor `personal-skills` Into `workflow`

整体状态：`Closed`

目标 owner：`Max / my-codex agents`

目标路径：`docs/todo/archive/refactor-personal-skills.md`

Planning root：`docs`

Goal directory：`docs/todo`

## 目标摘要

本 goal 将当前 `personal-skills` 插件重构为面向可复用工作流的 `workflow` 插件，并把原先散落在脚本中的插件安装选择上移为明确、可审查的安装清单。

最终目标态：

1. `plugins/personal-skills` 重命名为 `plugins/workflow`，插件 manifest、marketplace、README、验证命令和 Skill Watcher 监控语义同步改为 `workflow`。
2. 现有 `long-run-goal` skill 保留，并以 `workflow:long-run-goal` 作为当前 skill id。
3. 新增 `workflow:sop` skill，用于沉淀触发条件、输入、步骤、输出、验证、停止条件和失败处理都明确的标准流程。
4. 新增 `.agents/plugins/install-manifest.json` 作为默认安装和检查清单；`scripts/refresh_my_codex.py`、`scripts/check_my_codex.py` 和平台 wrapper 通过该清单选择插件，而不是依赖脚本内硬编码 tuple。
5. 完成迁移后，默认安装状态只保留 `workflow@my-codex`，不长期保留 `personal-skills@my-codex` alias 插件。

本 goal 不直接执行安装迁移；涉及 `$CODEX_HOME`、Codex plugin cache、hook trust、旧插件删除的步骤必须在执行里程碑时用命令证据确认。

## M0 执行前基线

当前事实：

1. [README.md](../../../README.md) 当前列出 `personal-skills`，Unix/Windows 安装命令、手动 reinstall checklist、验证命令和 layout 也都指向 `plugins/personal-skills`。
2. [.agents/plugins/marketplace.json](../../../.agents/plugins/marketplace.json) 当前包含 `personal-skills` 条目，路径为 `./plugins/personal-skills`。
3. [plugins/workflow/.codex-plugin/plugin.json](../../../plugins/workflow/.codex-plugin/plugin.json) 在 M0 基线时位于 `plugins/personal-skills/.codex-plugin/plugin.json`，manifest 的 `name`、`displayName`、description 和 default prompt 都是 personal skills 语义。
4. [scripts/refresh_my_codex.py](../../../scripts/refresh_my_codex.py) 当前用 `PLUGIN_NAMES` tuple 作为默认安装列表。
5. [scripts/check_my_codex.py](../../../scripts/check_my_codex.py) 从 refresh helper 导入 `PLUGIN_NAMES`，用同一硬编码列表检查 marketplace、`codex plugin list`、cache manifests 和 plugin validator。
6. [plugins/skill-watcher/scripts/codex_hook_adapter.py](../../../plugins/skill-watcher/scripts/codex_hook_adapter.py) 当前默认监控 `personal-skills:long-run-goal`，alias 也绑定旧 plugin id。
7. [plugins/skill-watcher/README.md](../../../plugins/skill-watcher/README.md) 当前默认 monitored skills 列表包含 `personal-skills:long-run-goal`。
8. [plugins/skill-watcher/tests/test_skill_watcher.py](../../../plugins/skill-watcher/tests/test_skill_watcher.py) 会断言 `DEFAULT_MONITORED_SKILLS` 等于 `plugins/*/skills/*/SKILL.md` 推导出的 packaged skills。
9. [docs/todo/README.md](../README.md) 在本计划升级前写着没有 active long-running goal plans。

已运行的审查命令和断点：

```bash
python3 plugins/workflow/skills/long-run-goal/scripts/check_goal_ready.py docs/todo/refactor-personal-skills.md
```

结果：失败。旧计划含 SOP 模板占位符，缺少 M0 milestone、failure handling、reusable prompt，也没有 Ready/In Progress/Closed 状态。

```bash
python3 plugins/doc-watcher/skills/doc-alignment/scripts/check_planning_tree.py docs/todo
```

结果：失败。`docs/todo/refactor-personal-skills.md` 是 active planning 文件，但没有被 `docs/todo/README.md` 引用。

## Doc Alignment Review

### High

1. `docs/todo/README.md` 声明没有 active long-running goal plans，但 `docs/todo/refactor-personal-skills.md` 已存在并描述未完成迁移。下一步：把本文件加入 TODO index。
2. 旧计划是建议稿，不是可执行 long-run-goal。它包含未替换占位符，缺少阶段 gate、checkpoint evidence、失败断点、关闭规则和复用 prompt。下一步：升级为本文件的长期目标合同。

### Medium

1. 插件默认选择目前由脚本 tuple 驱动；rename 计划如果只替换 tuple，会继续留下隐藏 source of truth。下一步：新增 `.agents/plugins/install-manifest.json`，让 refresh/check 读取清单。
2. `personal-skills` 语义分布在 marketplace、README、plugin manifest、Skill Watcher 默认监控和测试中。下一步：按里程碑顺序替换，避免同时启用两个 `long-run-goal` provider。
3. Skill Watcher 的监控列表与 packaged skills 绑定，新增 `sop` 后必须同步 adapter、README 和测试，否则 attribution 会漂移。

### Low

1. 旧计划的 commit 拆分有价值，但不等于阶段 gate。下一步：把拆分转换为 M1-M5 的执行顺序和验证命令。
2. SOP skill 草案内容可复用，但不应以未替换模板状态留在 active goal 正文中。下一步：将 SOP 具体内容移入 M3 交付范围。

## Goal 执行合同

如果本计划被作为 long-running goal 执行，必须按以下合同推进：

1. 阶段必须顺序执行：`M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> Close`。
2. 每个阶段开始前必须把阶段状态改为 `In Progress`。
3. 每个阶段完成后必须记录代码证据、行为证据、测试证据、文档证据、回滚证据和剩余风险。
4. 每个阶段必须记录 checkpoint evidence。若项目使用 Git 且用户允许 checkpoint commit，使用 `refactor-personal-skills M1: summary` 这类格式；否则记录文档修订、diff evidence 或明确写 `Not applicable: no checkpoint commit requested`。
5. 未满足当前阶段 review gate 时，不得进入下一阶段。
6. 失败必须停在失败点，记录 root cause、失败命令或路径、已知 breakpoint 和下一步诊断。
7. 不允许用 silent fallback、兼容假成功、alternate backend、隐藏 partial success、临时 alias 插件或修改假设来绕过 gate。
8. 任何涉及 `$CODEX_HOME`、plugin cache、hook trust 或旧插件删除的动作都必须有显式命令输出作为证据。
9. 如果执行中发现 manifest schema、验证规则、回滚路径或阶段边界不够严谨，必须先更新本计划或相关 reusable strategy，再继续实现。
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

`workflow` 是可复用 Codex 工作流技能包，负责 long-running goal、SOP 和未来稳定工作流 skill。它不负责监控运行时状态、后台 automation 记忆或多 agent 并行调度。

### `long-run-goal`

`workflow:long-run-goal` 负责创建、升级、执行、恢复、演进和关闭需要阶段、review gate、checkpoint evidence、验证证据和 close/archive hygiene 的长期目标。

### `sop`

`workflow:sop` 负责已经稳定或可以明确化的标准流程。适用条件是触发、输入、步骤、输出、验证、停止条件和失败处理都清楚。探索性计划、设计冻结和多阶段实施仍使用 `long-run-goal`。

### Plugin availability vs install selection

`.agents/plugins/marketplace.json` 是 marketplace availability catalog，表示有哪些插件可以安装。

`.agents/plugins/install-manifest.json` 是默认安装和检查清单，表示 refresh/check 默认选择哪些插件、以什么顺序安装、哪些插件参与 final check。脚本不得再把默认插件列表硬编码在 Python tuple 中。

建议 schema：

```json
{
  "schemaVersion": 1,
  "marketplace": "my-codex",
  "plugins": [
    {
      "name": "skill-watcher",
      "install": true,
      "check": true
    },
    {
      "name": "doc-watcher",
      "install": true,
      "check": true
    },
    {
      "name": "workflow",
      "install": true,
      "check": true
    },
    {
      "name": "mattpocock-skills",
      "install": true,
      "check": true
    },
    {
      "name": "orchestration",
      "install": true,
      "check": true
    }
  ]
}
```

脚本行为要求：

1. 默认 refresh 使用 `install: true` 的插件，按清单顺序执行。
2. 默认 check 使用 `check: true` 的插件，按清单顺序检查。
3. CLI `--plugin` 仍可显式缩小本次 refresh/check 范围；显式参数不得修改清单文件。
4. 清单中的 plugin 必须存在于 marketplace catalog；缺失时 fail fast。
5. plugin selector 默认补齐为 `plugin-name@marketplace-name`。

## Compatibility Surface

1. 迁移后 `$long-run-goal` 应继续触发同一个 skill 行为，但 Skill Watcher id 和 packaged skill id 变为 `workflow:long-run-goal`。
2. `personal-skills` 可在迁移说明中作为旧名出现，但不得作为 active plugin id、默认安装项、默认监控项或当前 layout 出现。
3. 不长期保留 `personal-skills` alias 插件，避免两个插件同时提供 `long-run-goal`。
4. 不编辑 Codex plugin cache、generated logs、runtime reports 或 `$CODEX_HOME` 文件来伪装迁移成功。

## 非目标

本 goal 不处理：

1. DocWatcher、Skill Watcher、Matt Pocock skills 或 orchestration 插件的产品重构，除非它们引用旧 plugin id 或安装清单。
2. 自动化调度变更、外部消息发送、远程发布或不可逆清理。
3. 长期保留 `personal-skills` 兼容插件。
4. 在未验证 Codex CLI selector 格式前强行删除旧插件安装状态。

## 阶段状态表

| Milestone | 状态 | Review gate |
|---|---|---|
| M0 - Contract Review And Design Freeze | `Done` | `Passed` |
| M1 - Plugin Install Manifest And Script Selection | `Done` | `Passed` |
| M2 - Rename Plugin To `workflow` | `Done` | `Passed` |
| M3 - Add `workflow:sop` Skill | `Done` | `Passed` |
| M4 - Update Skill Watcher Attribution | `Done` | `Passed` |
| M5 - Install Migration And Current Docs Closeout | `Done` | `Passed` |
| Close | `Done` | `Passed` |

## M0 - Contract Review And Design Freeze

状态：`Done`

范围：

1. 确认本计划的 source of truth、owner boundaries、install-manifest schema、rename 语义和非目标。
2. 确认 `.agents/plugins/install-manifest.json` 是脚本默认插件选择的唯一清单文件。
3. 确认 marketplace catalog 与 install selection 是两个不同事实源。
4. 不移动插件目录，不修改脚本行为，不执行 Codex plugin install/remove。

Review gate：

1. 本文件通过 long-run-goal readiness check。
2. `docs/todo/README.md` 引用本 active goal。
3. 本文件没有未替换占位符，且所有相对 Markdown 链接可解析。

执行证据：

1. 代码证据：
   - 更新 `docs/todo/refactor-personal-skills.md`：冻结 source of truth、owner boundaries、install-manifest schema、阶段 gate、失败处理、close procedure 和 reusable prompt。
   - 更新 `docs/todo/README.md`：将本 goal 加入 active long-running goal 导航。
2. 行为证据：
   - 无 runtime、plugin install、plugin cache 或 hook 状态变化。
   - M0 明确冻结 `.agents/plugins/install-manifest.json` 作为后续 refresh/check 默认插件选择的唯一清单文件；实际 manifest 和脚本迁移留给 M1。
3. 测试证据：
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_goal_ready.py docs/todo/refactor-personal-skills.md` -> passed: `goal readiness checks OK`。
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_todo_index.py docs/todo/refactor-personal-skills.md docs/todo/README.md` -> passed: referenced by 1 index file。
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs/todo` -> passed: markdown relative links OK。
   - `python3 plugins/doc-watcher/skills/doc-alignment/scripts/check_planning_tree.py docs/todo` -> passed: planning tree OK with 2 active markdown files and 1 index.
   - `git diff --check -- docs/todo/refactor-personal-skills.md docs/todo/README.md` -> passed with no output.
4. 文档证据：
   - 本 goal 文件和 `docs/todo/README.md` 已同步；active TODO index 能发现本 goal。
5. 回滚证据：
   - 回滚本阶段只需恢复 `docs/todo/refactor-personal-skills.md` 和 `docs/todo/README.md`。
6. 剩余风险：
   - M1-M5 尚未执行；`personal-skills` 仍是当前插件目录和默认脚本硬编码状态。

推荐验证：

```bash
python3 plugins/workflow/skills/long-run-goal/scripts/check_goal_ready.py docs/todo/refactor-personal-skills.md
python3 plugins/workflow/skills/long-run-goal/scripts/check_todo_index.py docs/todo/refactor-personal-skills.md docs/todo/README.md
python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs/todo
python3 plugins/doc-watcher/skills/doc-alignment/scripts/check_planning_tree.py docs/todo
git diff --check -- docs/todo/refactor-personal-skills.md docs/todo/README.md
```

Checkpoint evidence：

```text
Document checkpoint: M0 evidence recorded in docs/todo/refactor-personal-skills.md; no Git checkpoint commit requested.
```

## M1 - Plugin Install Manifest And Script Selection

状态：`Done`

Strategy evolution：

1. 执行 M1 前发现原 M1 范围要求清单默认包含 `workflow`，但 M2 才会将 marketplace 和 plugin directory 切到 `workflow`。
2. 该范围会导致 M1 的 refresh/check 默认选择当前不存在的 plugin id，违反“不把运行状态推进到不存在路径”的 gate。
3. M1 调整为先落地清单机制，并在过渡期默认选择当前存在的 `personal-skills`；M2 在完成 rename 时再把清单默认项切到 `workflow`。

范围：

1. 新增 `.agents/plugins/install-manifest.json`，M1 过渡期默认包含 `skill-watcher`、`doc-watcher`、`personal-skills`、`mattpocock-skills`、`orchestration`；M2 完成 rename 时必须切换为 `workflow`。
2. 在 `scripts/refresh_my_codex.py` 中加入 manifest loader，默认安装列表来自清单而不是 `PLUGIN_NAMES`。
3. 在 `scripts/check_my_codex.py` 中加入或复用 manifest loader，默认检查列表来自清单而不是硬编码 tuple。
4. 保留 CLI `--plugin` 作为本次运行的显式选择，不写回清单。
5. 为 manifest parse、缺失 plugin、install/check 过滤和 selector 补齐补测试。
6. 不在本阶段重命名目录；`workflow` 目录尚不存在时不得让默认 refresh/check 指向 `workflow`。

Review gate：

1. 脚本内不存在默认插件列表硬编码 tuple；默认列表来自 `.agents/plugins/install-manifest.json`。
2. 清单中 selected plugin 缺失于 marketplace 时会 fail fast，不静默跳过。
3. `--plugin` 显式参数仍可选择子集运行。
4. 测试覆盖安装清单 schema、默认选择和错误处理。
5. M1 默认清单保持当前可运行的 `personal-skills`；M2 必须将其切换为 `workflow`。

执行证据：

1. 代码证据：
   - 新增 `.agents/plugins/install-manifest.json`，M1 过渡期选择 `skill-watcher`、`doc-watcher`、`personal-skills`、`mattpocock-skills`、`orchestration`。
   - 更新 `scripts/refresh_my_codex.py`：移除 `PLUGIN_NAMES`，新增 install manifest loader、marketplace 校验、`install`/`check` action 选择和 selector 规范化。
   - 更新 `scripts/check_my_codex.py`：默认 check 插件来自 manifest，marketplace check 使用选中的 plugin selectors。
   - 更新 `plugins/skill-watcher/tests/test_skill_watcher.py`：覆盖 manifest 默认选择、显式 `--plugin` 子集和 selected plugin 缺失于 marketplace 时的 fail-fast。
   - 更新 `plugins/skill-watcher/scripts/codex_hook_adapter.py` 和 `plugins/skill-watcher/README.md`：M1 测试暴露默认 monitored skills 少了已打包的 `orchestration:orchestrate-subagents`，已修正 allowlist 和 alias。
2. 行为证据：
   - `refresh_my_codex.py` 默认安装列表现在来自 `.agents/plugins/install-manifest.json` 的 `install: true` 条目。
   - `check_my_codex.py` 默认检查列表现在来自 `.agents/plugins/install-manifest.json` 的 `check: true` 条目。
   - repeated `--plugin` 仍作为一次性子集选择，不写回清单。
   - 清单或显式 selector 指向当前 marketplace 缺失的 plugin 时会 fail fast。
   - M1 过渡期 dry-run 仍指向当前存在的 `personal-skills@my-codex`，没有提前指向尚不存在的 `workflow@my-codex`。
3. 测试证据：
   - `python3 scripts/bootstrap_tooling_env.py` -> passed; confirmed `/Users/max/.codex/venvs/my-codex/bin/python` imports PyYAML 6.0.3.
   - `python3 -m json.tool .agents/plugins/install-manifest.json >/dev/null` -> passed.
   - `python3 -m py_compile scripts/*.py` -> passed.
   - `/Users/max/.codex/venvs/my-codex/bin/python -m unittest plugins/skill-watcher/tests/test_skill_watcher.py` -> passed: 11 tests, 3 skipped.
   - `python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor` -> passed; printed `codex plugin add` for `skill-watcher`, `doc-watcher`, `personal-skills`, `mattpocock-skills`, and `orchestration`; dry-run wrote no changes.
   - `python3 scripts/check_my_codex.py --help` -> passed; check entry point loads new selection function.
   - `rg --hidden -n "PLUGIN_NAMES" scripts plugins .agents README.md docs/todo/refactor-personal-skills.md --glob '!**/__pycache__/**'` -> passed for code: only this goal document still mentions `PLUGIN_NAMES` as historical baseline and target text.
   - `git diff --check -- .agents/plugins/install-manifest.json scripts plugins/skill-watcher/tests/test_skill_watcher.py plugins/skill-watcher/scripts/codex_hook_adapter.py plugins/skill-watcher/README.md README.md docs/todo/refactor-personal-skills.md docs/todo/README.md` -> passed with no output.
4. 文档证据：
   - Root `README.md` now documents `.agents/plugins/install-manifest.json` as the default install/final-check selection source and includes it in layout.
   - `plugins/skill-watcher/README.md` default monitored skills list now includes `orchestration:orchestrate-subagents`.
   - This goal records the M1 strategy evolution that keeps `personal-skills` until M2 performs the rename.
5. 回滚证据：
   - 可删除 manifest loader 并恢复旧脚本，但不得用旧 tuple 作为最终状态。
6. 剩余风险：
   - M2 尚未执行；manifest 仍在过渡期选择 `personal-skills`，必须在 M2 rename 时切换为 `workflow`。
   - Full `scripts/check_my_codex.py` 未在 M1 执行，因为它会检查当前 `$CODEX_HOME` plugin install/cache/hook runtime 状态；M5 才执行实际安装迁移和 final closure check。

推荐验证：

```bash
python3 -m json.tool .agents/plugins/install-manifest.json >/dev/null
python3 -m py_compile scripts/*.py
python3 scripts/bootstrap_tooling_env.py
"$MY_CODEX_PYTHON" -m unittest plugins/skill-watcher/tests/test_skill_watcher.py
python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor
git diff --check -- .agents/plugins/install-manifest.json scripts plugins/skill-watcher/tests/test_skill_watcher.py README.md
```

Checkpoint evidence：

```text
Document checkpoint: M1 evidence recorded in docs/todo/refactor-personal-skills.md; no Git checkpoint commit requested.
```

## M2 - Rename Plugin To `workflow`

状态：`Done`

Strategy evolution：

1. 执行 M2 前确认 `plugins/skill-watcher/tests/test_skill_watcher.py` 会从 `plugins/*/skills/*/SKILL.md` 推导 packaged skill ids，并要求它们等于 `DEFAULT_MONITORED_SKILLS`。
2. 因此目录一旦从 `plugins/personal-skills` 改名为 `plugins/workflow`，`personal-skills:long-run-goal` 会立即变成失效的当前 attribution id。
3. M2 必须同步 `workflow:long-run-goal` 的 Skill Watcher allowlist、alias 和 README；M4 缩小为新增 `workflow:sop` 后的 attribution 补充。

范围：

1. 使用 `git mv plugins/personal-skills plugins/workflow`。
2. 更新 `plugins/workflow/.codex-plugin/plugin.json`：`name` 为 `workflow`，display name 为 `Workflow`，description/default prompt 采用 reusable workflow skills 语义。
3. 更新 `.agents/plugins/marketplace.json`：移除 `personal-skills` 条目，新增 `workflow` 条目并指向 `./plugins/workflow`。
4. 更新 `.agents/plugins/install-manifest.json`：默认选择 `workflow`，不选择 `personal-skills`。
5. 更新 [README.md](../../../README.md) 的插件说明、Unix/Windows 安装命令、手动 reinstall checklist、验证命令和 layout。
6. 更新 `plugins/skill-watcher/scripts/codex_hook_adapter.py` 和 `plugins/skill-watcher/README.md` 中的 `personal-skills:long-run-goal` 为 `workflow:long-run-goal`。
7. 不新增 SOP skill；本阶段只完成 plugin rename、`long-run-goal` attribution 和当前 docs/script 引用。

Review gate：

1. active docs 中不再把 `personal-skills` 当作当前 plugin id；旧名只允许出现在本计划、迁移说明或 historical context。
2. marketplace 只有 `workflow`，没有 `personal-skills`。
3. root README 的安装、验证和 layout 指向 `plugins/workflow`。
4. plugin validator 对 `plugins/workflow` 通过。
5. Skill Watcher packaged-skill guard 对 `workflow:long-run-goal` 通过。

执行证据：

1. 代码证据：
   - 使用 `git mv plugins/personal-skills plugins/workflow` 完成目录迁移。
   - 更新 `plugins/workflow/.codex-plugin/plugin.json`：plugin `name`、display name、description 和 default prompt 均改为 `workflow` / reusable workflow skills 语义。
   - 更新 `.agents/plugins/marketplace.json`：`personal-skills` 条目改为 `workflow`，路径改为 `./plugins/workflow`。
   - 更新 `.agents/plugins/install-manifest.json`：默认 install/check 选择从 `personal-skills` 切到 `workflow`。
   - 更新 `README.md` 的插件说明、Unix/Windows 安装命令、手动 reinstall checklist、验证命令和 layout。
   - 更新 `plugins/skill-watcher/scripts/codex_hook_adapter.py`、`plugins/skill-watcher/README.md` 和 `plugins/skill-watcher/tests/test_skill_watcher.py`：`long-run-goal` attribution 从 `personal-skills:long-run-goal` 切到 `workflow:long-run-goal`。
2. 行为证据：
   - `python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor` 现在打印 `codex plugin add workflow@my-codex`，不再打印 `personal-skills@my-codex`。
   - Skill Watcher packaged-skill guard 现在以 `workflow:long-run-goal` 匹配重命名后的 `plugins/workflow/skills/long-run-goal/SKILL.md`。
   - 未执行实际 `codex plugin add/remove`，未修改 `$CODEX_HOME` runtime 状态。
3. 测试证据：
   - `python3 -m json.tool .agents/plugins/marketplace.json >/dev/null` -> passed.
   - `python3 -m json.tool .agents/plugins/install-manifest.json >/dev/null` -> passed.
   - `/Users/max/.codex/venvs/my-codex/bin/python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/my-codex/plugins/workflow` -> passed: plugin validation passed.
   - `/Users/max/.codex/venvs/my-codex/bin/python -m unittest plugins/skill-watcher/tests/test_skill_watcher.py` -> passed: 11 tests, 3 skipped.
   - `python3 scripts/refresh_my_codex.py --dry-run --skip-bootstrap --skip-marketplace --skip-hooks --skip-doctor` -> passed; dry-run printed `workflow@my-codex`.
   - `rg --hidden -n "personal-skills|plugins/personal-skills|personal-skills@my-codex" README.md .agents scripts plugins --glob '!**/.git/**' --glob '!**/__pycache__/**'` -> passed with no output.
   - `rg --hidden -n "personal-skills|plugins/personal-skills|personal-skills@my-codex" docs --glob '!**/.git/**' --glob '!**/__pycache__/**'` -> returned only this goal file and the active TODO title/description as migration context.
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_goal_ready.py docs/todo/refactor-personal-skills.md` -> passed.
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_todo_index.py docs/todo/refactor-personal-skills.md docs/todo/README.md` -> passed.
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs/todo` -> passed.
   - `python3 plugins/doc-watcher/skills/doc-alignment/scripts/check_planning_tree.py docs/todo` -> passed.
   - `git diff --check -- README.md .agents scripts plugins docs/todo/refactor-personal-skills.md docs/todo/README.md` -> passed with no output.
4. 文档证据：
   - Root `README.md` now points installation, validation, and layout to `workflow`.
   - `docs/todo/refactor-personal-skills.md` updated its active helper paths to `plugins/workflow`.
   - `docs/todo/README.md` remains an active goal index; its old name references are migration context.
5. 回滚证据：
   - `git mv plugins/workflow plugins/personal-skills` 并恢复 marketplace、manifest、README 和脚本引用。
6. 剩余风险：
   - M3-M5 尚未执行；`workflow:sop` 尚未新增，runtime install/cache 仍待 M5 实际迁移。
   - `$CODEX_HOME` 可能仍安装旧 `personal-skills@my-codex`，必须在 M5 用实际 `codex plugin list` / remove / check 证据处理。

推荐验证：

```bash
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool .agents/plugins/install-manifest.json >/dev/null
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/workflow"
/Users/max/.codex/venvs/my-codex/bin/python -m unittest plugins/skill-watcher/tests/test_skill_watcher.py
rg --hidden -n "personal-skills|plugins/personal-skills|personal-skills@my-codex" README.md .agents scripts plugins --glob '!**/.git/**' --glob '!**/__pycache__/**'
rg --hidden -n "personal-skills|plugins/personal-skills|personal-skills@my-codex" docs --glob '!**/.git/**' --glob '!**/__pycache__/**'
git diff --check -- README.md .agents scripts plugins docs/todo/refactor-personal-skills.md
```

Checkpoint evidence：

```text
Document checkpoint: M2 evidence recorded in docs/todo/refactor-personal-skills.md; no Git checkpoint commit requested.
```

## M3 - Add `workflow:sop` Skill

状态：`Done`

范围：

1. 新增 `plugins/workflow/skills/sop/SKILL.md`。
2. 新增 `plugins/workflow/skills/sop/agents/openai.yaml`。
3. 新增 `plugins/workflow/skills/sop/templates/sop_template.md`。
4. 新增 `plugins/workflow/skills/sop/scripts/check_sop_ready.py` 和 `check_sop_links.py`。
5. 可选新增 `plugins/workflow/README.md`，仅说明 `long-run-goal` 与 `sop` 的边界。
6. 不修改 Skill Watcher attribution；M4 处理监控和测试。

SOP skill 一句话语义：

```text
Use when creating, updating, executing, validating, or reusing a deterministic standard operating procedure for a recurring task whose trigger, inputs, steps, outputs, validation, stop conditions, and failure handling are already known or can be made explicit.
```

Review gate：

1. `sop` frontmatter 只包含 `name` 和 `description`。
2. `sop` body 是 imperative procedure，不包含这次迁移的历史叙述。
3. SOP 模板包含摘要、触发条件、前置条件、工作目录、输入、允许动作、禁止动作、标准步骤、验证标准、输出合同、停止条件、更新规则和复用 prompt。
4. helper scripts 只使用 Python 标准库，失败时输出具体文件和断点。
5. `workflow` plugin validator 通过。

执行证据：

1. 代码证据：
   - 新增 `plugins/workflow/skills/sop/SKILL.md`，frontmatter 只包含 `name` 和 `description`，body 为可复用 SOP 创建、执行、更新和验证流程。
   - 新增 `plugins/workflow/skills/sop/agents/openai.yaml`，提供 SOP skill 的 UI display metadata 和默认 prompt。
   - 新增 `plugins/workflow/skills/sop/templates/sop_template.md`，包含摘要、触发条件、前置条件、工作目录、输入、允许动作、禁止动作、标准步骤、验证标准、输出合同、停止条件、更新规则和复用 Prompt。
   - 新增 `plugins/workflow/skills/sop/scripts/check_sop_ready.py` 和 `check_sop_links.py`，均只使用 Python 标准库。
   - 新增 `plugins/workflow/README.md`，简要说明 `long-run-goal` 与 `sop` skill 边界。
2. 行为证据：
   - `workflow` plugin 现在打包 `long-run-goal` 和 `sop` 两个 skills。
   - `sop` skill 只覆盖稳定、可明确化的标准流程；探索性计划和多阶段执行仍交给 `long-run-goal`。
   - M3 未修改 Skill Watcher `workflow:sop` attribution；该接入留给 M4。
3. 测试证据：
   - `python3 -m py_compile plugins/workflow/skills/sop/scripts/*.py` -> passed.
   - `python3 plugins/workflow/skills/sop/scripts/check_sop_links.py plugins/workflow/skills/sop` -> passed: SOP markdown relative links OK.
   - `python3 plugins/workflow/skills/sop/scripts/check_sop_ready.py TEMP_READY_SOP` -> passed: SOP readiness checks OK. First wrapper attempt used zsh read-only variable `status` and failed after the checker printed OK; rerun with `rc` passed.
   - `/Users/max/.codex/venvs/my-codex/bin/python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/my-codex/plugins/workflow` -> passed: plugin validation passed.
   - `git diff --check -- plugins/workflow README.md docs/todo/refactor-personal-skills.md` -> passed with no output.
4. 文档证据：
   - `plugins/workflow/README.md` added as the plugin-local skill summary.
   - This goal records that Skill Watcher attribution is intentionally deferred to M4.
5. 回滚证据：
   - 删除 `plugins/workflow/skills/sop` 并从 README/manifest/Skill Watcher 待办中移除引用。
6. 剩余风险：
   - M4 尚未执行，Skill Watcher default monitored skills does not yet include `workflow:sop`; running its packaged-skill guard before M4 would be expected to fail.
   - M5 尚未执行，runtime install/cache still needs actual migration evidence.

推荐验证：

```bash
python3 -m py_compile plugins/workflow/skills/sop/scripts/*.py
python3 plugins/workflow/skills/sop/scripts/check_sop_links.py plugins/workflow/skills/sop
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/workflow"
git diff --check -- plugins/workflow README.md docs/todo/refactor-personal-skills.md
```

Checkpoint evidence：

```text
Document checkpoint: M3 evidence recorded in docs/todo/refactor-personal-skills.md; no Git checkpoint commit requested.
```

## M4 - Update Skill Watcher Attribution

状态：`Done`

范围：

1. 更新 `plugins/skill-watcher/scripts/codex_hook_adapter.py`：新增默认 monitored skill `workflow:sop`。
2. 更新 `DEFAULT_SKILL_ALIASES`：新增 `workflow:sop` aliases，包括 `sop`、`standard operating procedure`、`standard procedure`、`标准流程`、`标准处理流程`。
3. 更新 `plugins/skill-watcher/README.md` 默认 monitored skills 列表。
4. 更新或确认 `plugins/skill-watcher/tests/test_skill_watcher.py` 仍能以 packaged skills 作为 guard。
5. 不修改 Skill Watcher runtime logs、reports、proposals 或 hook trust 状态。

Review gate：

1. `DEFAULT_MONITORED_SKILLS` 与 `plugins/*/skills/*/SKILL.md` 推导出的 packaged skills 一致。
2. `workflow:sop` 的 prompt mention 和 assistant announcement attribution 可被 alias 匹配。
3. README 与 adapter 默认列表一致。
4. Skill Watcher tests 通过。

执行证据：

1. 代码证据：
   - 更新 `plugins/skill-watcher/scripts/codex_hook_adapter.py`：默认 monitored skills 新增 `workflow:sop`。
   - 更新 `DEFAULT_SKILL_ALIASES`：`workflow:sop` 新增 `sop`、`standard operating procedure`、`standard procedure`、`标准流程`、`标准处理流程` aliases。
   - 更新 normalized event 的 `codex.matched_alias`，让 prompt mention 和 assistant announcement 都能保留实际匹配 alias 证据。
   - 更新 `plugins/skill-watcher/README.md` 默认 monitored skills 列表，加入 `workflow:sop`。
   - 更新 `plugins/skill-watcher/tests/test_skill_watcher.py`：补充 `workflow:sop` 中文 prompt mention 和 assistant announcement attribution 断言。
2. 行为证据：
   - Skill Watcher 默认 allowlist 现在覆盖 `workflow:sop`。
   - 用户 prompt 中出现 `标准流程` 会归因到 `workflow:sop`，attribution 为 `prompt_mention`。
   - assistant message 中出现 `$sop` 会归因到 `workflow:sop`，attribution 为 `assistant_announcement`。
   - 未修改 Skill Watcher runtime logs、reports、proposals、hook trust 或 `$CODEX_HOME` 状态。
3. 测试证据：
   - 第一次运行 `/Users/max/.codex/venvs/my-codex/bin/python -m unittest plugins/skill-watcher/tests/test_skill_watcher.py` 失败，因为 normalized event 的 `codex` metadata 未暴露 `matched_alias`；已补充该字段后重跑。
   - `/Users/max/.codex/venvs/my-codex/bin/python -m unittest plugins/skill-watcher/tests/test_skill_watcher.py` -> passed: 11 tests, 3 skipped.
   - `/Users/max/.codex/venvs/my-codex/bin/python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/my-codex/plugins/skill-watcher` -> passed: plugin validation passed.
   - `git diff --check -- plugins/skill-watcher docs/todo/refactor-personal-skills.md` -> passed with no output.
4. 文档证据：
   - `plugins/skill-watcher/README.md` default monitored skills list now matches adapter and packaged skill ids.
   - This goal records that M4 did not touch runtime hook trust or generated Skill Watcher artifacts.
5. 回滚证据：
   - 恢复 adapter 和 README，但不得在最终状态同时监控旧新两个 long-run-goal id。
6. 剩余风险：
   - M5 尚未执行；`workflow@my-codex` 仍未实际 installed/refreshed in `$CODEX_HOME` during this goal, and old `personal-skills@my-codex` runtime state may still exist.

推荐验证：

```bash
python3 -m unittest plugins/skill-watcher/tests/test_skill_watcher.py
"$MY_CODEX_PYTHON" "$PLUGIN_VALIDATOR" "$MY_CODEX_ROOT/plugins/skill-watcher"
git diff --check -- plugins/skill-watcher docs/todo/refactor-personal-skills.md
```

Checkpoint evidence：

```text
Document checkpoint: M4 evidence recorded in docs/todo/refactor-personal-skills.md; no Git checkpoint commit requested.
```

## M5 - Install Migration And Current Docs Closeout

状态：`Done`

Strategy evolution：

1. 执行 M5 前确认当前 worktree 仍包含本 goal 的未提交 plugin rename、manifest 和 skill 改动。
2. `scripts/refresh_my_codex.py` 若只检查 `HEAD == origin/main`，可能在 dirty worktree 中错误使用 Git marketplace source，从而安装不到当前未提交的 `workflow` 改动。
3. M5 先收紧 refresh source gate：只有 `HEAD` 匹配目标 ref 且 worktree 干净时才使用 Git marketplace source；dirty worktree 必须使用 local marketplace source。

范围：

1. 运行 refresh dry-run，确认默认插件选择来自 install manifest。
2. 运行 refresh 实际安装，刷新 `workflow@my-codex` 和 hooks。
3. 删除旧 `personal-skills@my-codex` 安装状态；如果 selector 格式失败，先运行 `codex plugin list` 读取实际显示名，再执行删除。
4. 运行 final check，确认 marketplace、plugin list、cache manifest、hook schema、plugin validator 和 Skill Watcher doctor。
5. 更新 README 和本计划的执行证据；不把 runtime cache 或 generated logs 纳入源码提交。

Review gate：

1. `codex plugin list` 最终只显示 `workflow@my-codex`，不显示启用的 `personal-skills@my-codex`。
2. `scripts/check_my_codex.py` 通过。
3. Skill Watcher hooks 刷新后有明确提示用户在 `/hooks` 中 trust；不声称 hook 已被用户信任，除非有 UI 或命令证据。
4. root README、plugin README、Skill Watcher README、TODO index 与最终状态一致。

执行证据：

1. 代码证据：
   - 更新 `scripts/refresh_my_codex.py`：`git_remote_ref_status` 现在先检查 `git status --porcelain`，只有 `HEAD` 匹配目标 ref 且 worktree 干净时才使用 Git marketplace source；dirty worktree 会使用 local marketplace source。
   - 更新 `README.md`：说明 Git marketplace source 只在 `HEAD` 匹配且 worktree 干净时使用；stale、dirty、unavailable 或失败时使用 local source。
   - `.agents/plugins/install-manifest.json` 是 refresh/check 的默认插件选择来源，当前选择 `skill-watcher`、`doc-watcher`、`workflow`、`mattpocock-skills` 和 `orchestration`。
2. 行为证据：
   - `python3 scripts/refresh_my_codex.py --dry-run` 在 dirty worktree 中选择 local marketplace source，并打印 manifest-selected `codex plugin add` 命令，包括 `workflow@my-codex` 和 `orchestration@my-codex`。
   - `python3 scripts/refresh_my_codex.py` 实际刷新完成，安装 manifest-selected plugins，并安装 `workflow@my-codex` 到 `/Users/max/.codex/plugins/cache/my-codex/workflow/0.1.0`。
   - refresh 更新 Skill Watcher hooks，备份为 `/Users/max/.codex/skill-watcher/backups/hooks-json/20260607T055942Z-hooks.json`，写入 `/Users/max/.codex/hooks.json`，并提示用户打开 `/hooks` review 和 trust 新 command hook definitions。
   - 初次 `codex plugin list` 显示 `workflow@my-codex`、`orchestration@my-codex` 和其他 manifest-selected plugins 均为 `installed, enabled`，旧 `personal-skills@my-codex` 不在 marketplace 列表中。
   - cache 检查发现旧 `/Users/max/.codex/plugins/cache/my-codex/personal-skills` 仍残留；执行 `codex plugin remove personal-skills@my-codex` 后返回 `Removed plugin personal-skills from marketplace my-codex`。
   - 删除后复查 `codex plugin list`，`my-codex` 只显示 `skill-watcher`、`doc-watcher`、`workflow`、`mattpocock-skills`、`orchestration` 为 installed/enabled；复查 cache 只命中 `/Users/max/.codex/plugins/cache/my-codex/workflow`，不再命中 `personal-skills`。
3. 测试证据：
   - `python3 -m py_compile scripts/*.py` -> passed.
   - `python3 scripts/refresh_my_codex.py --dry-run` -> passed; local source reason: `local worktree has uncommitted changes`; dry-run wrote no changes.
   - `python3 scripts/refresh_my_codex.py` -> passed; refresh complete; Skill Watcher doctor passed with 0 warnings.
   - `codex plugin remove personal-skills@my-codex` -> passed; removed old plugin from local config and cache.
   - `find /Users/max/.codex/plugins/cache/my-codex -maxdepth 3 -type d -name 'personal-skills' -o -name 'workflow' | sort` after remove -> only `/Users/max/.codex/plugins/cache/my-codex/workflow`.
   - `python3 scripts/check_my_codex.py` after remove -> passed; marketplace, PyYAML, `codex plugin list`, plugin cache manifests, hook schema, plugin validators and Skill Watcher doctor all passed with 0 warnings.
   - `git diff --check -- README.md .agents scripts plugins docs/todo` -> passed with no output.
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_goal_ready.py docs/todo/refactor-personal-skills.md` -> passed.
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_todo_index.py docs/todo/refactor-personal-skills.md docs/todo/README.md` -> passed.
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs/todo` -> passed.
   - `python3 plugins/doc-watcher/skills/doc-alignment/scripts/check_planning_tree.py docs/todo` -> passed.
4. 文档证据：
   - Root `README.md`、`plugins/workflow/README.md`、`plugins/skill-watcher/README.md`、`.agents/plugins/marketplace.json`、`.agents/plugins/install-manifest.json` 和 `docs/todo/README.md` 与 `workflow` 最终状态一致。
   - 本 goal 记录 M5 source gate strategy evolution、install/remove/runtime check 证据和 hook trust 边界。
5. 回滚证据：
   - 源码回滚可恢复 M1-M5 touched files 和 `plugins/workflow` rename。
   - Runtime 回滚需用户明确决定后重新安装旧 selector；当前不保留 `personal-skills@my-codex` alias，也不编辑 cache 来伪装成功。
6. 剩余风险：
   - 当前 session 的可用 skill 列表可能仍含启动时加载的旧 `personal-skills:long-run-goal`，但 final `codex plugin list` 和 plugin cache 证据显示新会话的 `my-codex` runtime 状态已迁到 `workflow`。
   - Hook installer 已写入 hooks 并提示 `/hooks` review/trust；没有 UI 或命令证据证明用户已完成 trust，因此本 goal 不声称 hook trust 已完成。

推荐验证：

```bash
python3 scripts/refresh_my_codex.py --dry-run
python3 scripts/refresh_my_codex.py
codex plugin list
codex plugin remove personal-skills@my-codex
python3 scripts/check_my_codex.py
git diff --check -- README.md .agents scripts plugins docs/todo
```

Checkpoint evidence：

```text
Document checkpoint: M5 evidence recorded in docs/todo/refactor-personal-skills.md; no Git checkpoint commit requested.
```

## Close Procedure

状态：`Done`

Close 前必须满足：

1. M0-M5 均为 `Done`，所有 review gate 为 `Passed`。
2. 所有执行证据均填入本文件或对应验证报告。
3. `.agents/plugins/install-manifest.json`、`.agents/plugins/marketplace.json`、root README、Skill Watcher README、workflow plugin files 和脚本引用一致。
4. `rg` 只在迁移说明、本计划或明确 historical context 中命中 `personal-skills`。
5. 最终 `scripts/check_my_codex.py` 通过，或明确记录外部 blocker 且不关闭 goal。
6. `docs/todo/README.md` 从 active goal list 中移除本文件。

关闭方式：

1. 将整体状态改为 `Closed`。
2. 记录最终 close evidence、最终验证命令和结果。
3. 若没有本地 archive convention，不创建新的 dated archive directory；通过 Git history 和 close checkpoint 保存历史。
4. 如果用户要求 active planning tree 保持无 closed 文件，则在当前 docs 同步完成后删除本 goal 文件；否则保留为 closed historical file 但必须从 active TODO index 移除，并接受 planning tree check 的相应范围调整。

Close 推荐验证：

```bash
python3 scripts/check_my_codex.py
python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs/todo
git diff --check -- README.md .agents scripts plugins docs/todo
```

Close checkpoint evidence：

```text
Document checkpoint: Close evidence recorded before archiving; no Git checkpoint commit requested.
```

Close execution evidence：

1. 代码证据：
   - 将整体状态改为 `Closed`，将 Close review gate 标记为 `Passed`。
   - 将本 goal 从 active TODO 导航移除，并作为历史 closed goal 移到 `docs/todo/archive/refactor-personal-skills.md`。
   - 新增 `docs/todo/archive/README.md` 作为 closed planning archive index。
2. 行为证据：
   - Active planning tree 不再包含本 goal；历史 checkpoint evidence 保留在 archive。
   - 未修改 `$CODEX_HOME` runtime cache、generated logs 或 hook trust 状态。
3. 测试证据：
   - `python3 scripts/check_my_codex.py` -> passed with 0 warnings.
   - `python3 plugins/workflow/skills/long-run-goal/scripts/check_md_links.py docs/todo` -> passed.
   - `python3 plugins/doc-watcher/skills/doc-alignment/scripts/check_planning_tree.py docs/todo` -> passed: `1 active md, 2 archive md, 1 index md`.
   - `git diff --check -- README.md .agents scripts plugins docs/todo` -> passed with no output.
   - `rg --hidden -n "PLUGIN_NAMES|personal-skills|plugins/personal-skills|personal-skills@my-codex" README.md .agents scripts plugins docs/todo/README.md --glob '!**/.git/**' --glob '!**/__pycache__/**'` -> no active-surface matches.
   - `rg --hidden -n "personal-skills|plugins/personal-skills|personal-skills@my-codex" README.md .agents scripts plugins docs/todo/README.md docs/todo/archive --glob '!**/.git/**' --glob '!**/__pycache__/**'` -> only archive/historical migration context.
   - `/Users/max/.codex/venvs/my-codex/bin/python -m unittest plugins/skill-watcher/tests/test_skill_watcher.py` -> passed: 11 tests, 3 skipped.
   - `python3 -m py_compile scripts/*.py plugins/workflow/skills/sop/scripts/*.py plugins/workflow/skills/long-run-goal/scripts/*.py` -> passed.
   - `python3 plugins/workflow/skills/sop/scripts/check_sop_links.py plugins/workflow/skills/sop` -> passed.
   - `/Users/max/.codex/venvs/my-codex/bin/python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/my-codex/plugins/workflow` -> passed.
   - `/Users/max/.codex/venvs/my-codex/bin/python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/my-codex/plugins/skill-watcher` -> passed.
4. 文档证据：
   - `docs/todo/README.md` now reports no active long-running goal plans.
   - `docs/todo/archive/README.md` links to this closed goal.
5. 回滚证据：
   - Reopen by moving `docs/todo/archive/refactor-personal-skills.md` back to `docs/todo/refactor-personal-skills.md`, restoring its active TODO index entry, and changing overall status from `Closed` to `Ready` or an appropriate milestone status.
6. 剩余风险：
   - Hook installer emitted the `/hooks` review/trust instruction during M5; no UI or command evidence was collected to prove user trust state.

## Reusable Goal Prompt (Historical)

```text
Resume the long-running goal at docs/todo/archive/refactor-personal-skills.md.

Follow milestones in order: M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> Close.
Before starting a milestone, mark it In Progress. Do not enter the next milestone until the current review gate passes. Record code evidence, behavior evidence, test evidence, docs evidence, rollback evidence, remaining risk, and checkpoint evidence for each milestone.

Do not bypass failures with fallback paths, alias plugins, fake success states, hidden partial success, alternate backends, or changed assumptions. Stop on failed validation and record the root cause, failing command or path, exact breakpoint when known, and the next diagnostic step.

The install/check plugin list must come from .agents/plugins/install-manifest.json, not a hardcoded script tuple. Marketplace availability remains in .agents/plugins/marketplace.json. The final state should use workflow@my-codex and not keep personal-skills@my-codex enabled.
```
