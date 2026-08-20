# Universal Agent Skills Phase 1b Execution Prompt

你正在处理仓库：

```text
/home/aefv/.codex/my-codex
```

本轮任务：继续完成 my-codex universal Agent Skills 迁移的 Phase 1b，并把当前 Draft PR #4 推进到“可独立合并”的状态。

## 当前已完成基线

远端 `main` 已包含并冻结上一轮 slimming 结果：

- PR #3 已合并；
- main merge commit：
  `8e29df2faeffb2b0dc3a8b202e3293d00ce2191a`

当前 universalization 工作分支：

```text
agent/universal-skill-profiles
```

当前 Draft PR：

```text
PR #4
Derive universal skill discovery from repository source
```

PR #4 当前已包含 Phase 1：

- `scripts/repo_skill_catalog.py`
- `scripts/skill_discovery_profiles.py`
- `scripts/check_skill_discovery.py`
- 已重构的 `scripts/sync_agents_skills.py`
- 对应 focused tests
- `docs/todo/universal-agent-skills-migration.md`
- `docs/todo/universal-skill-profiles-validation.md`
- `docs/todo/README.md` 索引更新

Phase 1 的架构结论已经冻结：

1. Git repository 是唯一 skill source authority。
2. 当前 `plugins/*/skills` 物理布局暂时保留。
3. `SKILL.md` frontmatter `name` 是 universal callable identity。
4. `~/.agents/skills` 是 repo-managed discovery projection，不是第二份源码或 cache。
5. Codex marketplace/plugin 是 optional adapter/distribution。
6. 同一运行环境只能有一个 active skills discovery profile：
   - `universal`
   - `plugin`
7. 不允许 universal links 和 skills-bearing plugin cache 同时注入相同 skills。
8. 不建立第二份手工维护的 skill catalog。
9. 不重命名现有 callable identity、Watcher namespaced identity 或 plugin identity。
10. Matt Pocock mirror 内容保持不变。

当前 canonical design：

```text
docs/todo/universal-agent-skills-migration.md
```

请以该文档为迁移权威，不要新建第二份 universalization design。

## 当前关键 blocker

PR #4 目前不能单独合并。

原因：

Phase 1 的 `scripts/sync_agents_skills.py` 已要求显式：

```text
--profile universal
```

或：

```text
--profile plugin
```

但当前：

```text
scripts/refresh_my_codex.py
scripts/check_my_codex.py
scripts/upgrade_my_codex.sh
scripts/upgrade_my_codex.ps1
```

仍按旧接口调用它。

因此如果直接合并当前 PR #4，会破坏现有 refresh/check workflow。

本轮核心目标就是完成这一 integration gap。

---

# 本轮核心目标

完成 Phase 1b：

```text
explicit discovery profile
+ profile-aware refresh
+ profile-aware closure check
+ wrapper propagation
+ transition-order validation
```

使 PR #4 在“不执行真实 runtime cutover”的前提下成为一个内部一致、可独立合并的源码变更。

---

# 开始前必须核实 live state

不要相信旧会话中的本地状态。

至少执行并记录：

```bash
pwd
realpath .
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short
git status --branch --short
git remote -v
git log --oneline --decorate -10
```

确认：

- 当前是否已经在 `agent/universal-skill-profiles`；
- HEAD 是否与远端 PR #4 head 一致；
- 是否存在用户未提交改动；
- 不覆盖、不 reset、不 clean 任何非本任务 dirty work。

如果工作树存在 unrelated dirty changes：
- 保留；
- 缩小本轮改动路径；
- 不使用 `git reset --hard`、`git clean` 或广域 restore。

---

# Phase 1b 已有候选补丁

如果以下文件可访问：

```text
my-codex-universal-phase-1b-only.patch
```

优先将它作为候选输入，而不是重新从零设计。

先：

```bash
git apply --check /path/to/my-codex-universal-phase-1b-only.patch
```

检查 patch 是否与当前 PR #4 HEAD 干净兼容。

如果兼容，可以应用：

```bash
git apply /path/to/my-codex-universal-phase-1b-only.patch
```

如果该 patch 是 `git format-patch` 形式，则按实际格式选择：

```bash
git am ...
```

不要为了套 patch 而覆盖当前有效改动。

如果 patch 已与当前 branch 漂移，则：
- 把 patch 当 design/reference；
- 按当前源码重新实现相同语义；
- 不机械解决冲突。

