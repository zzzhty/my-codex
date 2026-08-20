# Universal Agent Skills M1 / Phase 1b Execution Prompt

你正在处理仓库：

```text
/home/aefv/.codex/my-codex
```

本轮只执行 long-running goal 的 M1：

```text
docs/todo/universal-agent-skills-migration.md
```

目标是把归档的 Phase 1 原型与 Phase 1b 集成为一个内部一致、可独立合并、但不执行真实 runtime cutover 的源码批次。

## 开始前必须读取

1. `AGENTS.md`
2. `docs/todo/universal-agent-skills-migration.md`
3. `docs/todo/README.md`
4. `scripts/sync_agents_skills.py`
5. `scripts/refresh_my_codex.py`
6. `scripts/check_my_codex.py`
7. `scripts/upgrade_my_codex.sh`
8. `scripts/upgrade_my_codex.ps1`
9. 相关 tests、marketplace/install manifest、plugin manifests
10. 归档原型分支：

```text
archive/universal-phase1-candidate-20260820
```

归档分支是 prototype evidence，不是 merge-ready source。不要把它整分支直接合并进 `main`。

如本地仍有以下候选补丁，可把它作为参考或应用候选：

```text
my-codex-universal-phase-1b-only.patch
```

必须先在当前分支执行 `git apply --check`；不兼容时按当前源码重新实现，不要为了套补丁覆盖有效改动。

## 当前冻结架构

1. Git repository 是唯一 skill source authority。
2. 当前 canonical physical layout 仍是 `plugins/*/skills/*`。
3. `SKILL.md` frontmatter `name` 是 universal callable identity。
4. `~/.agents/skills` 是 repo-managed discovery projection，不是源码或 cache。
5. Codex marketplace/plugin 是 optional adapter/distribution。
6. 同一运行环境只能有一个 active skills discovery profile：
   - `universal`
   - `plugin`
7. 不允许 universal links 与 skills-bearing plugin 同时注入同名 skills。
8. 不新增第二份手工维护的 skill catalog。
9. 不重命名 callable identity、Watcher namespaced identity 或 plugin identity。
10. 不修改 Matt Pocock mirror skill 内容。
11. 当前 slimming 结果是冻结基线，不重新 slimming。

## 开始前 live state

