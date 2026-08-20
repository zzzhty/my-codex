# Universal Agent Skills Cleanup Follow-Up

Status: `Deferred`

This design note preserves the cleanup boundary removed from the active Universal Agent Skills Migration goal. It is not an executable long-running goal and grants no deletion authority.

## Activation Trigger

Create a separate cleanup long-running goal only after the migration goal's M5 cutover is `Done` and the universal profile has completed at least five successful sessions across at least three working days, including exact qualified Codex invocation identities, bare catalog-name mapping and request resolution, implicit routing, Watcher core, and repo-owned hook checks.

## Required Starting Evidence

1. Exact retained plugin, marketplace, cache, config, hook-backup, agent-support, and Watcher-state inventory from M5.
2. Repository-wide proof that no current source, test, doc, or runtime consumer requires each cleanup candidate.
3. Independent ownership and deletion review for an exact path or config-entry set.
4. A new planning preflight, explicit destructive authorization, rollback or recovery evidence, and bounded validation commands.

## Protected State

- Unrelated marketplaces, plugins, config, unmanaged skills, and user files.
- Watcher logs, reports, proposals, snapshots, hook backups still needed for recovery, and other durable evidence.
- The source checkout and any rollback artifact still required by the observation window.
- Symlink, junction, or reparse-point targets outside an exact owned deletion boundary.

## Current Boundary

No cleanup mutation is authorized by this note or by the active migration goal. Until the activation trigger and a separate `Ready` cleanup goal exist, retain the inventoried rollback state.
