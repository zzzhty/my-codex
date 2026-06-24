# Long-Running Goal Skill Compression Proposal

Generated: 2026-06-25

Status: proposal only. Do not edit `plugins/workflow/skills/long-running-goal/SKILL.md` from this artifact without a later source-edit pass, fresh oracle, independent review, and validation.
This proposal does not authorize direct installed-cache edits or cache writeback under `/Users/max/.codex/plugins/cache/`.

## Target

Reduce `long-running-goal` instruction sprawl only if a future candidate can preserve the skill's continuation contract semantics. The no-change baseline remains acceptable because the current skill carries permission-sensitive execution rules that are more important than token reduction.

## Evidence And Oracle

Evidence:

- `plugins/workflow/skills/long-running-goal/SKILL.md`
- `docs/todo/skill-prompt-optimization.md`
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
