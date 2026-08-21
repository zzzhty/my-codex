# Universal Agent Skills Local Cleanup Long-Running Goal

Overall status: `Ready`

Updated: 2026-08-21

This file is the sole active execution authority for the bounded local cleanup that follows the completed Universal Agent Skills migration. It replaces the deferred design note after the user explicitly waived the observation window, accepted Git as the functional recovery checkpoint, authorized the exact local and GitHub mutations, and confirmed permanent deletion of the exact rollback root.

## Goal Summary

Goal Name: `Universal Agent Skills Local Cleanup`

Goal Description:

1. Remove only the obsolete local migration rollback bundle, the live `my-codex` marketplace registration, and the empty live `my-codex` plugin-cache namespace.
2. Preserve the active 34-link universal discovery profile, repository source and optional plugin distribution, current hooks and agent support, unrelated configuration, and all Watcher durable state.
3. Publish a Git checkpoint and closure record that is sufficient to reconstruct functionally equivalent plugin or universal profiles in another environment, while explicitly accepting that deleted local historical evidence cannot be reproduced byte-for-byte.

Goal Status: `Ready`

Goal Owner: `my-codex repository maintainer`

Goal Path: `docs/todo/universal-agent-skills-cleanup.md`

Planning root: `docs/todo`

Goal directory: `docs/todo`

Continuation contract: Read this file, root `AGENTS.md`, current `main`, the newest user request, and current local runtime state before acting. Execute strictly in order `M0 -> M1 -> Close`. M0 admits no cleanup mutation. M1 may mutate only the exact authorized local targets after readiness and independent deletion review are Clean. Permanent rollback-root deletion is intentionally irreversible; preserve every excluded boundary and stop before deletion on any inventory, ownership, closure, config, hash, or review contradiction.

Planning preflight marker: `preflight:universal-agent-skills-cleanup:20260821-grill2`

Planning preflight status: `Done`

Preflight source: `grill-with-docs`

Resolved decisions: `The user explicitly superseded the five-session/three-working-day observation trigger because this Mac is not the future execution environment; confirmed Q1 exact cleanup scope; selected Q2 Not applicable task-temporary-cache handling; authorized Q3 branch, PR, merge, and safe branch deletion; and confirmed Q4 permanent deletion with shared understanding that raw local history is not recoverable from Git.`

Open decisions: `None.`

Docs written: `Not applicable: the existing discovery-profile and cleanup vocabulary is unchanged, so no glossary or ADR is required.`

## Preflight Time Assessment

Assessment target: `Ready-to-Closed`

Assessment mode: `Rough range`

Rough elapsed-time estimate: `30-60 minutes`

Basis or blocker: `2026-08-21 bounded inventory shows three exact local mutation classes totaling 912 KiB, no installed target plugins, an empty live cache namespace, and no repository or runtime consumer of the rollback root. The range includes serial independent review, local apply and recovery checks, GitHub Draft PR publication and merge, and branch cleanup. It assumes ordinary GitHub availability; the repository has no configured CI checks or other external wait.`

Critical-path time-cost distribution: `Not required: rough range recorded.`

## Task Temporary Cache / Housekeeping

Close housekeeping policy: `Not applicable`

Housekeeping decision source: `User explicitly confirmed Q2 as Not applicable on 2026-08-21.`

Task temporary cache root strategy: `Not applicable: no task temporary cache roots will be created, used, or needed. In-memory comparisons and repository goal evidence are sufficient.`

Recorded task temporary cache roots: `Not applicable`

Housekeeping boundary: `No task temporary cache root will be created or cleaned at Close. The permanent deletion authorized for M1 is the goal's primary exact cleanup target, not task-temporary-cache housekeeping. Generic ignored Python caches, dependencies, runtime state, logs, reports, and unknown producers remain outside this goal.`

## Current Execution Baseline