---

# Phase 1b 必须实现的语义

## 1. 显式 discovery profile

新增一个共享、单一 owner 的 profile policy，避免 refresh/check/wrapper 各自重新实现一套规则。

支持且仅支持：

```text
universal
plugin
```

优先考虑：

```text
--discovery-profile universal
--discovery-profile plugin
```

同时可允许一个明确环境变量作为 wrapper-to-helper 传递，例如：

```text
MY_CODEX_DISCOVERY_PROFILE
```

但必须满足：

- CLI 显式值优先；
- 没有 CLI 也没有环境变量时 fail closed；
- 不允许隐式恢复旧“双路径同时 active”的默认行为；
- profile 解析逻辑只存在一个 authoritative implementation。

---

# 2. Universal profile

目标：

```text
repo skill source
→ ~/.agents/skills
```

Universal profile 必须：

- 不要求 marketplace 存在；
- 不要求 plugin cache 存在；
- 不运行 `codex plugin add`；
- 不把 plugin cache identity 当 closure 条件；
- 不允许 skills-bearing `my-codex` plugins 同时 enabled；
- 如需从当前 plugin profile 转 universal：
  1. 先完整 preflight universal projection：
     - source catalog 可解析；
     - 无 duplicate frontmatter identity；
     - 无 unmanaged same-name target；
     - stale/owned links 可判定；
  2. 精确识别当前 enabled skills-bearing my-codex plugins；
  3. 精确 remove/disable 这些 plugins；
  4. 确认不会再从 plugin path 注入；
  5. 再创建/修复 `~/.agents/skills` repo-owned links；
  6. 最后运行 universal closure check。

不得存在：

```text
先建 universal links
再删 plugin
```

这种临时双重注入窗口。

如果 Codex CLI 不存在，但当前本来就是 clean universal profile：
- refresh/check 不应仅因为 marketplace/plugin CLI 不可用而失败；
- 只有实际需要移除 enabled skills plugin 时才要求 Codex plugin remove capability。

---

# 3. Plugin profile

目标：

```text
Codex skills-bearing plugin adapter
```

Plugin profile 必须：

1. 先验证 adapter/package 输入完整：
   - marketplace metadata；
   - install manifest；
   - source plugin manifests；
   - 需要的 Codex CLI capability；
   - 可验证的 plugin package/cache contract。
2. 然后删除本仓库拥有的 `~/.agents/skills` links。
3. 再执行 marketplace/plugin install/refresh。
4. 最后验证：
   - required skills-bearing plugins enabled；
   - exact source/cache identity；
   - 每个 enabled plugin 只有一个有效 cache version；
   - cached skill set 与 repo canonical skill group 一致；
   - repo-owned universal links 已不存在。

不得出现：

```text
先删 universal links
→ 后发现 plugin package 无法安装
→ 环境变成没有任何 discovery path
```

因此 plugin transition 必须先完成足够的 adapter preflight。

---

# 4. Bypass 参数处理

检查旧参数：

```text
--skip-marketplace
--skip-plugins
--skip-agents-skills
--prune-plugins
```

新的 profile contract 不能被这些 flag 绕过。

例如：

- universal profile 不能通过 `--skip-agents-skills` 绕过 universal discovery；
- plugin profile 不能通过 `--skip-plugins` 留下“无 plugin + 无 universal links”的状态；
- 不允许组合参数重新制造 dual-active state。

如果旧 flag 与显式 profile 语义冲突：
- fail closed；
- 给出明确错误；
- 不静默 reinterpret。

可以保留与 profile 不冲突的低层 flag，但必须证明不会削弱 profile invariant。

---

# 5. `check_my_codex.py`

把 closure check 从：

```text
marketplace + exact plugin cache + ~/.agents/skills
全部同时存在
```

改为：

```text
根据 explicit profile 选择 closure oracle
```

Universal：

```text
repo catalog valid
+ universal projection exact
+ no enabled skills-bearing plugin
+ no duplicate discovery path
```

Plugin：

```text
repo catalog valid
+ no repo-owned universal projection
+ expected plugins enabled
+ exact plugin/cache identity
+ cached skills == canonical source skills
```

注意：

- repo source 永远是比较权威；
- plugin cache 只是 plugin profile 的 projection；
- universal profile 不需要 cache；
- disabled stale cache 可以 warning，但不能被当作 active duplicate；
- enabled unknown `my-codex` plugin 必须 fail closed，除非以后有明确的 zero-skill adapter classification。

