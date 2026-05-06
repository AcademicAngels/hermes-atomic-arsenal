#!/usr/bin/env python3
"""Install Hermes local extensions from this plugin-pack repository.

Hermes currently installs one plugin per Git repository via
``hermes plugins install``. This package intentionally contains multiple
plugins, so this script copies selected plugin directories into
``$HERMES_HOME/plugins`` and can optionally enable them in ``config.yaml``.

The repository can also carry local skills and Ralph Loop templates. These are
copied into ``$HERMES_HOME/skills`` and ``$HERMES_HOME/loops`` when requested.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO_ROOT / "plugins"
SKILLS_DIR = REPO_ROOT / "skills"
LOOPS_DIR = REPO_ROOT / "loops"


def _plugin_names() -> list[str]:
    if not PLUGINS_DIR.is_dir():
        return []
    return sorted(
        p.name
        for p in PLUGINS_DIR.iterdir()
        if p.is_dir() and (p / "plugin.yaml").exists() and (p / "__init__.py").exists()
    )


def _skill_names() -> list[str]:
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(
        p.name
        for p in SKILLS_DIR.iterdir()
        if p.is_dir() and (p / "SKILL.md").exists()
    )


def _loop_names() -> list[str]:
    if not LOOPS_DIR.is_dir():
        return []
    return sorted(
        p.name
        for p in LOOPS_DIR.iterdir()
        if p.is_dir() and (p / "RALPH.md").exists()
    )


def _hermes_home(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    import os

    env_value = os.environ.get("HERMES_HOME")
    if env_value:
        return Path(env_value).expanduser().resolve()
    return Path.home() / ".hermes"


def _copy_plugin(name: str, hermes_home: Path, *, force: bool) -> Path:
    source = PLUGINS_DIR / name
    if not source.is_dir():
        raise SystemExit(f"Unknown plugin: {name}")
    target = hermes_home / "plugins" / name
    if target.exists():
        if not force:
            raise SystemExit(f"{target} already exists; re-run with --force to replace it")
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    return target


def _copy_named_dir(kind: str, source_root: Path, name: str, target_root: Path, *, force: bool) -> Path:
    source = source_root / name
    if not source.is_dir():
        raise SystemExit(f"Unknown {kind}: {name}")
    target = target_root / name
    if target.exists():
        if not force:
            raise SystemExit(f"{target} already exists; re-run with --force to replace it")
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    return target


def _enable_plugin(name: str, hermes_home: Path, hermes_bin: str) -> None:
    subprocess.run(
        [hermes_bin, "plugins", "enable", name],
        check=True,
        env={**__import__("os").environ, "HERMES_HOME": str(hermes_home)},
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Install plugins from this Hermes plugin pack.")
    parser.add_argument("plugins", nargs="*", help="Plugin names to install. Defaults to all.")
    parser.add_argument("--home", help="Hermes home directory. Defaults to $HERMES_HOME or ~/.hermes.")
    parser.add_argument("--force", action="store_true", help="Replace existing installed plugin directories.")
    parser.add_argument("--enable", action="store_true", help="Enable installed plugins after copying.")
    parser.add_argument("--skip-plugins", action="store_true", help="Do not install plugin directories.")
    parser.add_argument("--skills", nargs="*", help="Skill names to install. Use without values to install all skills.")
    parser.add_argument("--loops", nargs="*", help="Ralph Loop template names to install. Use without values to install all loops.")
    parser.add_argument("--all-assets", action="store_true", help="Install plugins, skills, and loops.")
    parser.add_argument("--hermes-bin", default="/usr/local/bin/hermes", help="Hermes CLI path for --enable.")
    args = parser.parse_args()

    hermes_home = _hermes_home(args.home)

    install_plugins = not args.skip_plugins
    install_skills = args.all_assets or args.skills is not None
    install_loops = args.all_assets or args.loops is not None

    if install_plugins:
        available = _plugin_names()
        selected = args.plugins or available
        unknown = sorted(set(selected) - set(available))
        if unknown:
            print(f"Unknown plugin(s): {', '.join(unknown)}", file=sys.stderr)
            print(f"Available: {', '.join(available) or '(none)'}", file=sys.stderr)
            return 2

        for name in selected:
            target = _copy_plugin(name, hermes_home, force=args.force)
            print(f"Installed plugin {name} -> {target}")
            if args.enable:
                _enable_plugin(name, hermes_home, args.hermes_bin)

    if install_skills:
        available = _skill_names()
        selected = args.skills or available
        unknown = sorted(set(selected) - set(available))
        if unknown:
            print(f"Unknown skill(s): {', '.join(unknown)}", file=sys.stderr)
            print(f"Available: {', '.join(available) or '(none)'}", file=sys.stderr)
            return 2

        for name in selected:
            target = _copy_named_dir("skill", SKILLS_DIR, name, hermes_home / "skills", force=args.force)
            print(f"Installed skill {name} -> {target}")

    if install_loops:
        available = _loop_names()
        selected = args.loops or available
        unknown = sorted(set(selected) - set(available))
        if unknown:
            print(f"Unknown loop(s): {', '.join(unknown)}", file=sys.stderr)
            print(f"Available: {', '.join(available) or '(none)'}", file=sys.stderr)
            return 2

        for name in selected:
            target = _copy_named_dir("loop", LOOPS_DIR, name, hermes_home / "loops", force=args.force)
            print(f"Installed loop {name} -> {target}")

    if install_plugins and not args.enable:
        print("Enable plugins with: hermes plugins enable <name>")
    print("Restart Hermes gateway/native service for changes to take effect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
