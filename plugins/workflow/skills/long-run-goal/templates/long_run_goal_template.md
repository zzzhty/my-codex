# Long Run Goal Template

本文件是 long-running goal 文档模板。使用时复制到项目的 active goal directory，例如 `<goal-dir>/<goal_slug>_long_run_goal_plan.md`，再替换所有 `<...>` 占位符；不要直接在本模板中记录具体任务进度。

整体状态：`Draft`

## 使用说明

1. 先确认项目已有的 planning root 和 goal directory。`<planning-root>` 是更大的文档/计划树；`<goal-dir>` 是直接存放 active goal 文件的目录。不要对已经是 goal directory 的路径再追加 `/todo`。
2. 复制本文件到目标计划路径，例如：

```bash
cp <skill-folder>/templates/long_run_goal_template.md <goal-dir>/<goal_slug>_long_run_goal_plan.md
```

3. 将标题、目标描述、目标路径、阶段名称、验证命令和 checkpoint evidence 替换为当前任务内容。
4. 执行过程中只更新复制后的 goal 文件，不更新本模板。
5. 每个阶段完成后必须补齐代码证据、行为证据、测试证据、文档证据、回滚证据和剩余风险。
6. 按任务规模增删 `M<N>` 阶段；删除不用的阶段，按顺序新增需要的阶段，并同步更新阶段状态表、Checkpoint evidence、Close Gate 和推荐 Goal Prompt。
7. Close 前必须确认所有阶段 `Done`，并记录最终验证结果。

## Goal 摘要

目标名称：`<Goal Name>`

目标描述：

1. `<用 1-3 条描述本 goal 要完成什么。>`
2. `<说明最终用户或系统行为的目标态。>`
3. `<说明不属于本 goal 的边界。>`

目标状态：`Draft`

目标 owner：`<owner / team / agent>`

目标路径：`<goal-dir>/<goal_slug>_long_run_goal_plan.md`

Planning root：`<planning-root>`

Goal directory：`<goal-dir>`

## M0 执行前基线

M0 设计冻结时的当前基线：

1. `<当前代码 / 文档 / runtime 的事实 1。>`
2. `<当前已交付或已验证的能力。>`
3. `<当前仍保留的 compatibility / legacy surface。>`
4. `<当前主要失败断点或风险。>`
5. `<当前不属于本计划提交范围的运行产物或外部依赖。>`

已读取的当前事实源：

1. `<root instructions / AGENTS.md / README / current guide / status doc。>`
2. `<相关 architecture / contract / validation / runbook。>`
3. `<现有 TODO / goal / archive / issue / PR。>`

## Goal 执行合同

如果本计划被作为 long-running goal 执行，必须按以下合同推进：

1. 阶段必须顺序执行：`M0 -> M1 -> M2 -> ... -> Close`。
2. 每个阶段开始前必须把阶段状态改为 `In Progress`。
3. 每个阶段完成后必须记录 review 结论、运行命令、通过证据、失败断点和未解决风险。
4. 每个阶段必须有 checkpoint evidence。若项目已有 Git / version-control 工作流且用户或项目要求阶段性提交，优先使用本计划中记录的 `<goal_slug> M<N>: <summary>` 或本项目约定格式作为 commit/revision 证据；非 VCS 环境不得强行初始化 Git 或伪造 commit。
5. 未满足当前阶段 Review gate 时，不得进入下一阶段。
6. 任何阶段失败必须停在失败点，记录 root cause、失败命令、文件路径、已知 breakpoint 和下一步修复建议。
7. 不允许用 silent fallback、兼容假成功、部分成功包装、alternate backend、隐藏错误或 silent degradation 来绕过 gate。
8. 不允许把 legacy / deprecated surface 重新包装成当前产品语义，除非本 goal 明确要求并完成文档更新。
9. 若执行过程中发现 gate、验证规则、回滚路径、阶段边界或 long-run-goal 策略不够严谨，必须先暂停实现，记录暴露该问题的证据，更新 reusable strategy 或本计划合同，再完成相关验证后回到原阶段继续；不得在实现完成后静默放宽验收标准。
10. 若上下文压缩、中断或用户新请求改变了任务方向，必须先按最新请求重新确认是否继续本 goal；若最新请求转为 planning、explanation、alignment、skill editing、review-only、git maintenance 或其他独立任务，不得继续旧阶段执行，也不得更新旧 goal 证据。
11. Close 只能在所有阶段 `Done` 且完成标准全部有代码、测试和文档证据后执行。

## 状态定义

