#!/usr/bin/env python3
"""Install Hermes local plugins from this plugin-pack repository.

Hermes currently installs one plugin per Git repository via
``hermes plugins install``. This package intentionally contains multiple
plugins, so this script copies selected plugin directories into
``$HERMES_HOME/plugins`` and can optionally enable them in ``config.yaml``.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = REPO_ROOT / "plugins"


def _plugin_names() -> list[str]:
    if not PLUGINS_DIR.is_dir():
        return []
    return sorted(
        p.name
        for p in PLUGINS_DIR.iterdir()
        if p.is_dir() and (p / "plugin.yaml").exists() and (p / "__init__.py").exists()
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
    parser.add_argument("--hermes-bin", default="/usr/local/bin/hermes", help="Hermes CLI path for --enable.")
    args = parser.parse_args()

    available = _plugin_names()
    selected = args.plugins or available
    unknown = sorted(set(selected) - set(available))
    if unknown:
        print(f"Unknown plugin(s): {', '.join(unknown)}", file=sys.stderr)
        print(f"Available: {', '.join(available) or '(none)'}", file=sys.stderr)
        return 2

    hermes_home = _hermes_home(args.home)
    for name in selected:
        target = _copy_plugin(name, hermes_home, force=args.force)
        print(f"Installed {name} -> {target}")
        if args.enable:
            _enable_plugin(name, hermes_home, args.hermes_bin)

    if not args.enable:
        print("Enable plugins with: hermes plugins enable <name>")
    print("Restart Hermes gateway/native service for changes to take effect.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
