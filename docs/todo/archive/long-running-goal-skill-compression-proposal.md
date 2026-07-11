# Long-Running Goal Skill Compression Proposal

Generated: 2026-06-25

Status: implemented and validated on 2026-07-10; archived as the accepted semantic inventory and closure record.
The source edit followed a fresh oracle, independent semantic and risk review, forward-testing, and source-only validation. Installed-cache writeback remained delegated to the repository refresh workflow.

## Target

Reduce `long-running-goal` instruction sprawl only if a future candidate can preserve the skill's continuation contract semantics. The no-change baseline remains acceptable because the current skill carries permission-sensitive execution rules that are more important than token reduction.

## Evidence And Oracle

Evidence:

- `plugins/workflow/skills/long-running-goal/SKILL.md`
- `docs/todo/archive/skill-prompt-optimization.md`
- `mattpocock-skills:writing-great-skills` rubric: predictability, description precision, information hierarchy, single source of truth, and sprawl control.
- `workflow:prompt-strategy-loop` rubric: no-change baseline, frozen oracle, independent evaluation, bounded writeback, and source/cache separation.

Future compression must improve readability or invocation predictability without weakening:

- Request supersession decisions.
- Draft/Ready gates.
- Planning preflight and checkpoint evidence.
- Loop Blueprint harness fields.
- YOLO non-stops and runtime hard stops.
- Codex goal tool boundary.
- Production cutover shadow/comparison semantics.
- Milestone execution, evolution, close, archive, and current-doc hygiene.

## Semantic Inventory

| Area | Current role | Compression boundary |
| --- | --- | --- |
| Invocation metadata | Routes creation, upgrade, execution, resume, evolution, close, Loop harness, YOLO/hard-stop, and supersession work. | May be shortened only if every trigger branch still has a clear leading phrase. |
| Request Supersession Guard | Prevents stale goal execution when the newest request is unrelated or changes scope. | Keep inline; this is a high-risk first-step guard. |
| Goal File And Template | Defines Ready criteria, template use, planning-area discovery, and required contract content. | Keep required contract fields checkable; minor wording compression only. |
| Components | Points to planning preflight and checkpoint components. | Keep inline context pointers; do not expand component content here. |
| Create Or Upgrade | Freezes goal contract before implementation and keeps approvals out of runtime execution. | Can be tightened, but must preserve Draft/Ready distinction and approval handling. |
| Loop Blueprint Harness | Defines triggers, inputs, orchestration, isolation, connectors, verification, hard stops, and durable learning. | Keep as explicit checklist unless moved behind a strong Loop-specific context pointer. |
| Pre-Approval And YOLO Boundary | Defines pre-approved local work, external boundaries, hard stops, and continuation behavior. | Keep inline and explicit; this is the highest-risk autonomy section. |
| Codex Goal Tool Boundary | Prevents misuse of active Codex goal tools and blocked/complete status. | Keep inline; the tool boundary is safety-sensitive. |
| Production Cutover Gate | Preserves shadow comparison and rollback semantics. | Candidate for disclosed reference if a pointer clearly says to load it for cutovers. |
| Execute, Checkpoint, And Evolve | Defines milestone execution, validation, strategy evolution, and no silent weakening. | Can be tightened only after preserving evidence fields and gate behavior. |
| Current Docs And Close | Defines close/archive hygiene and active navigation cleanup. | Keep close criteria checkable; minor wording compression only. |
| Bundled Helpers | Lists helper commands. | Can remain concise or move to a helper reference if link reliability is proven. |
| Quality Bar | Summarizes acceptance questions. | Keep as final checklist or merge with Ready criteria if duplication is proven. |

## No-Change Baseline

Keep the current source skill unchanged if the future candidate cannot prove semantic equivalence. The existing sprawl is an acceptable tradeoff because the skill governs long-lived, permission-sensitive work where premature completion, stale continuation, or unsafe YOLO behavior would be more costly than extra tokens.

## Future Candidate Boundaries

A future source-edit candidate may:

- Tighten the description while preserving the main trigger branches.
- Collapse duplicated Ready/quality-bar wording only where the same meaning has one clear source of truth.
- Move cutover-specific or helper-command reference behind a strong context pointer if the main skill still tells the agent exactly when to load it.
- Shorten wording inside low-risk explanatory paragraphs without removing checkable completion criteria.

