# Skill Slimming Batch 1 Validation Handoff

Generated: 2026-08-20

Status: source candidate implemented on `agent/skill-slimming-batch-1`; runtime and full test validation remain pending in an actual development checkout.

Baseline: `main@6f3dd5ce2cefabd4256137244293bac87041388a`

Candidate head: `cde089dd3f69c0a7cce85c441a053dcc407eb1ba`

Controlling review: [`skill-slimming-v2-review.md`](skill-slimming-v2-review.md)

## Scope

This batch changes only the low-risk targets authorized by the review:

- `workflow:summary-in-html`
- `workflow:sop`
- `watcher:housekeeping`
- `workflow:prompt-strategy-loop`
- `watcher:skill-compressor`

The Matt Pocock upstream mirror, `long-running-goal`, `orchestrate-subagents`, `doc-alignment`, root `AGENTS.md`, runtime hooks, installed plugin caches, templates, renderers, and deterministic validators are unchanged.

## Result

The five top-level `SKILL.md` files shrink from approximately 20.9 KB to 14.0 KB, a 32.9% reduction in the model-facing skill bodies.

Including the new on-demand summary schema reference and the shortened SOP interface metadata, the changed instruction surfaces shrink from approximately 21.3 KB to 16.3 KB, a 23.6% net reduction.

| Skill | Candidate words | Main change |
| --- | ---: | --- |
| `summary-in-html` | 290 | Move JSON/member detail behind `references/artifact-schema.md`. |
| `sop` | 371 | Let the template and readiness checker own field-level structure. |
| `housekeeping` | 382 | Replace long lists with three ownership classes. |
| `prompt-strategy-loop` | 401 | Center the flow on evidence, oracle, smallest candidate, and proportional review. |
| `skill-compressor` | 395 | Reuse prompt-strategy-loop review policy and retain only compression-specific rules. |

## Commit Map

1. `34add092` — deepen `summary-in-html`
2. `325693f9` — slim `sop`
3. `9519a38d` — classify `housekeeping` by ownership
4. `0b05bd63` — make prompt review proportional
5. `cde089dd` — compress the compressor

Each commit owns one skill or one tightly coupled skill/reference pair.

## Preserved Contracts

### `summary-in-html`

- Trigger still names a developer reference, source-code walkthrough, step-by-step code handoffs, and real entry points.
- `summary` and `source_walkthrough` remain distinct modes.
- Scope, source-walkthrough, chapter, artifact-schema, and visual branches remain reachable.
- Custom outputs keep JSON beside the HTML and assets in a sibling `assets/` directory.
- Generated visuals remain explicit-request only.
- Rendering, validation, standalone HTML, non-overwrite, blind-spot, and reader-progress boundaries remain.

### `sop`

- Stable-workflow suitability remains distinct from prompt strategy and long-running goals.
- Manual, agent-executed, automated, report-only, validation, maintenance/release, and incident/failure modes remain.
- The template and readiness/link checkers remain authoritative.
- Behavior-affecting updates still modify the affected contract fields together.
- Report-only execution stays non-mutating; missing required inputs and failed required validation remain stops.

### `housekeeping`

- Scheduled/read-only audits still route to `doc-alignment`.
- Cleanup requires inspection and established ownership/disposability.
- User work, private configuration, databases, reports, runtime/audit state, dependencies, build output, migrations, and unknown binaries remain protected.
- Active semantic drift is aligned rather than erased; archives remain historical.
- Exact-path mutation, focused validation, and recurring-artifact root-cause repair remain.

### `prompt-strategy-loop`

- Evidence and a frozen oracle precede candidates.
- The no-change baseline and smallest viable candidate remain mandatory.
- Independent evaluation and the separate risk pass remain proportional to the affected behavior.
- Missing required review stops at an unverified proposal.
- Report-only mode, authorized writeback, installed-state separation, long-running-goal routing, and subagent authorization remain.

### `skill-compressor`

- Compression remains behavior-preserving rather than redesign.
- Deterministic scripts remain out of scope unless explicitly included.
- A recoverable baseline and affected semantic inventory remain mandatory.
- Trigger/routing, permission, stop/failure, validator, and unique-edge-case drift block equivalence.
- Installed-state activation remains separately authorized.

## Static Review Completed Here

The current environment verified:

- source-candidate ancestry: five skill commits ahead of `main`, zero behind, before this handoff commit;
- changed-path scope: seven files only;
- summary invocation phrases required by `test_invocation_contract.py`;
- all new and retained relative reference targets exist in the repository;
- no Matt Pocock mirror, runtime, cache, hook, template, renderer, checker, or root-policy file changed;
- Standards axis: `writing-for-agents` information hierarchy, no-op pruning, positive steering, and deep-module interface;
- Contract axis: current source, prior review inventories, templates, scripts, tests, and checkers.

This environment could not clone GitHub or run the repository test suite, so no runtime, plugin-install, cache-refresh, or cross-platform pass is claimed.

## Development-Environment Validation

From a clean checkout of the candidate branch:

```bash
git switch agent/skill-slimming-batch-1
git status --short

python3 scripts/bootstrap_tooling_env.py
MY_CODEX_PYTHON="${CODEX_HOME:-$HOME/.codex}/venvs/my-codex/bin/python"

"$MY_CODEX_PYTHON" -m unittest discover -s plugins/workflow/tests -p 'test_*.py' -v
"$MY_CODEX_PYTHON" -m unittest discover -s plugins/watcher/tests -p 'test_*.py' -v
"$MY_CODEX_PYTHON" -m unittest discover -s tests -p 'test_*.py' -v

"$MY_CODEX_PYTHON" plugins/workflow/skills/long-running-goal/scripts/check_md_links.py plugins/workflow/skills
"$MY_CODEX_PYTHON" plugins/workflow/skills/long-running-goal/scripts/check_md_links.py plugins/watcher/skills

git diff --check main...HEAD
```

When `PLUGIN_VALIDATOR` is available, also validate both owning plugins directly.

Do not refresh installed plugin caches or hooks until the source candidate and behavioral scenarios pass.

## Behavioral Scenarios

Run baseline and candidate with the same model/settings and compare questions, stops, governance-only steps, outputs, and validation choices.

1. **HTML summary** — request a summary of one bounded module. Expect one evidence route, one JSON artifact, one HTML artifact, focused validation, and no schema narration in the user-facing response.
2. **Source walkthrough** — request an entry-first walkthrough. Expect a complete route map, valid handoff steps, current-source evidence, and no invented entry point.
3. **Report-only SOP** — execute a report-only procedure. Expect no mutation and a clear stop for a missing required input.
4. **Housekeeping with mixed candidates** — include ignored cache, untracked source-looking config, and stale active README text. Expect delete / preserve-and-report / align classifications respectively.
5. **Low-risk prompt wording change** — expect evidence, oracle, baseline, smallest candidate, and no unnecessary independent reviewer.
6. **High-risk routing change** — expect required independent evaluation and an unverified proposal if that review is unavailable.
7. **Skill compression touching a script** — expect the deterministic script to remain unchanged unless explicitly in scope.

Accept the batch only when required invariants pass, unnecessary questions or false stops do not increase, and the candidate reaches every matching reference branch.

## Rollback

The source candidate is five linear skill commits over `main`; this handoff is a sixth docs-only commit. Revert one skill independently or reset the branch to `main@6f3dd5ce` before activation. Installed state is unchanged, so source rollback requires no cache or hook cleanup unless a later validation step explicitly activates the candidate.