1. Repository `main` and `origin/main` both resolve to migration Close merge `f01d0a17b82dfbdb0e002675d2cd90908fd41d09`; the preflight worktree was clean.
2. Universal discovery exposes exactly 34 repository-owned symlinks below `/Users/max/.agents/skills`, with zero non-link entries. The three skills-bearing `my-codex` plugins are not installed and the live `/Users/max/.codex/plugins/cache/my-codex` directory is empty.
3. The live `my-codex` marketplace registration is a local binding from `/Users/max/.codex/config.toml` to `/Users/max/Projects/my-codex`. Repository `.agents/plugins/marketplace.json` and `.agents/plugins/install-manifest.json` remain the optional plugin-distribution source and are not deletion targets.
4. The exact rollback root `/Users/max/.codex/backups/my-codex/universal-agent-skills/20260820T184942Z` occupies 912 KiB and contains 755,090 regular-file bytes, 64 files, 138 directories, zero symlinks, and zero special nodes. It is entirely `max:staff`; directories are `0700`, ordinary files are `0600`, and the sole executable gate is `0700`.
5. Independent read-only audits found no repository or current runtime consumer of the rollback root or empty cache namespace. Removing the live marketplace registration does not affect universal discovery or Watcher; plugin mode can re-register the repository marketplace before installation.
6. Git can reconstruct functionally equivalent plugin caches, hooks, agent support, and marketplace registration, but cannot byte-for-byte reconstruct the three old cache archives, pre-cutover config and hook snapshots, 55 raw cutover evidence files, or Codex-generated timestamps. The user explicitly accepted that irreversible loss.
7. Current hooks SHA-256 is `f24da46573b7130a0684213dc096dbae1413d27a6ea48392fc7db152cc1f0520`; agent support SHA-256 is `66aa398bca3cf1793914613b943a611ee11b5461f3e99562ba443a251d3f0d5e`.
8. The canonical JSON SHA-256 of current `/Users/max/.codex/config.toml` after removing only `marketplaces.my-codex` in memory is `5783be69c8778981c11ade709c0c8f1c58b984494b32a7fdfb05a0d55ca35dc1`. M1 must reproduce that semantic fingerprint after the real CLI removal and separately prove the section is absent.
9. The dated M0 Watcher stat-inventory SHA-256 is `76fa1304b7842334ac37b626e5a98922a81f895b586d27a3c9b4e9348b8f5291`, generated literally by `find /Users/max/.codex/watcher -xdev -print0 | sort -z | xargs -0 stat -f '%N|%HT|%Sp|%z|%m' | shasum -a 256`. The protected historical file `evidence/watcher-state-before.txt` has file SHA-256 `391c158f5e03ff3fab3d59dc414ab41c2b14e74802be63d337cc9cc20f414719` because it is a differently ordered and serialized historical stat inventory; M1 does not use that historical file as its comparator. Because ordinary hooks may update Watcher between turns, M1 prints and freezes the value generated immediately before apply and requires every post-removal and post-validation value in that same execution block to equal it; it never substitutes the dated M0 value or a later value inside that comparison.

Current truth sources read:

1. Root `AGENTS.md`, `README.md`, `.gitignore`, `.agents/plugins/marketplace.json`, `.agents/plugins/install-manifest.json`, and current TODO indexes.
2. `docs/todo/archive/universal-agent-skills-migration.md`, the superseded cleanup follow-up, and the protected M5 execution summary and inventories.
3. Current `~/.codex/config.toml`, plugin and marketplace CLI inventories, universal links, hooks, agent support, Watcher state, backup tree, and cache tree.
4. `workflow:long-running-goal`, `watcher:housekeeping`, `mattpocock-skills:grilling`, `mattpocock-skills:domain-modeling`, and GitHub publishing guidance.

## Loop Blueprint / Harness

Execution mode: `Manual staged execution`

Loop-shaped execution: `Not applicable: manual staged execution is sufficient because this is a one-time serialized cleanup with no recurring trigger, connector workflow, parallel worktree, or automated orchestration.`

