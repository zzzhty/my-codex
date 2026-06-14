# DocWatcher

DocWatcher 是一个面向个人 vibe coding 工作流的 **文档语义漂移 audit plugin**。它定期或按 commit 阈值扫描指定本地仓库，收集只读证据，使用内置 `doc-alignment` 的语义对齐流程产出 audit summary，再由操作者决定是否修改文档；显式 cleanup 请求可使用 `housekeeping` 清理临时文件、缓存和 active docs 中的过时内容。

产品定位：**a local audit runner for drifting docs**。DocWatcher 先报告，不自动改目标仓库，不创建远端评审流程，不把个人工作流升级成公司级治理平台。

本文是项目定位、当前 MVP 和执行方向的 source of truth。

命名约定：`DocWatcher` 是产品展示名，用于 README、插件界面、audit 报告标题和运行状态；`doc-watcher` 是机器可读 slug，用于仓库名、脚本路径、runtime state 和插件 manifest。

## Core Principles

- 目标仓库只读：DocWatcher 不修改被扫描仓库的代码或文档。
- 报告优先：默认产物是 audit summary，不是补丁。
- 人工决策：操作者阅读 summary 后，显式决定是否让 `doc-alignment` 进入 implementation mode。
- 清理分流：临时文件、缓存、过时 active docs、旧 hook/skill 名称和迁移残留走 `housekeeping`，语义审查和文档对齐仍以 `doc-alignment` 为基准。
- 语义对齐：关注名称、入口、文档口径、历史/当前边界、断链、脚本命令和验证口径是否一致。
- 低摩擦触发：支持 scheduled full scan 和 commit-dependent scan，贴近日常个人工作流。
- Cockpit 作为 adapter：本地 backend/frontend 只展示 audit state、运行报告和手动触发结果，不拥有第二套事实源。

## MVP Workflow

MVP 优先跑通这条轻量闭环：

```text
配置本地 repos
  -> 定时或按 commit 阈值触发
  -> 收集 README、AGENTS、docs、scripts、配置和 recent commits
  -> 生成 deterministic audit pack
  -> Codex 按 doc-alignment 语义审查
  -> 写入 $CODEX_HOME/doc-watcher/reports/
  -> 操作者判断是否需要修改
```

默认触发方式：

- **Full scan mode**：扫描配置中的 repos，生成汇总报告，主要用于手动 baseline/full scan。
- **Commit-dependent mode**：记录每个 repo 的 last audited revision、config hash 和 finding fingerprints；当新增 commit 数达到阈值或 repo 配置变化时触发扫描。
- **Manual mode**：直接对某个 repo 运行一次 audit，用于临时检查。

## Audit Workflow Contract

- Trigger: commit-dependent scheduled scan, baseline full scan, or an explicit manual audit request.
- Inputs: configured local repositories, selected source-of-truth files, recent commits, and audit configuration.
- Outputs: deterministic audit pack plus human-readable audit summary.
- Report location: `$CODEX_HOME/doc-watcher/reports/` unless the user passes an explicit output path.
- State location: `$CODEX_HOME/doc-watcher/repo-state.json` for commit-dependent audit state, config hashes, and finding fingerprints.
- Allowed actions: inspect target repositories, collect read-only evidence, generate audit reports, and summarize drift findings.
- Forbidden actions: do not modify target repositories, rewrite docs, open remote review flows, or apply `doc-alignment` implementation changes unless the user explicitly asks for implementation mode.
- Validation: report the audited repo, evidence pack or report path, checked entry points, new/resolved/still-open findings, and blockers. Do not treat missing configured files as success unless the report names them.

## Plugin Layout

```text
.codex-plugin/plugin.json
skills/doc-alignment/SKILL.md
skills/housekeeping/SKILL.md
config/repos.example.json
scripts/audit_repo.py
scripts/generate_report.py
scripts/commit_counter.py
scripts/doctor.py
```

Runtime state 写入用户目录，不写目标 repo：

```text
$CODEX_HOME/doc-watcher/
├── reports/
├── audits/
└── repo-state.json
```

## Local Audit Cockpit

DocWatcher 现在包含一个本地 audit cockpit，用来查看配置仓库、commit-dependent 状态、审计报告、finding delta 和手动运行日志。Cockpit 是 plugin scripts 的 adapter：

- Backend 读取 `config/repos*.json`、`$CODEX_HOME/doc-watcher/repo-state.json`、`$CODEX_HOME/doc-watcher/reports/` 和 `runs/` 记录。
- Frontend 默认进入 `/audit`，报告详情在 `/audit/reports/:reportId`，finding 详情在 `/audit/repos/:repoName/findings/:findingId`。
- 手动按钮调用同一组脚本：`commit_counter.py`、`generate_report.py`、`audit_repo.py`。
- Cockpit 不写目标仓库，不生成补丁，不创建远端 PR；需要修改文档时，复制 handoff prompt 后显式进入 `doc-alignment` implementation mode。

主要 API：