A future source-edit candidate must not:

- Convert hard stops into ordinary checkpoints.
- Make source-skill edits, cache refreshes, connector writes, external writes, or destructive actions implicit outside a frozen goal boundary.
- Weaken planning-preflight, checkpoint, validation, or close evidence.
- Merge unrelated planning schemes or use Codex goal tools without explicit user request.
- Hide high-risk YOLO, supersession, or Draft/Ready rules behind weak references.

## Review And Validation Required Before Source Edit

Before editing the source skill, run a fresh `prompt-strategy-loop` pass:

1. Freeze candidate-specific oracle and no-change baseline.
2. Produce a semantic inventory of old and new meanings.
3. Use one evaluator to score semantic preservation and one risk-reviewer to search for autonomy, permission, and failure-handling regressions.
4. Validate the Workflow plugin and planning helpers:

```bash
/Users/max/.codex/venvs/my-codex/bin/python scripts/check_my_codex.py --skip-agents --plugin workflow
/Users/max/.codex/venvs/my-codex/bin/python plugins/workflow/skills/long-running-goal/scripts/check_md_links.py docs/todo
git diff --check -- plugins/workflow/skills/long-running-goal/SKILL.md docs/todo
```

## Residual Risk

The likely failure mode is a shorter skill that looks cleaner but causes weaker continuation behavior. Any future edit should prefer keeping the current text over accepting a candidate that removes observable gates, evidence fields, or hard-stop conditions.

## Closure Evidence — 2026-07-10

Implemented:

- Kept request supersession, `Ready`, template/components, pre-approval/YOLO, runtime hard stops, Codex goal-tool boundaries, helper commands, and the quality bar inline.
- Added explicit create/Loop, production-cutover, and execute/evolve/close context pointers with branch completion criteria under `references/`.
- Kept create/upgrade/evolve current-doc synchronization inline after independent review found an initial cross-branch discoverability gap.
- Reduced top-level `SKILL.md` from 184 to 116 physical lines and from 2,246 to 1,298 words.
- Added `plugins/workflow/tests/test_long_running_goal_disclosure.py` to lock high-risk inline contracts, branch triggers, moved headings, current-doc synchronization, and reference completion criteria.

Independent evaluation:

- Semantic evaluator verdict after the current-doc fix: `equivalent`, no blocker.
- Risk reviewer verdict: `mostly equivalent with caveats`, no blocking semantic drift; high-risk rules remain inline.
- A fresh-context Loop-shaped production-cutover forward-test loaded all matching branch references, kept unspecified semantics and approvals `Draft`, preserved the comparison matrix and anti-fake-speedup rule, and distinguished review-gate failure from a true runtime hard stop.

Validation passed:

- Workflow tests: 18/18.
- Focused disclosure tests: 2/2.
- Skill quick validation and Workflow plugin validation.
- Relative Markdown link checks and `git diff --check`.

Residual risk: the readiness checker remains a signal-based structural checker. It does not yet reject every semantically invalid Loop/connector, YOLO, hard-stop, or close-navigation contract; that pre-existing hardening opportunity is outside this disclosure change and must not be represented as covered by the static tests.

## Follow-Up Validation Hardening — 2026-07-10

The residual checker opportunity above was implemented as a separate follow-up:

- `check_goal_ready.py` now parses explicit overall and milestone lifecycle state, enforces ordered `Done* -> current? -> Not Started*` milestones, and couples `Done`, Review, Checkpoint, Close, preflight, and section-local status evidence.
- Manual and Loop-shaped execution modes now have distinct harness contracts; Loop-shaped goals require all nine non-empty fields.
- The checker rejects obvious permission-model contradictions such as destructive/external actions in local YOLO scope, recoverable work listed as a hard stop, and unresolved external-write approval on a non-Draft goal.
- `check_todo_index.py` now validates exact Markdown links in `active`, `closed`, and `absent` modes; archive names, prose, and fenced examples cannot satisfy active navigation.
- The Workflow skill, close reference, and template document the stricter interfaces and their static-validation boundary.

The checker still validates what the document declares, not whether permissions, revisions, command output, rollback behavior, or external-system facts are true. Those remain execution and independent-review responsibilities.
