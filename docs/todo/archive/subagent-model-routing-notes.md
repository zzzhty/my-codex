# Subagent Model Routing Notes

状态：Background design note；v1 execution contract 已迁移到 [subagent-model-routing-v1.md](subagent-model-routing-v1.md)。

本文件保留 subagent model-routing、custom-agent TOML 和 character 讨论的背景材料。当前可执行 long-run-goal plan 是 [subagent-model-routing-v1.md](subagent-model-routing-v1.md)。

当前边界：

- 运行时执行合同仍以 `plugins/orchestration/skills/orchestrate-subagents/SKILL.md` 为准。
- V1 执行计划以 [subagent-model-routing-v1.md](subagent-model-routing-v1.md) 为准。
- 本文件中的旧角色清单、目录结构和模型分配是背景草案；与 v1 冲突时，以 [subagent-model-routing-v1.md](subagent-model-routing-v1.md) 为准。
- archive 只保留已关闭历史，不承载当前 open work。

背景阶段曾记录的问题：

1. 是否先落地 read-only custom agents，还是继续只使用内置 `explorer`、`default`、`worker` 加 assignment label。
2. 具体 custom-agent character、命名规范和文件名规范。
3. 是否在 M1 排除 write-capable agents，例如 `impl_worker` 和 `test_runner`。
4. 每个角色的模型和 `model_reasoning_effort` 是否固定，还是由 parent prompt 按任务选择。
5. 项目级 `.codex/agents/` 与个人级 `$CODEX_HOME/agents/` 的边界。
6. 是否增加一个 subagent fit check / advisor gate：复杂任务开始前先建议是否调用 `$orchestrate-subagents`，但不自动派生。
7. 是否采用 `read-only` / `mixed` / `write-capable` 三类 work mode 作为人类可扫读的建议标签。
8. 验证路径：Codex 版本、trusted project、agent 加载、`/agent` 可见性、sandbox/approval 继承行为和回滚方式。

V1 已在 [subagent-model-routing-v1.md](subagent-model-routing-v1.md) 中收口为：M1 只落地 read-only custom agents、managed `$CODEX_HOME/agents/` sync 和 orchestration fallback；write-capable agents 与 advisor skill 留作 Future。

官方依据：Codex 支持 custom agents，并允许在 agent TOML 中配置 `model`、`model_reasoning_effort`、`sandbox_mode` 等字段；custom agents 可放在 `~/.codex/agents/` 或项目级 `.codex/agents/`；`agents.max_threads` 默认上限为 6，`agents.max_depth` 默认 1。([OpenAI开发者][1])

## External Reference: `cast-subagents`

参考文章：[Codex 明明支持 Subagent，为什么却不会主动用？我做了个 Skill 来解决这个问题][2]。

文章方法可以概括为：

- 用常驻 guidance 先判断当前任务是否值得拆分。
- 简单任务保持安静，让主 agent 直接执行。
- 复杂任务调用一个 advisor skill，推荐 1-4 个 subagent 角色和工作模式。
- 在用户确认前不真正派生 subagent。
- 将建议模式分成 `read-only`、`mixed`、`write-capable`，让权限风险先被看见。

和本仓库当前方案的关系：

- 相同点：都反对把 subagent 理解成自动 router，都强调 read-heavy work 先并行出去，避免主上下文被探索日志、测试输出和文档核验污染。
- 不同点：`cast-subagents` 解决的是“提醒/建议层”；本仓库已经有 `orchestration:orchestrate-subagents` 作为“执行编排层”，负责 assignment、ownership、evidence、failure handling 和 consolidation。
- 不同点：`cast-subagents` 倾向打包一组常用角色；本仓库目前暂不把 character、命名和模型固化为 runtime TOML。
- 不同点：`cast-subagents` 可通过全局 gate 提前介入；本仓库不应把未收口设计写进全局 AGENTS，以免让所有任务都多一层噪音。

可吸收进本方案的内容：

1. 增加 `Subagent Fit Check`：在复杂任务开始前，先判断是否建议使用 `$orchestrate-subagents`。
2. 增加 `Work Mode` 标签：用 `read-only`、`mixed`、`write-capable` 表示建议阵容的写入风险。
3. 增加确认边界：advisor 只推荐，不自动 spawn；parent 在用户确认或明确任务授权后才执行。
4. 保持角色轻量：下一轮可以先把 `code-mapper`、`reviewer`、`docs-researcher` 等作为 recipe labels，而不是直接创建 custom-agent TOML。

不建议照搬的内容：