不要相信旧会话中的本地 HEAD、dirty scope 或分支状态。至少执行：

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
git branch -a --list '*universal*'
```

规则：

- 从当前 `main` 创建新的 M1 实现分支；不要复用已关闭的计划 PR 分支作为源码实现分支。
- 建议分支名：

```text
agent/universal-phase1b-integration
```

- 保留所有 unrelated dirty work。
- 不使用 `git reset --hard`、`git clean`、广域 restore 或 `git add -A`。
- 只 stage 本轮确认的路径。

## M1 核心目标

实现并集成：

```text
repository-derived skill catalog
+ explicit discovery profile policy
+ ownership-safe ~/.agents/skills projection
+ profile-aware refresh
+ profile-aware closure check
+ Unix/PowerShell wrapper propagation
+ transition-order validation
```

完成后，任何现有公开 refresh/check/wrapper 入口都不能因为缺少新的 profile 参数而断裂。

## 必须实现的 profile policy

支持且仅支持：

```text
universal
plugin
```

推荐接口：

```text
--discovery-profile universal
--discovery-profile plugin
```

可以支持环境变量：

```text
MY_CODEX_DISCOVERY_PROFILE
```

但必须满足：

- CLI 显式值优先；
- CLI 与环境变量都缺失时 fail closed；
- 不隐式恢复旧“双路径同时 active”默认；
- profile 解析与策略只有一个 authoritative owner；
- refresh、check 和 wrappers 使用同一解析结果。

## Canonical catalog

从以下源码派生：

```text
plugins/*/skills/*/SKILL.md
```

必须：

- 读取 frontmatter `name` 作为 callable identity；
- 允许物理目录名与 callable identity 不同；
- 拒绝重复 identity；
- 拒绝缺失或损坏的 frontmatter / `SKILL.md`；
- 拒绝 skill 目录或文件通过 symlink 逃逸 repo authority；
- 不读取 marketplace/plugin manifest 来决定 universal skill catalog。

## Universal profile

目标：

```text
repository source -> ~/.agents/skills
```

Universal profile 必须：

- 不要求 marketplace 存在；
- 不要求 plugin cache 存在；
- 当前已经是 clean universal profile 时不要求 Codex CLI；
- 不执行 `codex plugin add`；
- 不允许 enabled skills-bearing `my-codex` plugin；
- 只管理指向当前 checkout 直接 skill directory 的 symlink；
- unmanaged 同名目录、文件或外部 symlink 一律 fail closed；
- prune 只删除可证明属于本 checkout 的 stale owned links；
- unrelated user skills 始终保留。

Plugin -> universal 的顺序必须是：

```text
1. preflight canonical catalog and all universal targets
2. identify exact enabled skills-bearing plugins
3. remove/disable those exact plugins
4. verify old active discovery path is inactive
5. create or repair repo-owned universal links
6. run universal closure check
```

不得先创建 links 再删除 plugin，避免瞬时双重注入。

如果 plugin remove 失败：

- 不写入 universal links；
- 报告准确 breakpoint；
- 保留原 active profile。

## Plugin profile

目标：

```text
Codex skills-bearing plugin distribution
```

Plugin profile 必须先完成足够的 adapter/package preflight：

- marketplace metadata；
- install manifest；
- source plugin manifests；
- 所需 Codex CLI capabilities；
- 可验证的 package/cache contract。

Universal -> plugin 的顺序必须是：

```text
1. validate adapter/package inputs and commands
2. confirm replacement can be activated
3. remove only repo-owned universal links
4. install/enable plugin profile
5. verify exact plugin/cache/source identity
6. run plugin closure check
```

不得在 preflight 失败前删除 universal links。

Plugin closure 必须验证：

- required skills-bearing plugins enabled；
- repo-owned universal links 不存在；
- 每个 enabled plugin 只有一个有效 cache version；
- cached skill set 与 canonical source group 完全一致；
- plugin cache 只是 projection，不是比较权威。

## Legacy bypass flags

检查现有：

```text
--skip-marketplace
--skip-plugins
--skip-agents-skills
--prune-plugins
```

新 profile contract 不能被旧 flag 绕过。

至少保证：

- universal profile 不能跳过 universal projection；
- plugin profile 不能跳过 plugin activation；
- 参数组合不能制造 dual-active 或 zero-active 状态；
- 冲突组合明确 fail closed，不静默 reinterpret。

## Closure check

`check_my_codex.py` 必须按 profile 使用不同 oracle。

Universal：

```text
repo catalog valid
+ universal projection exact
+ no enabled skills-bearing my-codex plugin
+ no duplicate active discovery path
```

Plugin：

```text
repo catalog valid
+ no repo-owned universal projection
+ expected plugins enabled
+ exact source/cache identity
+ cached skills == canonical source skills
```

Disabled stale cache 可以 warning，但不能被当作 active duplicate。

Enabled unknown `my-codex` plugin 必须 fail closed，除非未来有已经测试并明确分类的 zero-skill adapter；M1 不引入该例外。

## Platform wrappers

同步更新：

```text
scripts/upgrade_my_codex.sh
scripts/upgrade_my_codex.ps1
```

必须：

- 接受显式 discovery profile；
- 将同一个 resolved profile 传给 refresh 和 check；
- help 与输出包含 profile；
- 缺少 profile 时 fail closed；
- Unix 与 PowerShell 行为一致。

建议调用：

```bash
scripts/upgrade_my_codex.sh --discovery-profile universal
```

```powershell
.\scripts\upgrade_my_codex.ps1 -DiscoveryProfile universal
```

## 本轮禁止修改

- 任意 `SKILL.md` 正文；
- slimming baseline；
- Matt Pocock mirror；
- callable / Watcher / plugin identities；
- Watcher metadata discovery internals；
- Watcher shared runtime 定位；
- hook schema；
- 真实 `~/.agents/skills`；
- 真实 plugin cache；
- 真实 Codex config / hooks / marketplace state。

Watcher marketplace-independent metadata 属于 M2，不混入 M1。

## 测试要求

至少覆盖：

### Profile policy

- missing profile fails closed；
- invalid profile fails；
- CLI profile 优先于环境变量；
- universal / plugin mutually exclusive。

### Universal

- fresh universal 不需要 Codex CLI；
- fresh universal 不需要 marketplace/cache；
- enabled plugin 阻止直接写 links；
- transition 顺序为 preflight -> plugin remove -> link create；
- remove 失败时不写 links；
- unmanaged target 不覆盖；
- unrelated user skill 不删除。

### Plugin

- adapter preflight 失败时保留 universal links；
- transition 顺序为 adapter preflight -> owned links deactivate -> plugin activation；
- activation 失败报告明确 breakpoint；
- cache/source skill set mismatch 失败；
- 多个 enabled cache versions 失败。

### Bypass

- `--skip-agents-skills` 不能绕过 universal profile；
- `--skip-plugins` 不能绕过 plugin profile；
- 旧参数组合不能产生双路径或零路径。

### Wrappers

- Unix wrapper 将 profile 传给 refresh/check；
- PowerShell wrapper 同样；
- missing profile 报错；
- help 包含 profile。

建议命令：

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

然后执行：

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s plugins/workflow/tests -p 'test_*.py' -v
python3 -m unittest discover -s plugins/watcher/tests -p 'test_*.py' -v
```

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

