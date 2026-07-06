# Skill Watcher

This context describes the language used to evaluate Skill Watcher usage data for Codex skills and plugin-provided skill systems.

## Language

**Primary Skill**:
The entry skill that a turn is directly attributed to through an explicit signal or the strongest detected match.
_Avoid_: active skill, single skill context

**Supporting Skill**:
A skill that is directly used or required by the primary skill's workflow but is not the turn's entry point.
_Avoid_: secondary skill, indirect skill, dependency skill

**Effective Skill**:
Any skill whose discipline was exercised in a turn, including both the primary skill and supporting skills.
_Avoid_: combined usage, actual skill

**Effective Turns**:
The count of turn summaries where a skill appears as either the primary skill or a supporting skill.
_Avoid_: primary turns, skill mentions

**Primary Turns**:
The count of turn summaries where a skill is the primary skill.
_Avoid_: effective turns, raw events

**Supporting Turns**:
The count of turn summaries where a skill appears as a supporting skill.
_Avoid_: primary turns, mentioned turns

**Supporting-only Skill**:
A skill with no primary turns but at least one supporting turn in the reporting window.
_Avoid_: unused skill, zero-hit skill

**Zero Effective Usage**:
A reporting result where a skill has no primary turns and no supporting turns in the reporting window.
_Avoid_: zero primary usage, low usage

**Skill Dependency Map**:
A declared relationship that lists which supporting skills belong to a primary skill's workflow.
_Avoid_: inferred dependency, text-matched dependency

**Mentioned Skill**:
A skill name or alias observed in runtime text that may provide attribution evidence but does not by itself prove workflow use.
_Avoid_: supporting skill, effective skill

**Skill Metadata Manifest**:
A plugin-owned machine-readable declaration at `.codex-plugin/skill-watcher.json` containing canonical names, legacy names, aliases, roles, and skill dependency map entries that Skill Watcher can consume.
_Avoid_: README inference, directory scan as source of truth

**Incremental Metadata Index**:
A plugin-owned metadata layer added beside upstream skill instructions to improve discovery, attribution, and reporting without changing the skill instructions themselves.
_Avoid_: behavior patch, upstream skill edit

**Typed Alias**:
An alias with an explicit kind and matching strategy so runtime matching can distinguish exact skill names, slugs, phrases, and risky natural-language terms.
_Avoid_: substring alias, untyped alias

**Skill Role**:
A metadata classification that explains how a skill is normally used in a skill system: entrypoint, wrapper, discipline, or specialized.
_Avoid_: usage count bucket, deletion signal

**Runtime Metadata Cache**:
A Skill Watcher-generated cache of installed skill metadata manifests used by hooks at runtime.
_Avoid_: plugin source of truth, hand-maintained allowlist

**Skill Attribution**:
The structured explanation of why a turn is associated with primary, supporting, effective, or mentioned skills.
_Avoid_: skill name, active skill

**Turn Summary**:
The turn-level usage fact emitted at the end of a monitored turn and used as the default source for usage reporting.
_Avoid_: raw event aggregate, tool event count

**Tool Failure Observation**:
A record that a tool call failed during a turn; it is diagnostic evidence, not a task outcome by itself.
_Avoid_: skill failure, task failure

**Skill Watcher Schema Migration**:
An explicit reset of Skill Watcher runtime state from one event schema to another, with old logs archived rather than mixed with new events.
_Avoid_: automatic compatibility, mixed-schema log