| 状态 | 含义 |
|---|---|
| `Draft` | 设计仍需补充，不能执行实现 |
| `Ready` | 设计与验收指标已明确，可以开始该阶段 |
| `Not Started` | 该阶段尚未开始，且必须等待前置阶段 Done |
| `In Progress` | 当前阶段正在实现或验证 |
| `Blocked` | 当前阶段因明确失败或未决设计被阻塞 |
| `Done` | 阶段 Review gate、量化验收和 checkpoint evidence 均已完成 |
| `Closed` | 仅用于整体计划完成后关闭并从 active TODO/goal 导航移除 |

## 全局验收规则

每个阶段的验收至少包含：

1. 代码证据：列出新增、修改或删除的关键文件。
2. 行为证据：说明 API / UI / migration / runtime 行为是否变化。
3. 测试证据：列出实际执行命令和结果；不能只写“应当通过”。
4. 文档证据：同步更新本文件状态表，并按需更新 active current docs。
5. 回滚证据：说明该阶段如何回滚，migration 阶段必须说明正反向策略。
6. 风险证据：列出仍保留的 legacy compatibility、未解决风险和下一阶段要消除的部分。

默认验证命令：

```bash
git diff --check -- <changed-paths>
```

按改动类型追加验证：

1. 涉及 Python / backend model / serializer / API / migration：运行相关 test 和 migration check。
2. 涉及前端页面、route、wire shape 或交互：运行 targeted unit / browser / Playwright validation。
3. 涉及 runtime user flow、proxy、container、fixture 或 browser gate：运行对应 runtime diagnostics。
4. 涉及 shell / PowerShell / batch / Python scripts：运行对应语法检查和 dry-run。
5. 涉及 docs-only：至少运行 `git diff --check -- <changed-paths>`，并确认链接与事实源不冲突。

## 设计原则

1. `<原则 1：领域 ownership 或模块边界。>`
2. `<原则 2：API / UI / runtime 行为边界。>`
3. `<原则 3：compatibility / legacy 处理原则。>`
4. `<原则 4：failure handling 和 fail-fast 规则。>`
5. `<原则 5：测试与验证边界。>`

## 目标结构

### `<Target Area 1>`

1. `<目标态 1。>`
2. `<目标态 2。>`
3. `<必须保留的兼容边界。>`
4. `<必须移除或禁止恢复的旧行为。>`

### `<Target Area 2>`

1. `<目标态 1。>`
2. `<目标态 2。>`
3. `<风险或后续 Future 边界。>`

## 非目标 / Future 边界

本 goal 不处理：

1. `<明确不处理的事项 1。>`
2. `<明确不处理的事项 2。>`
3. `<明确不处理的事项 3。>`

## 阶段计划

本模板默认给出 `M0`、`M1`、`M2` 三个阶段作为示例。创建具体 goal 时，应按实际任务规模增删阶段：

1. 保留 `M0` 作为执行前基线 / contract review / design freeze，除非本项目已有等价阶段。
2. 删除不需要的示例阶段，不要留下空的占位阶段。
3. 新增阶段时按 `M3`、`M4` 继续编号，并复制完整的范围、Review gate、执行证据、推荐验证和 Checkpoint evidence 结构。
4. 每次增删阶段后，同步更新“阶段状态表”和“推荐 Goal Prompt”里的阶段顺序要求。

### M0 - `<阶段名称>`

状态：`Ready`

范围：

1. `<本阶段要做的事情 1。>`
2. `<本阶段要做的事情 2。>`
3. `<本阶段不做的事情。>`

Review gate：

1. `<必须满足的验收条件 1。>`
2. `<必须满足的验收条件 2。>`
3. `<必须满足的验收条件 3。>`

执行证据：

1. 代码证据：
   - `<完成后填写关键文件和改动。>`
2. 行为证据：
   - `<完成后填写行为变化或无行为变化说明。>`
3. 测试证据：
   - `<完成后填写实际命令和结果。>`
4. 文档证据：
   - `<完成后填写文档同步情况。>`
5. 回滚证据：
   - `<完成后填写回滚方式。>`
6. 剩余风险：
   - `<完成后填写残留风险。>`

推荐验证：

```bash
git diff --check -- <changed-paths>
<additional-command-if-needed>
```

Checkpoint evidence：

```text
<Git commit / revision / issue history / document revision / artifact path / Not applicable: no VCS in this workspace>
```

### M1 - `<阶段名称>`

状态：`Not Started`

范围：

1. `<本阶段要做的事情 1。>`
2. `<本阶段要做的事情 2。>`
3. `<本阶段不做的事情。>`

Review gate：

1. `<必须满足的验收条件 1。>`
2. `<必须满足的验收条件 2。>`
3. `<必须满足的验收条件 3。>`

执行证据：

1. 代码证据：
   - `<完成后填写关键文件和改动。>`