1. Trigger: the user's 2026-08-21 permanent-delete confirmation resumes this goal.
2. Inputs: this goal, repository `main`, exact local target inventory, config and marketplace state, universal closure, hashes, and independent review findings.
3. Triage and orchestration: the primary agent owns the serialized plan, integration, mutation, validation, and final decision; read-only reviewers independently verify exact ownership and post-apply boundaries.
4. Worktree and isolation: one branch, `codex/universal-agent-skills-cleanup`, in the shared checkout; no parallel writes or alternate worktrees.
5. Skills and context: the primary agent follows `workflow:long-running-goal` and `watcher:housekeeping`; reviewers read this contract and the exact current diff or runtime inventory.
6. Connector read/write boundaries: local filesystem and Codex CLI reads and exact mutations are authorized. Git and GitHub branch push, Draft PR creation/update, ready transition, merge, and safe merged-branch deletion are authorized. No other connector, message, issue, automation, hook definition, or external system write is authorized.
7. Independent verification: a read-only Contract reviewer must return Clean before permanent deletion, and a separate read-only runtime review must return Clean after apply before Close.
8. Runtime hard stops: stop before permanent deletion if exact ownership/type/count changes reveal unknown content; a target plugin becomes installed; the marketplace config diff is broader than the one section; universal closure, hashes, or Watcher comparison fails; or a required reviewer cannot produce a reliable verdict. After deletion, diagnose any failure directly without inventing restored raw evidence.
9. Durable learning: record the preflight decision, exact deletion evidence, functional recovery boundary, validation, reviews, and Git revisions in this goal, then archive it under `docs/todo/archive`.

## Pre-Approval / YOLO

1. Pre-approved YOLO local operations: non-destructive local planning and documentation edits, exact inventory and fingerprint reads, universal closure and package validation, Git branch and commit operations, and validation reruns. The separately authorized destructive set below is excluded from the YOLO field and remains subject to its exact pre-delete gate.
2. Pre-approved external reads/writes: GitHub repository and PR reads; push `codex/universal-agent-skills-cleanup`; create and update its Draft PR; mark it ready; merge it after every gate passes; delete only its fully merged local and remote branch.
3. Authorized destructive set:
   - remove only the live `my-codex` marketplace registration with `/Applications/ChatGPT.app/Contents/Resources/codex plugin marketplace remove --json my-codex`;
   - permanently remove only `/Users/max/.codex/backups/my-codex/universal-agent-skills/20260820T184942Z` after the pre-delete gate;
   - remove `/Users/max/.codex/plugins/cache/my-codex` only with non-recursive `rmdir` after proving it is empty.
   - Never remove `/Users/max/.codex/backups/my-codex/universal-agent-skills`, `/Users/max/.codex/backups/my-codex`, `/Users/max/.codex/backups`, or any generic parent/cache namespace.
4. Recovery boundary: before permanent deletion, restore the marketplace with `/Applications/ChatGPT.app/Contents/Resources/codex plugin marketplace add --json /Users/max/Projects/my-codex` if its removal or validation fails. The empty cache directory can be recreated by plugin installation. The permanently deleted rollback root has no local recovery; Git provides only functional reconstruction.
5. Runtime hard stops: the conditions in the harness boundary are the only stops after Ready.
6. Non-stops: ordinary review fixes, documentation sync, validation retries with a clear local next step, Git checkpoints, authorized PR state transitions, and timing rebaselines.

## Design Principles

1. Active discovery and source authority are protected; cleanup removes obsolete rollback material, not current capabilities.
2. Exact-path ownership is required before destructive action; no glob, environment-variable target, symlink traversal, generic cache sweep, or broad recursive root is allowed.
3. The live config mutation must be semantically exact and independently reversible before the irreversible file deletion begins.
4. Watcher durable state, current hooks, agent support, unrelated config, generic ignored caches, dependencies, and historical repository archives are explicitly excluded.
5. Git is accepted as functional recovery, not as a claim of byte-identical recovery for deleted local evidence.

## Non-Goals / Future Boundary

This goal does not:

1. Delete or change any of the 34 universal skill links or their repository targets.
2. Delete repository plugin manifests, source skills, optional plugin packaging, tooling venvs, `node_modules`, generic `__pycache__`, or unrelated plugin caches.
3. Change current hook definitions, hook trust, agent support, Watcher logs/reports/proposals/snapshots/backups/state, or unrelated Codex configuration.
4. Install or test the plugin profile on this Mac; dry-run reconstruction evidence is sufficient because another environment is the future execution target.
5. Rewrite the closed migration archive's historical changed-file records or raw evidence claims.

## Milestone Status