1. 不直接安装全局 AGENTS gate；如果要做 gate，应先在 repo-local TODO 中定义触发条件、静默条件、输出格式和验证方式。
2. 不直接安装全部内置角色；write-capable role 尤其需要等 disjoint write scope、rollback 和 validation 策略明确后再讨论。
3. 不让 advisor 取代 parent judgment；parent 仍负责是否派生、如何拆分、写范围控制、最终验证和用户结论。

## Subagent Fit Check 草案

触发候选：

- 复杂 PR review、branch review 或 multi-file diff review。
- 大型代码库探索、调用链梳理、架构边界判断。
- bug triage 中同时需要 reproduction、code-path mapping 和 test-risk review。
- 代码实现和官方文档/API 行为需要并行核对。
- 多方案技术调研或 migration/refactor planning。

静默条件：

- typo、单文件小改、简单解释、已有明确实现路径的小修。
- 用户明确要求不要使用 subagents。
- 任务需要严格顺序调试，提前并行会重复工作或制造冲突。
- 写入范围不清楚，但任务已经要求立即修改；这时 parent 应先收窄范围，而不是自动派生 worker。

建议输出格式：

```text
Subagent fit: recommended | not recommended
Mode: read-only | mixed | write-capable
Reason:
- <why this task is or is not worth splitting>
Suggested assignments:
- <role or built-in role> as <assignment-label>: <single task>
Confirmation needed:
- <what the parent/user must approve before spawning>
```

## Work Mode 草案

`read-only`：

- 只允许阅读、搜索、运行只读检查和汇总。
- 适合 review、code mapping、docs/API verification、test-gap discovery。
- 默认优先采用。

`mixed`：

- 先只读探索，再由 parent 决定是否进入修改阶段。
- 适合“不确定修复路径”的 bug、refactor planning、依赖/API migration planning。
- 不应在同一 subagent assignment 中混合 mapping 和 implementation。

`write-capable`：

- 只有在用户已经授权实现、写入范围互不重叠、回滚和验证路径明确时才使用。
- 每个 worker 必须有 disjoint ownership、blocked files、stop condition 和 validation evidence。
- 第一阶段 custom-agent TOML 不应优先落地 write-capable characters。

## Draft: Codex Model Routing / Subagent Delegation 设计说明

## 结论

Codex 默认使用一个主模型完成任务，但可以通过 **Subagent / Custom Agent** 机制实现近似“模型路由”。

核心判断：

- Codex 不是透明自动 Router。
- Codex 更接近：**主 Agent 显式委派任务给不同 Subagent**。
- 每个 Subagent 可以配置自己的：
  - `model`
  - `model_reasoning_effort`
  - `sandbox_mode`
  - `developer_instructions`
  - MCP servers
  - skills config

因此，`my-codex` 中可以把不同工程角色拆成独立 agent，并为它们指定不同模型。

## 推荐定位

不要把这个机制理解为：

> 主模型自动判断每一步该用哪个模型。

更合理的理解是：

> 通过 custom agent，把任务拆成“探索 / 审查 / 实现 / 文档核验 / 测试”几个角色；每个角色绑定不同模型、权限和指令；在 prompt 或 workflow 中显式要求 Codex 调用这些 subagents。

## 推荐目录结构

```text
.codex/
  config.toml
  agents/
    code-mapper.toml
    reviewer.toml
    impl-worker.toml
    docs-researcher.toml
    test-runner.toml
  skills/
    workflow/
    sop/
```

如果是个人全局配置，也可以放在：

```text
~/.codex/
  config.toml
  agents/
    code-mapper.toml
    reviewer.toml
    impl-worker.toml
```

项目级 `.codex/agents/` 更适合放进 `my-codex` 仓库，便于版本管理和复用。

## `.codex/config.toml` 建议

```toml
model = "gpt-5.5"
model_reasoning_effort = "high"

[agents]
max_threads = 6
max_depth = 1
```

说明：

* 主模型使用较强模型，负责总体规划、综合判断、最终决策。
* `max_threads = 6` 控制最多并行 agent 数量。
* `max_depth = 1` 避免 subagent 继续无限委派，降低失控风险。
* 复杂任务建议先让 read-only agents 完成探索和审查，再让 implementation agent 修改代码。

## Agent 角色设计

### 1. `code_mapper`

用途：只读代码探索，定位相关文件、调用链、配置入口、风险区域。

适合模型：

```toml
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
```

示例：