2. 行为证据：
   - `<完成后填写行为变化或无行为变化说明。>`
3. 测试证据：
   - `<完成后填写实际命令和结果。>`
4. 文档证据：
   - `<完成后填写文档同步情况。>`
5. 回滚证据：
   - `<完成后填写回滚方式。>`
6. 剩余风险：
   - `<完成后填写残留风险。>`

推荐验证：

```bash
git diff --check -- <changed-paths>
<additional-command-if-needed>
```

Checkpoint evidence：

```text
<Git commit / revision / issue history / document revision / artifact path / Not applicable: no VCS in this workspace>
```

### M2 - `<阶段名称>`

状态：`Not Started`

范围：

1. `<本阶段要做的事情 1。>`
2. `<本阶段要做的事情 2。>`
3. `<本阶段不做的事情。>`

Review gate：

1. `<必须满足的验收条件 1。>`
2. `<必须满足的验收条件 2。>`
3. `<必须满足的验收条件 3。>`

执行证据：

1. 代码证据：
   - `<完成后填写关键文件和改动。>`
2. 行为证据：
   - `<完成后填写行为变化或无行为变化说明。>`
3. 测试证据：
   - `<完成后填写实际命令和结果。>`
4. 文档证据：
   - `<完成后填写文档同步情况。>`
5. 回滚证据：
   - `<完成后填写回滚方式。>`
6. 剩余风险：
   - `<完成后填写残留风险。>`

推荐验证：

```bash
git diff --check -- <changed-paths>
<additional-command-if-needed>
```

Checkpoint evidence：

```text
<Git commit / revision / issue history / document revision / artifact path / Not applicable: no VCS in this workspace>
```

## 阶段状态表

| 阶段 | 状态 | Review | Checkpoint |
|---|---|---|---|
| M0 `<阶段名称>` | Ready | Pending | Pending |
| M1 `<阶段名称>` | Not Started | Pending | Pending |
| M2 `<阶段名称>` | Not Started | Pending | Pending |
| Close | Not Started | Pending | Pending |

## Close Gate

Close 前必须满足：

1. 所有阶段均为 `Done`。
2. 所有 Review gate 均为 `Passed`。
3. 所有 checkpoint evidence 均已完成并记录。
4. active current docs、validation log、runtime/test checklist 或相关索引已同步。
5. 所有必须执行的测试命令均记录实际结果。
6. `git diff --check -- <changed-paths>` 通过。
7. Markdown 链接检查按需通过。
8. 未解决风险已记录，并明确是否进入 Future。
9. close checkpoint evidence 已记录；若项目已有 Git / version-control 工作流且要求 close commit，使用 `<goal_slug> close: <summary>` 或本项目约定格式。

Close 执行证据：

1. 代码证据：
   - `<Close 时填写最终关键文件。>`
2. 行为证据：
   - `<Close 时填写最终行为结论。>`
3. 测试证据：
   - `<Close 时填写最终命令和结果。>`
4. 文档证据：
   - `<Close 时填写文档同步。>`
5. 回滚证据：
   - `<Close 时填写整体回滚策略。>`
6. 剩余风险：
   - `<Close 时填写 Future / residual risk。>`

Checkpoint evidence：

```text
<Git commit / revision / issue history / document revision / artifact path / Not applicable: no VCS in this workspace>
```

## 当前风险

1. `<执行前已知风险 1。>`
2. `<执行前已知风险 2。>`
3. `<执行前已知风险 3。>`

## 推荐 Goal Prompt

```text
请按照 <goal-dir>/<goal_slug>_long_run_goal_plan.md 执行 <Goal Name>。

执行要求：
1. 阶段必须顺序执行，不得跳过 gate。
2. 每个阶段开始前把该阶段状态改为 In Progress，完成后记录代码证据、行为证据、测试证据、文档证据、回滚证据和剩余风险。
3. 每个阶段都必须有 checkpoint evidence；若项目已有 Git / version-control 工作流且用户或项目要求阶段性提交，使用本 goal 记录的 <goal_slug> M<N>: <summary> 或本项目约定格式作为 commit/revision 证据；非 VCS 环境不得强行初始化 Git 或伪造 commit。
4. 失败时停在失败点，报告 root cause、失败命令、文件路径、已知 breakpoint 和下一步修复建议。
5. 不允许使用 fallback、兼容假成功、alternate backend、部分成功包装、隐藏错误或 silent degradation 来绕过 gate。
6. Close 前必须运行并记录 git diff --check -- <changed-paths> 以及本 goal 指定的所有验证命令。
```

## 相关文档

1. `<相关 current doc 1>`
2. `<相关 current doc 2>`
3. `<相关 architecture / API / validation / runbook doc>`