外部依赖缺失时，区分环境失败和代码失败；不伪造通过。

## Read-only real-state inventory

M1 可以读取真实状态，但不执行 cutover。

完成源码候选后，对两个 profile 运行 read-only inventory；命令在迁移前允许失败。记录：

- 当前 active state 更接近 universal、plugin、dual-active 还是 inconsistent；
- repo-owned links；
- unmanaged conflicts；
- enabled my-codex plugins；
- cache versions；
- unknown/unclassified plugin；
- 下一次 M5 前的 blockers。

不得因此自动修改安装态。

## 独立 review

在 M1 Done 前，必须做独立只读 Contract review，至少检查：

1. 是否存在瞬时 dual-active window；
2. 是否存在无替代路径的 zero-active window；
3. failure 是否留下不可恢复中间态；
4. 是否可能删除 unmanaged `~/.agents/skills`；
5. 是否可能误删其他 marketplace/plugin；
6. universal 是否真正不依赖 cache/marketplace；
7. plugin 是否仍以 repo source 为比较权威；
8. identities 和 slimming baseline 是否完全未变；
9. 所有现有 refresh/check/wrapper callers 是否已适配。

没有 subagent runtime 时，可以由同一 agent 做独立第二遍 Standards/Contract review，但必须声明独立性限制。

## Git / PR 边界

本轮授权：

- 创建 M1 feature branch；
- 修改源码/tests/当前 goal docs；
- commit/push；
- 创建或更新一个 Draft PR；
- 读取 CI/review。

本轮不授权：

- merge M1 PR；
- 修改真实 runtime/install state；
- 删除 plugin/cache；
- marketplace cutover。

每个 commit 只 stage 已确认路径；不得使用 `git add -A`、`git add .` 或 `git add --all`。

完成后更新：

```text
docs/todo/universal-agent-skills-migration.md
```

将 M1 状态、review、checkpoint、测试证据、PR 和剩余 blocker 写回。不要创建第二份 universalization authority 文档。

## 完成标准

M1 完成时：

- repository-derived catalog 与所有调用方一起落地；
- refresh/check/wrappers 使用同一个 explicit profile；
- universal/plugin 源码层严格互斥；
- universal 不依赖 marketplace/cache；
- plugin 不允许 repo-owned universal links；
- transition ordering fail closed；
- bypass flags 不能破坏 profile invariant；
- focused/full tests 和独立 review 通过；
- real-state read-only inventory 已记录；
- skill 内容、identity、slimming baseline 未变化；
- runtime cutover 未执行；
- Draft PR 已准备好供用户决定是否合并。

最终中文报告：

1. M1 实现内容；
2. 双重注入和零路径如何被 transition ordering 阻止；
3. 测试与 review 结果；
4. 真实环境 read-only discovery 状态；
5. PR 当前是否具备 merge 条件；
6. 未执行的 runtime cutover；
7. 下一步 M2 Watcher metadata/shared-runtime 解耦入口。