---

# 6. Platform wrappers

必须同步处理：

```text
scripts/upgrade_my_codex.sh
scripts/upgrade_my_codex.ps1
```

至少做到：

- 接受显式 discovery profile；
- 把同一个 profile 传给 refresh 和 check；
- help 文档更新；
- 日志打印当前 profile；
- 缺少 profile 时 fail closed，而不是偷偷选旧 plugin 模式；
- Unix 与 PowerShell 行为一致。

建议接口：

Unix：

```bash
scripts/upgrade_my_codex.sh --discovery-profile universal
```

PowerShell：

```powershell
.\scripts\upgrade_my_codex.ps1 -DiscoveryProfile universal
```

也可以复用环境变量，但 wrapper 最终必须显式把 resolved profile 传给两个 Python helpers。

---

# 7. 保持以下内容不变

本轮不要修改：

- 任意 `SKILL.md` 正文；
- 当前 slimming 结果；
- Matt Pocock skill mirror；
- skill frontmatter invocation identities；
- Watcher namespaced identities；
- `.codex-plugin/skill-watcher.json` attribution semantics；
- Watcher metadata discovery internals；
- Watcher shared runtime 定位；
- hook schema；
- real `~/.agents/skills`；
- real plugin cache；
- real Codex config；
- marketplace installation state。

Watcher marketplace-independent metadata 是后续 Phase 2，不要混进本轮。

---

# 测试要求

优先复用已有 Phase 1/Phase 1b focused tests。

至少覆盖：

## Profile policy

- missing profile fails closed；
- invalid profile fails；
- CLI profile 优先于环境变量；
- universal 与 plugin mutually exclusive。

## Universal

- fresh universal environment 不要求 Codex CLI；
- fresh universal environment 不要求 marketplace/cache；
- enabled skills-bearing plugin 阻止直接建 links；
- transition 顺序为：
  `preflight -> plugin remove -> universal link create`；
- plugin remove 失败时 universal links 不写入；
- unmanaged same-name target 不覆盖。

## Plugin

- universal links 存在时不能直接完成 plugin closure；
- transition 顺序为：
  `adapter preflight -> universal links deactivate -> plugin activation`；
- preflight 失败时 universal links 保留；
- plugin activation 失败必须报告明确 breakpoint；
- plugin closure 验证 exact cache/source skill set。

## Bypass

- `--skip-agents-skills` 不能绕过 profile contract；
- `--skip-plugins` 不能绕过 plugin profile；
- 其他旧参数不能产生 dual-active/zero-active 状态。

## Wrapper

- Unix wrapper 将 profile 传给 refresh；
- Unix wrapper 将同一 profile 传给 check；
- PowerShell 同样；
- missing profile 报错；
- help 包含 profile 说明。

---

# 建议测试命令

至少运行：

```bash
python3 -m unittest -v \
  tests.test_repo_skill_catalog \
  tests.test_skill_discovery_profiles \
  tests.test_sync_agents_skills \
  tests.test_discovery_profile_runtime \
  tests.test_refresh_discovery_profile \
  tests.test_check_discovery_profile \
  tests.test_refresh_profile_integration \
  tests.test_check_my_codex \
  tests.test_upgrade_my_codex
```

并运行仓库现有相关测试：

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s plugins/workflow/tests -p 'test_*.py' -v
python3 -m unittest discover -s plugins/watcher/tests -p 'test_*.py' -v
```

如果完整 suite 因环境缺少 Codex/plugin validator 等外部依赖失败：

- 区分真实代码失败与环境缺失；
- 不伪造通过；
- 记录准确 breakpoint。

静态验证：

```bash
python3 -m py_compile \
  scripts/repo_skill_catalog.py \
  scripts/skill_discovery_profiles.py \
  scripts/check_skill_discovery.py \
  scripts/sync_agents_skills.py \
  scripts/discovery_profile_runtime.py \
  scripts/refresh_my_codex.py \
  scripts/check_my_codex.py

git diff --check
```

如仓库有 shell/PowerShell focused tests，也必须执行。

---

# Read-only real-state inventory

本轮可以读取真实状态，但不要 cutover。

在完成源码候选后，执行 read-only inventory：

```bash
python3 scripts/check_skill_discovery.py \
  --profile universal \
  --repo-root "$PWD" \
  --agents-root "$HOME/.agents/skills" \
  --codex-home "${CODEX_HOME:-$HOME/.codex}" \
  --json
