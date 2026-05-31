# DocWatcher

DocWatcher 是一个面向个人 vibe coding 工作流的 **文档语义漂移 audit plugin**。它定期或按 commit 阈值扫描指定本地仓库，收集只读证据，使用内置 `doc-alignment` 的语义对齐流程产出 audit summary，再由操作者决定是否修改文档。

产品定位：**a local audit runner for drifting docs**。DocWatcher 先报告，不自动改目标仓库，不创建远端评审流程，不把个人工作流升级成公司级治理平台。

本文是项目定位、当前 MVP 和执行方向的 source of truth。更细的执行包放在 `.codex/mvp-execution/`。

命名约定：`DocWatcher` 是产品展示名，用于 README、插件界面、audit 报告标题和运行状态；`doc-watcher` 是机器可读 slug，用于仓库名、脚本路径、runtime state 和插件 manifest。

## Core Principles

- 目标仓库只读：DocWatcher 不修改被扫描仓库的代码或文档。
- 报告优先：默认产物是 audit summary，不是补丁。
- 人工决策：操作者阅读 summary 后，显式决定是否让 `doc-alignment` 进入 implementation mode。
- 语义对齐：关注名称、入口、文档口径、历史/当前边界、断链、脚本命令和验证口径是否一致。
- 低摩擦触发：支持 daily scan 和 commit-dependent scan，贴近日常个人工作流。
- 可复用资产收敛：旧实现中仅保留 dashboard 和 webhook 思路作为未来可复用能力。

## MVP Workflow

MVP 优先跑通这条轻量闭环：

```text
配置本地 repos
  -> 定时或按 commit 阈值触发
  -> 收集 README、AGENTS、docs、scripts、配置和 recent commits
  -> 生成 deterministic audit pack
  -> Codex 按 doc-alignment 语义审查
  -> 写入 ~/.codex/doc-watcher/reports/
  -> 操作者判断是否需要修改
```

默认触发方式：

- **Daily mode**：每天扫描配置中的 repos，生成汇总报告。
- **Commit-dependent mode**：记录每个 repo 的 last audited revision；当新增 commit 数达到阈值时触发扫描。
- **Manual mode**：直接对某个 repo 运行一次 audit，用于临时检查。

## Plugin Layout

```text
.codex-plugin/plugin.json
skills/doc-alignment/SKILL.md
config/repos.example.json
scripts/audit_repo.py
scripts/daily_report.py
scripts/commit_counter.py
scripts/doctor.py
```

Runtime state 写入用户目录，不写目标 repo：

```text
~/.codex/doc-watcher/
├── reports/
├── audits/
└── repo-state.json
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
      "name": "doc-watcher",
      "path": "/Users/max/Projects/my-codex/plugins/doc-watcher",
      "docs": [
        "plugins/doc-watcher/README.md",
        "plugins/doc-watcher/AGENTS.md",
        "plugins/doc-watcher/.codex/mvp-execution"
      ],
      "source_of_truth": [
        "plugins/doc-watcher/README.md",
        "plugins/doc-watcher/AGENTS.md"
      ],
      "watch_terms": [],
      "commit_threshold": 5
    }
  ]
}
```

将 `config/repos.example.json` 复制为本地私有配置后再改路径。不要把包含私人路径或内部仓库列表的配置提交到共享仓库。

## Current MVP Status

当前已完成 MVP pivot 的源头改造：

- 新增 source-only Codex plugin manifest。
- 新增 `doc-alignment` skill，定义只读语义 audit 工作流。
- 新增 repo audit、daily report、commit counter 和 doctor 脚本。
- active roadmap 已改为 audit-first，不再以远端分支评审作为未来路线。
- 旧 backend/frontend 实现保留在仓库中，但不再代表当前 MVP 主线。

可复用旧资产：

- **Dashboard**：未来可改造成 audit backlog 和 drift trend 页面。
- **Webhook**：未来可作为 commit/event 触发器，不承担写入或远端评审职责。

暂不继续投入：

- 文档补丁自动生成闭环。
- 远端 provider 写入闭环。
- 复杂团队治理、权限、多租户和远端状态同步。

## Commands

直接审计单个 repo：

```bash
python3 scripts/audit_repo.py --repo /Users/max/Projects/my-codex/plugins/doc-watcher --name doc-watcher --print-report
```

按配置生成日报：

```bash
python3 scripts/daily_report.py --config config/repos.example.json --print-report
```

检查 commit 阈值触发状态：

```bash
python3 scripts/commit_counter.py --config config/repos.example.json
```

检查插件和配置：

```bash
python3 scripts/doctor.py --config config/repos.example.json
cd backend && uv run python /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/max/Projects/my-codex/plugins/doc-watcher
```

旧 Web app 仍可本地运行，用于查看可复用界面和服务代码：

```bash
./scripts/doc-watcher init
./scripts/doc-watcher start
./scripts/doc-watcher status
./scripts/doc-watcher logs
./scripts/doc-watcher stop
```

Backend:

```bash
cd backend
uv sync
uv run python -m uvicorn app.main:app --reload
uv run ruff check app tests
uv run --all-groups python -m pytest
```

Frontend:

```bash
cd frontend
pnpm install
pnpm dev
pnpm build
pnpm lint
```

## Documentation Map

- `README.md`：当前产品定位、MVP 路线和维护入口。
- `AGENTS.md`：贡献者和 agent 工作约束。
- `.codex/mvp-execution/`：audit-first MVP 执行包和验收清单。
- `skills/doc-alignment/SKILL.md`：可由 Codex 调用的语义 audit 工作流。