| Milestone | Status | Review | Checkpoint |
|---|---|---|---|
| M0 Contract, Inventory, and Deletion Freeze | Done | Passed | Done |
| M1 Exact Local Cleanup and Validation | Ready | Pending | Pending |
| Close Goal Closure and Archive | Not Started | Pending | Pending |

## M0 Contract, Inventory, and Deletion Freeze

Status: `Done`

Scope:

1. Convert the deferred cleanup note into this continuation-ready goal and align active navigation.
2. Reproduce the exact target inventory, consumer audit, functional reconstruction proof, and failure boundaries.
3. Obtain independent read-only Contract and deletion review before any cleanup mutation.

Review gate:

1. `check_goal_ready.py`, TODO index ownership, planning-tree topology, Markdown links, and `git diff --check` pass.
2. The exact target set has zero symlink or special-node escape and no current runtime consumer.
3. Independent review returns Clean on ownership, command order, recovery, exclusions, fingerprints, and authorization.

Validation:

```bash
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.agents/skills/long-running-goal/scripts/check_goal_ready.py docs/todo/universal-agent-skills-cleanup.md
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.agents/skills/long-running-goal/scripts/check_md_links.py docs/todo
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.agents/skills/long-running-goal/scripts/check_todo_index.py docs/todo/universal-agent-skills-cleanup.md docs/todo/README.md
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.agents/skills/doc-alignment/scripts/check_planning_tree.py docs/todo
git diff --check
```

Execution evidence: `2026-08-21 readiness, active TODO index, Markdown links, planning-tree topology, zsh syntax, exact read-only oracle prefix, forced-failure present-state rollback, and git diff checks all passed. Independent Contract and deletion/runtime reviewers each returned Clean after verifying the literal command order, serializer boundaries, transition rollback, protected state, and exact destructive scope. No cleanup runtime mutation occurred during M0.`

Checkpoint component: `M0 Contract, Inventory, and Deletion Freeze`

Checkpoint evidence: `Commit 76b1af37ec53bf20fb09164e5abfc97fbbe408be published the reviewed contract on codex/universal-agent-skills-cleanup; Draft PR #12 is https://github.com/zzzhty/my-codex/pull/12.`

## M1 Exact Local Cleanup and Validation

Status: `Ready`

Scope:

1. Re-run the frozen pre-delete inventory and capture immediate config, hooks, agent-support, universal-link, and Watcher fingerprints in memory.
2. Remove the live marketplace registration; prove the entire config excluding that exact section is unchanged, universal closure passes, and protected boundaries are unchanged. Recover the marketplace and stop if this gate fails.
3. Permanently delete only the exact rollback root, remove only confirmed-empty owned namespaces with `rmdir`, and prove the exact targets are absent.
4. Re-run universal closure, hashes, Watcher comparison, plugin and source validation, stale active-doc scan, and independent post-apply runtime review.

Exact apply order:

1. Immediately before mutation, require the rollback target to be a real directory and not a symlink; require exactly 64 regular files, 138 directories, 755,090 regular-file bytes, zero non-file/non-directory nodes, and only `max:staff` ownership. Require the live cache namespace to be a real empty directory, all three target selectors to be not installed, and universal discovery to contain exactly 34 symlinks and zero non-link entries.
2. Capture the Watcher inventory in memory with `find /Users/max/.codex/watcher -xdev -print0 | sort -z | xargs -0 stat -f '%N|%HT|%Sp|%z|%m' | shasum -a 256`. Capture current hook and agent-support hashes. Do not write a temporary snapshot.
3. Remove only the marketplace registration with `/Applications/ChatGPT.app/Contents/Resources/codex plugin marketplace remove --json my-codex`.
4. Parse the resulting config with `tomllib`, require `marketplaces.my-codex` to be absent, and require the canonical sorted compact JSON SHA-256 of the entire config to equal `5783be69c8778981c11ade709c0c8f1c58b984494b32a7fdfb05a0d55ca35dc1`. Run universal closure and compare the immediate Watcher, hook, agent-support, and 34-link fingerprints. On any failure, run `/Applications/ChatGPT.app/Contents/Resources/codex plugin marketplace add --json /Users/max/Projects/my-codex`, verify the restored source binding, and stop before file deletion.
5. Revalidate the exact rollback inventory without accepting drift, then permanently execute `/bin/rm -R /Users/max/.codex/backups/my-codex/universal-agent-skills/20260820T184942Z`. Use non-recursive `rmdir` only for the independently proven-empty live cache namespace; a concurrent entry makes `rmdir` fail closed. Preserve every backup parent.
6. Require every exact cleanup target to be absent, rerun universal closure and repository validators, and again require the Watcher, hooks, agent-support, config, and 34-link fingerprints to match the immediate pre-apply contract.

