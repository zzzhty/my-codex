from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from repo_skill_catalog import load_repo_skill_catalog  # noqa: E402
from skill_discovery_profiles import (  # noqa: E402
    CheckProfileOptions,
    DiscoveryProfile,
    RefreshProfileOptions,
    ensure_plugin_profile_covers_catalog,
    parse_discovery_profile,
    validate_check_profile,
    validate_refresh_profile,
)


def write_skill(root: Path, plugin: str, name: str) -> None:
    skill = root / "plugins" / plugin / "skills" / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: fixture\n---\n",
        encoding="utf-8",
    )


class DiscoveryProfilePolicyTests(unittest.TestCase):
    def test_profile_is_required_and_has_only_two_values(self) -> None:
        self.assertIs(parse_discovery_profile("universal"), DiscoveryProfile.UNIVERSAL)
        self.assertIs(parse_discovery_profile("plugin"), DiscoveryProfile.PLUGIN)
        with self.assertRaisesRegex(SystemExit, "invalid discovery profile"):
            parse_discovery_profile("")
        with self.assertRaisesRegex(SystemExit, "invalid discovery profile"):
            parse_discovery_profile("mixed")

    def test_legacy_bypasses_are_rejected_for_refresh_and_check(self) -> None:
        refresh_flags = ("skip_marketplace", "skip_plugins", "skip_agents_skills")
        for flag in refresh_flags:
            with self.subTest(flag=flag), self.assertRaisesRegex(SystemExit, "legacy bypass"):
                validate_refresh_profile(
                    RefreshProfileOptions(
                        profile=DiscoveryProfile.PLUGIN,
                        **{flag: True},
                    )
                )
        for flag in ("skip_plugins", "skip_agents_skills"):
            with self.subTest(check_flag=flag), self.assertRaisesRegex(SystemExit, "legacy bypass"):
                validate_check_profile(
                    CheckProfileOptions(
                        profile=DiscoveryProfile.UNIVERSAL,
                        **{flag: True},
                    )
                )

    def test_universal_rejects_plugin_selection_and_pruning(self) -> None:
        with self.assertRaisesRegex(SystemExit, "--plugin"):
            validate_refresh_profile(
                RefreshProfileOptions(
                    profile=DiscoveryProfile.UNIVERSAL,
                    selected_plugins=("watcher",),
                )
            )
        with self.assertRaisesRegex(SystemExit, "--prune-plugins"):
            validate_refresh_profile(
                RefreshProfileOptions(
                    profile=DiscoveryProfile.UNIVERSAL,
                    prune_plugins=True,
                )
            )

    def test_plugin_refresh_may_select_packages_but_closure_check_may_not(self) -> None:
        validate_refresh_profile(
            RefreshProfileOptions(
                profile=DiscoveryProfile.PLUGIN,
                selected_plugins=("watcher",),
            )
        )
        with self.assertRaisesRegex(SystemExit, "cannot narrow"):
            validate_check_profile(
                CheckProfileOptions(
                    profile=DiscoveryProfile.PLUGIN,
                    selected_plugins=("watcher",),
                )
            )

    def test_plugin_profile_must_cover_exact_skills_bearing_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            write_skill(root, "alpha", "one")
            write_skill(root, "beta", "two")
            catalog = load_repo_skill_catalog(root)

            ensure_plugin_profile_covers_catalog(
                catalog,
                ["alpha@test", "beta@test"],
                marketplace_name="test",
            )
            with self.assertRaisesRegex(SystemExit, "missing skills-bearing plugins"):
                ensure_plugin_profile_covers_catalog(
                    catalog,
                    ["alpha@test"],
                    marketplace_name="test",
                )
            with self.assertRaisesRegex(SystemExit, "without canonical skills"):
                ensure_plugin_profile_covers_catalog(
                    catalog,
                    ["alpha@test", "beta@test", "adapter@test"],
                    marketplace_name="test",
                )


if __name__ == "__main__":
    unittest.main()
