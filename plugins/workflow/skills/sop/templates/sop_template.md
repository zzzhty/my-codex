# SOP: <SOP Name>

状态：`Draft`

## 摘要

SOP 名称：`<SOP Name>`

SOP 路径：`<sop-path>`

Owner：`<owner / team / agent>`

适用场景：

1. `<什么时候使用本 SOP。>`
2. `<本 SOP 要稳定复用的流程。>`

不适用场景：

1. `<明确不适用场景。>`
2. `<需要改用 long-running-goal / report / automation 的场景。>`

## 触发条件

1. `<用户请求中的触发语义。>`
2. `<定期 / 手动 / 事件触发条件。>`

## 前置条件

1. `<需要存在的文件、目录、环境变量或权限。>`
2. `<需要先读取的事实源。>`
3. `<不能缺失的输入。>`

## 工作目录

```text
<working-directory>
```

## 输入

| 输入 | 必需 | 来源 | 校验方式 |
|---|---:|---|---|
| `<input>` | 是/否 | `<user / file / command>` | `<validation>` |

## 允许动作

1. `<允许读取哪些文件。>`
2. `<允许运行哪些命令。>`
3. `<允许修改哪些文件或状态。>`

## 禁止动作

1. `<禁止发送外部消息、删除、发布、重置、迁移等。>`
2. `<没有明确授权时禁止的动作。>`

## 标准步骤

### Step 1 - `<步骤名称>`

目的：`<目的>`

操作：

```bash
<command-or-action>
```

预期输出：

```text
<expected-output>
```

失败处理：

```text
<stop / retry once / collect diagnostics / escalate>
```

### Step 2 - `<步骤名称>`

目的：`<目的>`

操作：

```bash
<command-or-action>
```

预期输出：

```text
<expected-output>
```

失败处理：

```text
<stop / retry once / collect diagnostics / escalate>
```

## 验证标准

1. `<必须通过的命令或检查。>`
2. `<必须存在的报告、diff、截图或 artifact。>`
3. `<必须同步的文档或状态。>`

## 输出合同

执行完成后必须报告：

1. `<完成了什么。>`
2. `<实际读取或修改的路径。>`
3. `<实际运行的命令和结果。>`
4. `<生成的报告或 artifact 路径。>`
5. `<未解决风险或下一步。>`

## 停止条件

必须停止并报告 blocker 的情况：

1. `<缺少必要输入。>`
2. `<验证失败。>`
3. `<权限或工具不可用。>`
4. `<请求超出允许动作。>`
5. `<事实源与 SOP 假设冲突。>`

## 更新规则

修改本 SOP 时必须：

1. 保留当前已验证命令，除非有新证据替代。
2. 记录为什么流程变化。
3. 同步相关 README、runbook、automation memory 或 skill 文档。
4. 重新运行 SOP ready/link 检查。

## 复用 Prompt

```text
Use $sop to execute <SOP Name> at <sop-path>. Follow the SOP exactly, stop on failed required validation, do not perform forbidden actions, and report commands, outputs, changed paths, generated artifacts, and unresolved blockers.
```