Frozen executable oracle:

Run the following single fail-fast block from `/Users/max/Projects/my-codex`. It writes no snapshot or task cache. Its rollback trap applies only between marketplace removal and the irreversible deletion gate; after every semantic and protected-state check succeeds, the trap is deliberately disarmed and the literal permanent-delete command runs.

```zsh
set -euo pipefail

assert_destructive_inventory() {
/Users/max/.codex/venvs/my-codex/bin/python -B - <<'PY'
import collections
import grp
import os
import pathlib
import pwd
import stat

root = pathlib.Path("/Users/max/.codex/backups/my-codex/universal-agent-skills/20260820T184942Z")
cache = pathlib.Path("/Users/max/.codex/plugins/cache/my-codex")
gate = root / "evidence/qualified-identity-gate.zsh"

for ancestor in (
    pathlib.Path("/Users/max/.codex/backups"),
    pathlib.Path("/Users/max/.codex/backups/my-codex"),
    pathlib.Path("/Users/max/.codex/backups/my-codex/universal-agent-skills"),
    pathlib.Path("/Users/max/.codex/plugins"),
    pathlib.Path("/Users/max/.codex/plugins/cache"),
):
    value = ancestor.lstat()
    assert stat.S_ISDIR(value.st_mode) and not ancestor.is_symlink(), ancestor

root_stat = root.lstat()
assert stat.S_ISDIR(root_stat.st_mode) and not root.is_symlink(), root
root_device = root_stat.st_dev
stack = [root]
directories = 0
files = 0
file_bytes = 0
file_modes = collections.Counter()
while stack:
    path = stack.pop()
    value = path.lstat()
    assert value.st_dev == root_device, path
    assert pwd.getpwuid(value.st_uid).pw_name == "max", path
    assert grp.getgrgid(value.st_gid).gr_name == "staff", path
    mode = stat.S_IMODE(value.st_mode)
    if stat.S_ISDIR(value.st_mode):
        assert mode == 0o700, path
        directories += 1
        stack.extend(sorted((pathlib.Path(item.path) for item in os.scandir(path)), reverse=True))
    elif stat.S_ISREG(value.st_mode):
        assert mode == (0o700 if path == gate else 0o600), path
        files += 1
        file_bytes += value.st_size
        file_modes[mode] += 1
    else:
        raise AssertionError(f"unsupported node: {path}")
assert (files, directories, file_bytes) == (64, 138, 755090)
assert file_modes == collections.Counter({0o600: 63, 0o700: 1})

cache_stat = cache.lstat()
assert stat.S_ISDIR(cache_stat.st_mode) and not cache.is_symlink(), cache
assert pwd.getpwuid(cache_stat.st_uid).pw_name == "max", cache
assert grp.getgrgid(cache_stat.st_gid).gr_name == "staff", cache
assert not any(cache.iterdir()), cache
print("destructive-inventory=PASS")
PY
}

assert_universal_projection() {
/Users/max/.codex/venvs/my-codex/bin/python -B - <<'PY'
import pathlib
import stat

root = pathlib.Path("/Users/max/.agents/skills")
repository = pathlib.Path("/Users/max/Projects/my-codex").resolve(strict=True)
root_stat = root.lstat()
assert stat.S_ISDIR(root_stat.st_mode) and not root.is_symlink(), root
entries = sorted(root.iterdir())
assert len(entries) == 34, len(entries)
for entry in entries:
    assert entry.is_symlink(), entry
    target = entry.resolve(strict=True)
    assert target.is_relative_to(repository), (entry, target)
    assert (target / "SKILL.md").is_file(), target
print("universal-links=34; nonlinks=0")
PY
/Users/max/.codex/venvs/my-codex/bin/python -B scripts/sync_agents_skills.py --check --prune
}

assert_target_plugins_absent() {
/Applications/ChatGPT.app/Contents/Resources/codex plugin list --json |
/Users/max/.codex/venvs/my-codex/bin/python -B -c 'import json,sys; data=json.load(sys.stdin); targets={"watcher@my-codex","workflow@my-codex","mattpocock-skills@my-codex"}; found=sorted(item["pluginId"] for item in data["installed"] if item["pluginId"] in targets); assert not found, found; print("target-plugins=absent")'
}

assert_marketplace_present() {
/Applications/ChatGPT.app/Contents/Resources/codex plugin marketplace list --json |
/Users/max/.codex/venvs/my-codex/bin/python -B -c 'import json,sys; items=[item for item in json.load(sys.stdin)["marketplaces"] if item["name"]=="my-codex"]; assert len(items)==1, items; item=items[0]; assert item["root"]=="/Users/max/Projects/my-codex", item; assert item["marketplaceSource"]=={"sourceType":"local","source":"/Users/max/Projects/my-codex"}, item; print("marketplace=present-local")'
}

assert_marketplace_absent() {
/Applications/ChatGPT.app/Contents/Resources/codex plugin marketplace list --json |
/Users/max/.codex/venvs/my-codex/bin/python -B -c 'import json,sys; items=[item for item in json.load(sys.stdin)["marketplaces"] if item["name"]=="my-codex"]; assert not items, items; print("marketplace=absent")'
}

assert_config_before_removal() {
/Users/max/.codex/venvs/my-codex/bin/python -B - <<'PY'
import hashlib
import json
import pathlib
import tomllib

config = tomllib.loads(pathlib.Path("/Users/max/.codex/config.toml").read_text())
entry = config["marketplaces"].pop("my-codex")
assert entry["source_type"] == "local", entry
assert entry["source"] == "/Users/max/Projects/my-codex", entry
payload = json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
digest = hashlib.sha256(payload).hexdigest()
assert digest == "5783be69c8778981c11ade709c0c8f1c58b984494b32a7fdfb05a0d55ca35dc1", digest
print(f"config-without-my-codex={digest}")
PY
}

assert_config_after_removal() {
/Users/max/.codex/venvs/my-codex/bin/python -B - <<'PY'
import hashlib
import json
import pathlib
import tomllib

config = tomllib.loads(pathlib.Path("/Users/max/.codex/config.toml").read_text())
assert "my-codex" not in config.get("marketplaces", {}), config.get("marketplaces", {})
payload = json.dumps(config, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
digest = hashlib.sha256(payload).hexdigest()
assert digest == "5783be69c8778981c11ade709c0c8f1c58b984494b32a7fdfb05a0d55ca35dc1", digest
print(f"config-after-removal={digest}")
PY
}

watcher_fingerprint() {
find /Users/max/.codex/watcher -xdev -print0 |
sort -z |
xargs -0 stat -f '%N|%HT|%Sp|%z|%m' |
shasum -a 256 |
awk '{print $1}'
}

assert_destructive_inventory
assert_universal_projection
assert_target_plugins_absent
assert_marketplace_present
assert_config_before_removal

cleanup_hooks_before="$(shasum -a 256 /Users/max/.codex/hooks.json | awk '{print $1}')"
cleanup_agent_support_before="$(shasum -a 256 /Users/max/.codex/agents/operating-principles.md | awk '{print $1}')"
cleanup_watcher_before="$(watcher_fingerprint)"
[[ "$cleanup_hooks_before" == "f24da46573b7130a0684213dc096dbae1413d27a6ea48392fc7db152cc1f0520" ]]
[[ "$cleanup_agent_support_before" == "66aa398bca3cf1793914613b943a611ee11b5461f3e99562ba443a251d3f0d5e" ]]
[[ ${#cleanup_watcher_before} -eq 64 ]]
[[ "$cleanup_watcher_before" != *[^0-9a-f]* ]]
print "watcher-immediate-before=$cleanup_watcher_before"

cleanup_marketplace_transition_armed=0
cleanup_restore_marketplace_on_exit() {
    cleanup_status=$?
    trap - EXIT
    if (( cleanup_status != 0 && cleanup_marketplace_transition_armed == 1 )); then
        set +e
        assert_marketplace_present
        cleanup_present_status=$?
        cleanup_restore_status=0
        cleanup_restore_verify_status=0
        cleanup_restore_config_status=0
        if (( cleanup_present_status != 0 )); then
            assert_marketplace_absent
            cleanup_absent_status=$?
            if (( cleanup_absent_status == 0 )); then
                /Applications/ChatGPT.app/Contents/Resources/codex plugin marketplace add --json /Users/max/Projects/my-codex
                cleanup_restore_status=$?
            else
                cleanup_restore_status=1
                print -u2 "marketplace state is neither exact present-local nor absent"
            fi
        fi
        if (( cleanup_restore_status == 0 )); then
            assert_marketplace_present
            cleanup_restore_verify_status=$?
            assert_config_before_removal
            cleanup_restore_config_status=$?
        fi
        set -e
        if (( cleanup_restore_status != 0 || cleanup_restore_verify_status != 0 || cleanup_restore_config_status != 0 )); then
            print -u2 "marketplace rollback failed; inspect /Users/max/.codex/config.toml"
        fi
    fi
    exit "$cleanup_status"
}
trap cleanup_restore_marketplace_on_exit EXIT

cleanup_marketplace_transition_armed=1
/Applications/ChatGPT.app/Contents/Resources/codex plugin marketplace remove --json my-codex
assert_marketplace_absent
assert_config_after_removal
assert_target_plugins_absent
assert_universal_projection
/Users/max/.codex/venvs/my-codex/bin/python -B scripts/check_my_codex.py --discovery-profile universal
[[ "$(shasum -a 256 /Users/max/.codex/hooks.json | awk '{print $1}')" == "$cleanup_hooks_before" ]]
[[ "$(shasum -a 256 /Users/max/.codex/agents/operating-principles.md | awk '{print $1}')" == "$cleanup_agent_support_before" ]]
[[ "$(watcher_fingerprint)" == "$cleanup_watcher_before" ]]
assert_destructive_inventory

cleanup_marketplace_transition_armed=0
trap - EXIT
/bin/rm -R /Users/max/.codex/backups/my-codex/universal-agent-skills/20260820T184942Z
/bin/rmdir /Users/max/.codex/plugins/cache/my-codex

/Users/max/.codex/venvs/my-codex/bin/python -B - <<'PY'
import pathlib

for path in (
    pathlib.Path("/Users/max/.codex/backups/my-codex/universal-agent-skills/20260820T184942Z"),
    pathlib.Path("/Users/max/.codex/plugins/cache/my-codex"),
):
    assert not path.exists() and not path.is_symlink(), path
print("cleanup-targets=absent")
PY

assert_marketplace_absent
assert_config_after_removal
assert_target_plugins_absent
assert_universal_projection
/Users/max/.codex/venvs/my-codex/bin/python -B scripts/check_my_codex.py --discovery-profile universal
/Users/max/.codex/venvs/my-codex/bin/python -B scripts/update_mattpocock_skills.py --validate-only
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/watcher
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/workflow
/Users/max/.codex/venvs/my-codex/bin/python -B - <<'PY'
import pathlib

goal = pathlib.Path("docs/todo/universal-agent-skills-cleanup.md")
archive = pathlib.Path("docs/todo/archive")
paths = [pathlib.Path("README.md"), *pathlib.Path("docs").rglob("*.md")]
needles = (
    "universal-agent-skills-cleanup-follow-up.md",
    "/Users/max/.codex/backups/my-codex/universal-agent-skills/20260820T184942Z",
)
hits = []
for path in paths:
    if path == goal or path.is_relative_to(archive):
        continue
    text = path.read_text()
    hits.extend((str(path), needle) for needle in needles if needle in text)
assert not hits, hits
print("stale-active-docs=absent")
PY
[[ "$(shasum -a 256 /Users/max/.codex/hooks.json | awk '{print $1}')" == "$cleanup_hooks_before" ]]
[[ "$(shasum -a 256 /Users/max/.codex/agents/operating-principles.md | awk '{print $1}')" == "$cleanup_agent_support_before" ]]
[[ "$(watcher_fingerprint)" == "$cleanup_watcher_before" ]]
git diff --check
print "M1 exact cleanup oracle=PASS"
```