```text
GET  /api/v1/audit/status
GET  /api/v1/audit/repos
GET  /api/v1/audit/repos/{repo_name}
GET  /api/v1/audit/reports
GET  /api/v1/audit/reports/{report_id}
GET  /api/v1/audit/last-run
GET  /api/v1/audit/runs
POST /api/v1/audit/runs/commit-counter
POST /api/v1/audit/runs/generate-report
POST /api/v1/audit/repos/{repo_name}/runs/audit
```

## Target Repo Contract

DocWatcher 默认面向普通本地 Git 项目，不要求额外治理配置。推荐但不强制存在以下入口：

```text
my-project/
├── README.md
├── AGENTS.md
├── docs/
├── scripts/
├── package.json / pyproject.toml / other runtime config
└── .codex/
```

Repo 配置使用 JSON，避免给个人工作流增加额外依赖：

```json
{
  "repos": [
    {
      "name": "my-codex",
      "path": "../../..",
      "docs": [
        "README.md",
        "AGENTS.md",
        "plugins/doc-watcher/README.md",
        "plugins/doc-watcher/AGENTS.md",
        "plugins/skill-watcher/README.md",
        "plugins/skill-watcher/hooks/codex/README.md",
        "plugins/skill-watcher/todo.md",
        "plugins/workflow/README.md",
        "plugins/workflow/.codex-plugin/plugin.json",
        "plugins/workflow/skills"
      ],
      "source_of_truth": [
        "README.md",
        "AGENTS.md",
        "plugins/workflow/README.md"
      ],
      "watch_terms": [],
      "commit_threshold": 5
    }
  ]
}
```

将 `config/repos.example.json` 复制为本地私有配置后再改路径。不要把包含私人路径或内部仓库列表的配置提交到共享仓库。

Repo `path` supports environment variables and relative paths. Relative paths are resolved from the config file directory.

## Current MVP Status

当前 MVP 已完成 audit-first pivot，并接入本地 audit cockpit：

- 新增 Codex plugin manifest。
- 新增 `doc-alignment` skill，定义只读语义 audit 工作流。
- 新增 `housekeeping` skill，基于 `doc-alignment` 语义清理临时文件、缓存、过时 active docs 和迁移残留。
- 新增 repo audit、report generation、commit counter 和 doctor 脚本。
- 新增 backend audit read model 和 command bridge，API 状态全部回溯到 plugin config、runtime state、reports 和 run records。
- 新增 frontend audit cockpit，默认 route 是 `/audit`，当前导航只展示 audit cockpit。
- active roadmap 已改为 audit-first，不再以远端分支评审作为未来路线。
- 旧 patch/PR/provider/webhook 路由和页面文件保留为 legacy compatibility/source history，不挂载为当前产品导航。

可复用旧资产：

- **Audit cockpit**：当前用于 audit backlog、latest report、finding backlog、recent runs 和手动触发。
- **Webhook 思路**：未来可作为 commit/event 触发器，不承担写入或远端评审职责。

暂不继续投入：

- 文档补丁自动生成闭环。
- 远端 provider 写入闭环。
- 复杂团队治理、权限、多租户和远端状态同步。

## Commands

直接审计单个 repo：

```bash
python3 scripts/audit_repo.py --repo ../.. --name my-codex --print-report
```

按配置生成审计报告：

```bash
python3 scripts/generate_report.py --config config/repos.example.json --print-report
```

生成定时任务应使用的增量 digest，并在成功后推进 repo audit state：

```bash
python3 scripts/generate_report.py --config config/repos.example.json --mode commit-dependent --mark-audited --digest
```

检查 commit 阈值触发状态：

```bash
python3 scripts/commit_counter.py --config config/repos.example.json
```

检查插件和配置：

```bash
python3 scripts/doctor.py --config config/repos.example.json
PLUGIN_VALIDATOR="${PLUGIN_VALIDATOR:-${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py}"
(cd backend && uv run python "$PLUGIN_VALIDATOR" ..)
```

运行本地 audit cockpit：

```bash
./scripts/doc-watcher init
./scripts/doc-watcher up
./scripts/doc-watcher start
./scripts/doc-watcher status
./scripts/doc-watcher logs
./scripts/doc-watcher stop
```

`up` 在前台同时启动 backend 和 frontend，适合开发和 Browser 验证；`start/status/logs/stop` 使用本地 run/log 目录管理后台进程。

Backend:

```bash
cd backend
uv sync
uv run python -m uvicorn app.main:app --reload
uv run ruff check app tests
uv run --all-groups python -m pytest
```

Backend audit endpoints are served under `/api/v1/audit/*`. Existing database-backed patch/PR/provider routes are legacy compatibility surfaces and are not the current audit product source of truth.

Frontend:

```bash
cd frontend
pnpm install
pnpm dev
pnpm build
pnpm lint
```

Frontend `/dashboard` redirects to `/audit`. Current visible routes are the audit cockpit, report detail, and finding detail views.

## Documentation Map

- `README.md`：当前产品定位、MVP 路线和维护入口。
- `AGENTS.md`：贡献者和 agent 工作约束。
- `skills/doc-alignment/SKILL.md`：可由 Codex 调用的语义 audit 工作流。
- `skills/housekeeping/SKILL.md`：可由 Codex 调用的 cleanup 工作流，用于临时文件、缓存和过时 active docs 清理。
