# Make Git the universal skill discovery authority

Repository `SKILL.md` content is the only canonical skill source. Each runtime must explicitly select one mutually exclusive discovery profile: `universal` exposes bare frontmatter callable identities through repository-owned user-level links and hooks without an adapter, while `plugin` packages the same source as an optional compatibility and rollback distribution.

## Decision

Universal discovery is the production target and must not read marketplace metadata or plugin cache as source authority. Plugin packaging remains buildable, but it is inactive whenever universal discovery is active and may not introduce a second catalog, fallback path, zero-skill adapter, or alternate callable identity. Watcher retains its namespaced durable attribution identities while deriving callable skill inventory from repository authority.

## Consequences

Refresh, check, upgrade, and wrapper entry points require an explicit `universal` or `plugin` profile, which is an intentional CLI compatibility break. Literal plugin-qualified invocation selectors may differ between profiles even though bare callable identity and routing semantics remain stable. Cutover must therefore compare profiles sequentially, retain a proven plugin rollback baseline, and defer deletion until a separately preflighted cleanup goal has enough universal-profile stability evidence.