Review gate:

1. The only live configuration change is absence of `marketplaces.my-codex`; no target plugin is installed and the Git marketplace source remains reconstructable.
2. The rollback root and empty `my-codex` cache namespace are absent; active universal discovery remains exactly 34 repository-owned symlinks.
3. Hooks, agent support, and the immediate pre/post Watcher stat inventory are identical.
4. Universal closure and all repository-owned package validators pass with zero warnings, and independent post-apply review returns Clean.

Validation:

```bash
/Users/max/.codex/venvs/my-codex/bin/python -B scripts/check_my_codex.py --discovery-profile universal
/Users/max/.codex/venvs/my-codex/bin/python -B scripts/sync_agents_skills.py --check --prune
/Users/max/.codex/venvs/my-codex/bin/python -B scripts/update_mattpocock_skills.py --validate-only
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/watcher
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/workflow
git diff --check
```

Execution evidence: `Pending M1 apply and post-apply validation.`

Checkpoint component: `Pending until the M1 review gate passes.`

Checkpoint evidence: `Pending M1 Git commit and Draft PR update.`

## Close Goal Closure and Archive

Status: `Not Started`

Close prerequisites:

1. M0 and M1 are `Done`, `Review=Passed`, and `Checkpoint=Done`.
2. The exact cleanup and protected-state acceptance matrix has current evidence.
3. The goal is moved to `docs/todo/archive/universal-agent-skills-cleanup.md`, active navigation is removed, and both TODO indexes describe the closed record.
4. The Close PR is mergeable; after merge, the branch is deleted only if it contains no commits absent from `main`.
5. The Task Temporary Cache / Housekeeping outcome is explicitly `Not applicable` with no root created.

