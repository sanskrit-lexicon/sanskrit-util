#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Persisted tray opt-in state for KeySwap v3 plugins (V3-2/V3-7 residual, H1639).

Owns *persistence only* of which plugin ids the user opted into from the tray
(Windows AHK menu / Mac status-bar menu) across restarts. The enable surface
itself stays exactly what ``plugins/discovery.py`` and ``typing_check.py``
already read — ``KEYSWAP_PLUGINS`` (env, comma-separated ids) / ``--plugin``
(CLI) — this module never becomes a second, parallel enable path. The tray
caller reads the persisted set at startup, reflects it as menu checkmarks,
and turns it into ``KEYSWAP_PLUGINS`` for each subprocess call that needs it
(see ``windows/KeySwap.ahk`` ``CheckClipboardHeadword`` / macOS
``AppDelegate.clipHeadwordCheck``).

State file (outside the repo tree by design — see
docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md "Future: tray opt-in" note):
``%APPDATA%\\KeySwap\\plugins.ini`` on Windows, ``~/.keyswap/plugins.ini``
elsewhere. Still off by default — an absent or empty file means no plugins,
same as today.

CLI (one round trip per tray click):

  python plugins/tray_state.py --list                    # prints comma list (may be empty)
  python plugins/tray_state.py --toggle offline_fuzzy     # flips one id, prints new comma list
"""
from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Iterable
from pathlib import Path

STATE_FILENAME = "plugins.ini"
STATE_KEY = "enabled"


def default_state_path() -> Path:
    """Per-user tray state path — never inside the git-tracked repo tree."""
    appdata = os.environ.get("APPDATA")
    base = Path(appdata) / "KeySwap" if appdata else Path.home() / ".keyswap"
    return base / STATE_FILENAME


def load_enabled(path: str | Path | None = None) -> frozenset[str]:
    """Return the persisted opt-in plugin ids (empty = none, the default)."""
    p = Path(path) if path is not None else default_state_path()
    if not p.exists():
        return frozenset()
    ids: set[str] = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("["):
            continue
        key, sep, value = line.partition("=")
        if not sep or key.strip() != STATE_KEY:
            continue
        for part in value.split(","):
            part = part.strip()
            if part:
                ids.add(part)
    return frozenset(ids)


def save_enabled(ids: Iterable[str], path: str | Path | None = None) -> None:
    """Persist ``ids`` (empty = fully off — the same state as never having toggled)."""
    p = Path(path) if path is not None else default_state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    ordered = ",".join(sorted({i.strip() for i in ids if i.strip()}))
    p.write_text(
        "# KeySwap v3 plugin tray opt-in state — off by default;\n"
        "# never wired to default Startup (see plugins/README.md)\n"
        f"{STATE_KEY}={ordered}\n",
        encoding="utf-8",
    )


def toggle(plugin_id: str, path: str | Path | None = None) -> frozenset[str]:
    """Flip ``plugin_id`` membership, persist, and return the new enabled set."""
    current = set(load_enabled(path))
    if plugin_id in current:
        current.discard(plugin_id)
    else:
        current.add(plugin_id)
    save_enabled(current, path)
    return frozenset(current)


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="print persisted enabled ids")
    group.add_argument("--toggle", metavar="PLUGIN_ID", help="flip one plugin id and persist")
    parser.add_argument(
        "--state-path", default=None, help="override state file path (tests / CI)"
    )
    args = parser.parse_args(argv)

    if args.toggle:
        ids = toggle(args.toggle, path=args.state_path)
    else:
        ids = load_enabled(path=args.state_path)
    sys.stdout.write(",".join(sorted(ids)))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(_main())