```toml
name = "code_mapper"
description = "Read-only codebase explorer for locating relevant files, symbols, configs, and execution paths."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"

developer_instructions = """
Stay in exploration mode.
Use fast search and targeted file reads.
Map relevant files, symbols, execution paths, configs, and likely risk points.
Do not edit files.
Do not propose large rewrites unless explicitly asked.
Return concise findings with file paths and next-step recommendations.
"""
```

适用场景：

* 大仓库改动前先摸清结构。
* 不确定 bug 来源。
* 需要避免主模型一上来就乱改代码。

---

### 2. `reviewer`

用途：强审查，只读，负责 correctness / security / regression / tests。

适合模型：

```toml
model = "gpt-5.5"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
```

示例：

```toml
name = "reviewer"
description = "Strict reviewer focused on correctness, security, regression risk, and missing tests."
model = "gpt-5.5"
model_reasoning_effort = "high"
sandbox_mode = "read-only"

developer_instructions = """
Review like a senior maintainer.
Prioritize real correctness bugs, behavior regressions, security issues, compatibility risks, and missing tests.
Avoid style-only comments unless they hide real maintenance risk.
Do not edit files.
Return findings with severity, evidence, affected files, and suggested fixes.
"""
```

适用场景：

* PR review。
* 大改动前的风险评估。
* Codex 自动实现后复核。

---

### 3. `impl_worker`

用途：执行小范围实现，允许写文件，但应严格控制修改范围。

适合模型：

```toml
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"
```

示例：

```toml
name = "impl_worker"
description = "Implementation-focused worker for small, targeted code changes."
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"

developer_instructions = """
Make the smallest defensible implementation change.
Keep unrelated files untouched.
Prefer surgical patches over broad rewrites.
Run focused validation after edits when possible.
Summarize changed files, validation results, and remaining risks.
"""
```

适用场景：

* 已经明确修复路径的小 patch。
* reviewer / code_mapper 已经给出边界后的实现。
* 避免主模型又探索又实现导致上下文混乱。

---

### 4. `docs_researcher`

用途：查官方文档、API 变更、框架行为、版本兼容性。

适合模型：

```toml
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
```

示例：

```toml
name = "docs_researcher"
description = "Documentation specialist for verifying framework APIs, options, and version-specific behavior."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"

developer_instructions = """
Verify APIs, options, version-specific behavior, and migration notes from official documentation when possible.
Return concise answers with exact references.
Do not edit code.
Clearly mark uncertain or version-dependent conclusions.
"""
```

适用场景：

* Python / CUDA / MLflow / Label Studio / React / TypeScript 等版本敏感问题。
* 不希望主模型凭记忆猜 API。
* 合同设计、schema 设计、平台集成前的官方资料确认。

---

### 5. `test_runner`

用途：执行测试、收集失败日志、缩小失败原因。

适合模型：

```toml
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"
```

示例：

```toml
name = "test_runner"
description = "Validation worker that runs focused tests and summarizes failures."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "workspace-write"

developer_instructions = """
Run only focused validation commands relevant to the change.
Avoid long-running full test suites unless explicitly requested.
Capture exact command, exit code, and important error snippets.
Do not make implementation changes unless explicitly asked.
Return a concise validation report.
"""
```

适用场景：

* 实现后验证。
* CI 失败定位。
* 避免主模型被长日志污染上下文。

## 推荐调用方式

### 代码修改任务

```text
Use subagents before editing:
1. code_mapper: map relevant files and execution paths.
2. reviewer: identify correctness, regression, and test risks.
3. impl_worker: implement the smallest safe change only after mapper and reviewer finish.
4. test_runner: run focused validation after implementation.

Wait for read-only agents first, then implement.
Summarize final changes, tests, and remaining risks.
```

### PR Review 任务

```text
Review this branch against main.

Use:
- code_mapper to map affected files and execution paths.
- reviewer to find correctness, security, compatibility, and missing-test risks.
- docs_researcher to verify external API/framework assumptions when needed.

Do not edit files.
Return findings grouped by severity.
```

### Bug 定位任务

```text
Investigate this bug with subagents:

- code_mapper: trace the likely execution path and state transitions.
- test_runner: reproduce or run focused tests if available.
- reviewer: identify the most likely root cause and regression risk.

Do not edit until the root cause is clear.
After all agents report back, propose the smallest fix.
```

### 文档 / SOP 整理任务

```text
Use subagents:
- docs_researcher: verify official behavior and version-sensitive details.
- reviewer: check whether the proposed SOP is safe, repeatable, and missing edge cases.

Then produce a reusable SOP under the workflow/sop skill structure.
```

## 模型分配建议