Final validation:

```bash
/Users/max/.codex/venvs/my-codex/bin/python -B scripts/check_my_codex.py --discovery-profile universal
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.agents/skills/long-running-goal/scripts/check_goal_ready.py docs/todo/archive/universal-agent-skills-cleanup.md
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.agents/skills/long-running-goal/scripts/check_md_links.py docs/todo
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.agents/skills/long-running-goal/scripts/check_todo_index.py --mode closed --archived-goal docs/todo/archive/universal-agent-skills-cleanup.md docs/todo/universal-agent-skills-cleanup.md docs/todo/README.md docs/todo/archive/README.md
/Users/max/.codex/venvs/my-codex/bin/python -B /Users/max/.agents/skills/doc-alignment/scripts/check_planning_tree.py docs/todo
git diff --check
```

Close execution evidence: `Pending after M1 and archive/index completion.`

Checkpoint component: `Pending until the Close review gate passes.`

Close checkpoint evidence: `Pending Close Git revision and PR merge.`

Close rollback: `Restore active navigation only if closure documentation is incomplete. Do not recreate the permanently deleted local rollback root or silently re-register the marketplace after successful cleanup.`

## Current Risks

1. Permanent deletion intentionally removes byte-identical historical recovery and forensic detail. This is accepted, not a recoverable risk.
2. A plugin-profile refresh in the future will re-register `my-codex` and recreate its cache namespace by design; that is a new explicit profile transition, not cleanup regression.
3. Watcher state can legitimately change between user turns due hooks. M1 therefore freezes and compares an immediate pre/post apply inventory; any change inside that boundary is a hard stop.

## Recommended Goal Prompt

```text
Execute docs/todo/universal-agent-skills-cleanup.md strictly in order M0 -> M1 -> Close. Preserve the active universal profile, source checkout, unrelated config, current hooks and agent support, and all Watcher durable state. M0 performs no cleanup mutation and requires independent Clean review. M1 first removes only the live my-codex marketplace registration and proves the exact semantic config diff plus universal health; only then permanently deletes the frozen rollback root and confirmed-empty owned namespaces. Use no temporary cache root. Publish the authorized Draft PR, merge only after every gate passes, prove the goal branch is fully contained in main, delete it locally and remotely, archive the goal, and stop only at a declared runtime hard stop.
```

## Related Documents

1. [Universal Agent Skills Migration archive](archive/universal-agent-skills-migration.md)
2. [TODO index](README.md)
3. [Repository discovery-profile guide](../../README.md#skill-discovery-profiles)