```

以及：

```bash
python3 scripts/check_skill_discovery.py \
  --profile plugin \
  --repo-root "$PWD" \
  --agents-root "$HOME/.agents/skills" \
  --codex-home "${CODEX_HOME:-$HOME/.codex}" \
  --json
```

这些命令在迁移前允许失败。

目标是记录：

- 当前 active profile 更接近哪种状态；
- 当前是否 dual-active；
- 哪些 repo-owned links 存在；
- 哪些 unmanaged conflicts 存在；
- 哪些 my-codex plugins enabled；
- 哪些 cache versions 存在；
- 是否存在 unknown/unclassified plugin；
- 下一次真实 cutover 前需要处理的 blocker。

不要因此自动修改安装态。

---

# 独立 review

由于 Phase 1b 会改变：

- discovery routing；
- plugin removal ordering；
- active-path mutual exclusion；
- closure oracle；

在最终标记 PR ready 前，需要一次独立只读 review。

Review 至少检查：

1. 是否存在瞬时 dual-active window；
2. 是否存在瞬时 zero-active window；
3. failure 是否会留下不可恢复的中间状态；
4. 是否可能删掉 unmanaged `~/.agents/skills`；
5. 是否可能误删其他 marketplace/plugin；
6. universal 是否真正不依赖 cache/marketplace；
7. plugin 是否仍以 repo source 为比较权威；
8. invocation identity 是否完全未变；
9. slimming skill 内容是否完全未变。

如果环境不支持 subagent，不要因为缺 subagent 阻塞本轮；可以做单 agent 的独立第二遍只读 contract review，但必须明确说明 reviewer independence 的限制。

---

# Git / PR 边界

当前目标 PR：

```text
#4 Derive universal skill discovery from repository source
```

优先继续使用现有：

```text
agent/universal-skill-profiles
```

不要创建第二个 competing universalization PR。

完成 Phase 1b 后：

1. 查看 scoped diff；
2. 确认没有 skill 内容变化；
3. commit Phase 1b，建议独立语义 commit；
4. 如 wrapper 改动较大，可再拆一个 wrapper commit；
5. push 到同一 branch；
6. 更新 PR #4 body；
7. 所有 source/integration tests 和 independent review 通过后，才把 PR 从 Draft 标记 Ready。

本轮授权可以：
- 修改源码；
- 修改 tests；
- 修改当前 canonical migration/validation 文档；
- commit；
- push；
- 更新 PR #4。

本轮不要：
- merge PR #4；
- 修改真实 runtime/install state；
- 删除 plugin/cache；
- 执行 marketplace cutover。

---

# 文档更新

更新：

```text
docs/todo/universal-agent-skills-migration.md
docs/todo/universal-skill-profiles-validation.md
```

只更新当前 implementation state：

例如从：

```text
Phase 1 implemented
Phase 1b pending
```

变为：

```text
Phase 1 implemented
Phase 1b implemented and source-validated
runtime cutover not started
```

不要创建新的 universalization authority 文档。

---

# 完成标准

本轮完成时应达到：

```text
PR #4 source tree internally consistent
```

具体：

- `sync_agents_skills.py` 新接口已有所有调用者；
- refresh/check/wrappers 都要求同一 explicit profile；
- universal 与 plugin profile 在源码层严格互斥；
- universal 不依赖 marketplace/cache；
- plugin profile 不允许 repo-owned universal links；
- transition ordering fail closed；
- old skip flags 不能绕过 profile contract；
- relevant tests pass；
- real environment read-only inventory 已记录；
- slimming baseline 未变化；
- runtime cutover 未执行；
- PR #4 仍未 merge。

最终报告请按以下格式：

1. Phase 1b 实现了什么；
2. transition ordering 如何保证不会双重注入；
3. 测试结果；
4. real environment 当前 discovery 状态；
5. PR #4 当前是否已具备 Ready 条件；
6. 仍未执行的 runtime cutover；
7. 下一步最小任务：Phase 2 Watcher metadata/shared-runtime 解耦，还是先执行一次受控 universal cutover。

如果真实证据显示 Phase 1b 设计存在问题，优先修设计，不要为了让 PR 变绿而增加 fallback、dual-read、compatibility shim 或第二套 catalog。