| Agent             | 推荐模型           | Reasoning | 权限              | 说明           |
| ----------------- | -------------- | --------: | --------------- | ------------ |
| 主 Agent           | `gpt-5.5`      |      high | 按任务决定           | 负责规划、综合、最终决策 |
| `code_mapper`     | `gpt-5.4-mini` |    medium | read-only       | 快速探索代码结构     |
| `reviewer`        | `gpt-5.5`      |      high | read-only       | 高质量风险审查      |
| `impl_worker`     | `gpt-5.4`      |    medium | workspace-write | 小范围实现        |
| `docs_researcher` | `gpt-5.4-mini` |    medium | read-only       | 查文档、查 API    |
| `test_runner`     | `gpt-5.4-mini` |    medium | workspace-write | 跑测试、收集日志     |

## 设计原则

### 1. Read-only agents 优先

复杂任务不要让实现 agent 直接开改。

推荐顺序：

```text
Explore -> Review -> Implement -> Validate
```

即：

```text
code_mapper -> reviewer -> impl_worker -> test_runner
```

### 2. 高风险任务用强模型审查

以下任务建议让 `reviewer` 使用强模型：

* 数据库 migration。
* 平台 contract / schema。
* 权限 / 安全 / token / secret。
* 并发 / 异步 / 分布式任务。
* 训练平台、任务调度、状态机。
* 影响大量文件的重构。

### 3. 轻量任务用 mini 模型

以下任务适合 mini 模型：

* 文件定位。
* 代码路径 mapping。
* 文档查找。
* 日志摘要。
* 测试结果总结。
* 重复性 batch audit。

### 4. 实现 agent 必须限制范围

`impl_worker` 的指令中应明确：

* smallest defensible change
* keep unrelated files untouched
* no broad rewrite
* run focused validation
* summarize changed files

这样可以降低 Codex 自动扩大修改范围的风险。

### 5. Prompt 中显式指定 agent

不要假设 Codex 一定会自动路由。

推荐在任务开头直接写：

```text
Use subagents:
- code_mapper ...
- reviewer ...
- impl_worker ...
```

并要求：

```text
Wait for read-only agents before editing.
```

## 和 `workflow` / `sop` skill 的关系

建议在 `my-codex` 中这样分层：

```text
skills/
  workflow/
    SKILL.md
    workflows/
      pr-review.md
      bugfix.md
      refactor.md
      docs-audit.md

  sop/
    SKILL.md
    sops/
      safe-code-change.md
      contract-review.md
      dependency-upgrade.md
      mlflow-integration-review.md
```

其中：

* `workflow`：描述较大的任务编排方式，例如 PR review、bugfix、重构。
* `sop`：描述稳定、可重复的标准处理流程，例如安全改代码、合同审查、依赖升级。
* `agents/`：描述可被 Codex 委派的执行角色。
* `workflow` 和 `sop` 可以在步骤中要求调用特定 agents。

示例：

```markdown
## Safe Code Change SOP

1. Use `code_mapper` to locate affected paths.
2. Use `reviewer` to identify correctness and regression risks.
3. Only then use `impl_worker` to make the smallest change.
4. Use `test_runner` for focused validation.
5. Summarize:
   - changed files
   - validation commands
   - remaining risks
```

## 推荐落地顺序

第一阶段先实现最小可用 agent 集合：

```text
.codex/
  config.toml
  agents/
    code-mapper.toml
    reviewer.toml
    impl-worker.toml
```

第二阶段再补：

```text
agents/
  docs-researcher.toml
  test-runner.toml
```

第三阶段把 workflow / sop 接入：

```text
skills/
  workflow/
  sop/
```

## 当前建议

对于 `my-codex`，建议把 Codex route 机制定义为：

> Explicit Subagent Delegation with Per-Agent Model Configuration

即：

> 显式 Subagent 委派 + 每个 Agent 独立模型配置。

不要命名为完全自动 routing，避免误导。

推荐文档命名：

```text
docs/codex-model-routing.md
docs/subagent-design.md
docs/workflow-and-sop-design.md
```

推荐核心口径：

```text
Codex supports role-based model routing through custom subagents.
Each agent can pin its own model, reasoning effort, sandbox mode, tools, and instructions.
The parent agent remains responsible for planning and delegation.
For reliable behavior, workflows should explicitly name which subagents to use and when.
```

[1]: https://developers.openai.com/codex/subagents "Subagents – Codex | OpenAI Developers"
[2]: https://blog.csdn.net/dahuoji0917/article/details/161025776 "Codex 明明支持 Subagent，为什么却不会主动用？我做了个 Skill 来解决这个问题"
