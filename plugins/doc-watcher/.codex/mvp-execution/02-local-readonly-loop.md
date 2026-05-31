# 02. Local Readonly Loop

## Goal

让用户能配置一个或多个本地 Git repos，读取 active docs、入口文件、脚本/config、recent commits 和 changed files，并生成只读 evidence pack。

## Current State

已完成第一版。`audit_repo.py` 会校验 repo、发现文档文件、检查 markdown 相对链接、扫描 watch terms、列出 recent commits 和 changed files，并输出 report。

## Deliverables

- Repo config 支持 `name`、`path`、`docs`、`source_of_truth`、`watch_terms`、`commit_threshold`。
- 扫描过程不写目标 repo。
- 缺失路径、非法 repo、Git 命令失败会直接报错。
- report 中包含 source-of-truth 状态、recent commits、changed files 和 deterministic findings。

## Task Breakdown

### P0

- 读取 JSON repo config。
- 校验 repo path 是 Git repo。
- 发现 configured docs 或默认 entry docs。
- 检查 markdown 相对链接。
- 搜索 configured watch terms。
- 根据 recent commit window 计算 changed files。

### P1

- 增加 include/exclude pattern。
- 增加 docs inventory hash，用于判断 docs 是否变化。
- 增加更细的 changed file 分组：code、runtime config、tests、docs、scripts。

## Interfaces

- `config/repos.example.json` 是公开示例。
- `config/repos.json` 是本地私有配置，不能提交私人路径。
- `audit_repo.py` 输出 Markdown report，并打印 report path 和 findings count。

## Acceptance Criteria

- 用户可以对当前 repo 运行一次 audit。
- 缺失 configured docs 会成为 high finding。
- 断链会成为 high finding。
- watch terms 会成为 medium finding。
- 近期 code/runtime changes 没有对应 docs changes 时会提示人工 review。

## Risks

- 不要扫描 `.git`、`node_modules`、`dist`、`.venv` 等生成目录。
- 不要让 configured path 逃出 repo 根目录。
- 不要把没有 deterministic finding 解释为语义完全对齐。
