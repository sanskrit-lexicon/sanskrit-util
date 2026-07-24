#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for KeySwap 2.8 trigger presets (stdlib only)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from trigger_presets import (  # noqa: E402
    DEFAULT_PRESET_ID,
    PRESETS,
    get_preset,
    normalize_preset_id,
    parse_trigger_ini,
    resolve_preset_id,
)


class TriggerPresetTests(unittest.TestCase):
    def test_known_ids(self) -> None:
        self.assertEqual(set(PRESETS), {"equals", "bracket", "slash", "backtick"})
        self.assertEqual(get_preset("equals").char, "=")
        self.assertEqual(get_preset("bracket").char, "]")
        self.assertEqual(get_preset("slash").char, "/")
        self.assertEqual(get_preset("backtick").char, "`")

    def test_aliases(self) -> None:
        self.assertEqual(normalize_preset_id("]"), "bracket")
        self.assertEqual(normalize_preset_id("="), "equals")
        self.assertEqual(normalize_preset_id("grave"), "backtick")

    def test_unknown_raises(self) -> None:
        with self.assertRaises(ValueError):
            normalize_preset_id("xyzzy")

    def test_parse_ini(self) -> None:
        self.assertEqual(parse_trigger_ini("preset=bracket\n"), "bracket")
        self.assertEqual(parse_trigger_ini("# comment\npreset = slash\n"), "slash")
        self.assertEqual(parse_trigger_ini(""), DEFAULT_PRESET_ID)

    def test_env_wins_over_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "trigger.ini"
            p.write_text("preset=bracket\n", encoding="utf-8")
            self.assertEqual(
                resolve_preset_id(env="slash", ini_path=p),
                "slash",
            )
            self.assertEqual(
                resolve_preset_id(env="", ini_path=p),
                "bracket",
            )

    def test_ahk_literal_is_shift_of_key(self) -> None:
        for p in PRESETS.values():
            self.assertTrue(
                p.ahk_literal.startswith("+") or p.ahk_literal == "+=",
                msg=p.id,
            )

    def test_example_ini_exists(self) -> None:
        ex = ROOT / "windows" / "trigger.example.ini"
        self.assertTrue(ex.is_file())
        text = ex.read_text(encoding="utf-8")
        self.assertIn("preset=", text)

    def test_ahk_mentions_presets(self) -> None:
        ahk = (ROOT / "windows" / "KeySwap.ahk").read_text(encoding="utf-8")
        for pid in PRESETS:
            self.assertIn(pid, ahk, msg=f"AHK missing preset {pid}")
        self.assertIn("RegisterTriggerHotkeys", ahk)
        self.assertIn("2.8", ahk)


if __name__ == "__main__":
    unittest.main()
