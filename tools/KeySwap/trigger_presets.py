#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KeySwap 2.8 — named cycle-trigger presets (non-US keyboards).

Upstream Keyswap PE users often change the trigger off ``=`` when Word or a
layout maps that key elsewhere. Named presets keep AHK / Mac / PWA aligned.

Presets (id → character / notes):

  equals    =   default US; literal escape Shift+=
  bracket   ]   common non-US pick; literal Shift+]
  slash     /   alternate; literal Shift+/
  backtick  `   alternate; literal Shift+`

Config file (Windows): ``windows/trigger.ini`` (see trigger.example.ini)::

  preset=bracket

Env override: ``KEYSWAP_TRIGGER=bracket`` (wins over file when set).

This module is the **canonical table** for tests + docs; runtimes read the
same ids.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_TRIGGER_INI = ROOT / "windows" / "trigger.ini"
ENV_TRIGGER = "KEYSWAP_TRIGGER"


@dataclass(frozen=True)
class TriggerPreset:
    id: str
    char: str
    label: str
    # AHK v2 hotkey name for the cycle key (no modifiers)
    ahk_key: str
    # AHK v2 hotkey for literal escape (usually Shift+key)
    ahk_literal: str
    # macOS ANSI virtual keycode (kVK_ANSI_*)
    mac_keycode: int
    note: str = ""


# Canonical registry — keep in sync with windows/KeySwap.ahk PRESETS map.
PRESETS: dict[str, TriggerPreset] = {
    "equals": TriggerPreset(
        id="equals",
        char="=",
        label="Equals (=)",
        ahk_key="=",
        ahk_literal="+=",
        mac_keycode=0x18,  # kVK_ANSI_Equal
        note="Default US layout",
    ),
    "bracket": TriggerPreset(
        id="bracket",
        char="]",
        label="Right bracket (])",
        ahk_key="]",
        ahk_literal="+]",
        mac_keycode=0x1E,  # kVK_ANSI_RightBracket
        note="Common non-US PE workaround",
    ),
    "slash": TriggerPreset(
        id="slash",
        char="/",
        label="Slash (/)",
        ahk_key="/",
        ahk_literal="+/",
        mac_keycode=0x2C,  # kVK_ANSI_Slash
        note="Alternate when = / ] conflict",
    ),
    "backtick": TriggerPreset(
        id="backtick",
        char="`",
        label="Backtick (`)",
        ahk_key="`",
        ahk_literal="+`",
        mac_keycode=0x32,  # kVK_ANSI_Grave
        note="Alternate; rare layout collision",
    ),
}

DEFAULT_PRESET_ID = "equals"


def normalize_preset_id(raw: str | None) -> str:
    s = (raw or "").strip().lower()
    if not s:
        return DEFAULT_PRESET_ID
    # aliases
    aliases = {
        "=": "equals",
        "equal": "equals",
        "plus": "equals",
        "]": "bracket",
        "rbrack": "bracket",
        "right-bracket": "bracket",
        "/": "slash",
        "solidus": "slash",
        "`": "backtick",
        "grave": "backtick",
        "tick": "backtick",
    }
    s = aliases.get(s, s)
    if s not in PRESETS:
        raise ValueError(
            f"unknown trigger preset {raw!r}; choose one of: "
            + ", ".join(sorted(PRESETS))
        )
    return s


def get_preset(preset_id: str | None = None) -> TriggerPreset:
    return PRESETS[normalize_preset_id(preset_id)]


def parse_trigger_ini(text: str) -> str:
    """Return preset id from trigger.ini body (``preset=…``)."""
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith(";"):
            continue
        m = re.match(r"preset\s*=\s*(\S+)", s, re.I)
        if m:
            return normalize_preset_id(m.group(1))
    return DEFAULT_PRESET_ID


def resolve_preset_id(
    *,
    env: str | None = None,
    ini_path: str | Path | None = None,
) -> str:
    """Env KEYSWAP_TRIGGER wins; else trigger.ini; else equals."""
    raw_env = env if env is not None else os.environ.get(ENV_TRIGGER, "")
    if (raw_env or "").strip():
        return normalize_preset_id(raw_env)
    path = Path(ini_path) if ini_path is not None else DEFAULT_TRIGGER_INI
    if path.is_file():
        return parse_trigger_ini(path.read_text(encoding="utf-8-sig"))
    return DEFAULT_PRESET_ID


def resolve_preset(
    *,
    env: str | None = None,
    ini_path: str | Path | None = None,
) -> TriggerPreset:
    return get_preset(resolve_preset_id(env=env, ini_path=ini_path))


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    import sys

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true", help="list presets as JSON")
    ap.add_argument("--resolve", action="store_true", help="print active preset")
    ap.add_argument("--ini", type=Path, default=None)
    args = ap.parse_args(argv)
    if args.list:
        print(
            json.dumps(
                {k: {"char": v.char, "label": v.label, "mac": v.mac_keycode}
                 for k, v in PRESETS.items()},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    p = resolve_preset(ini_path=args.ini)
    print(f"{p.id}\t{p.char}\t{p.label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
