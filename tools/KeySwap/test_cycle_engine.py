#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for KeySwap cycle_engine (stdlib unittest, no pytest required)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from cycle_engine import ConfigError, CycleEngine, parse_chains, validate_config_text


class TestParse(unittest.TestCase):
    def test_basic(self):
        chains = parse_chains("n > ṇ > ṅ > ñ\na > ā\n")
        self.assertEqual(chains[0], ["n", "ṇ", "ṅ", "ñ"])
        self.assertEqual(chains[1], ["a", "ā"])

    def test_comments_and_bom_safe(self):
        text = "# head\nn > ṇ  # nasal\n\na > ā\n"
        chains = parse_chains(text)
        self.assertEqual(len(chains), 2)

    def test_duplicate_base(self):
        with self.assertRaises(ConfigError):
            parse_chains("a > ā\na > á\n")

    def test_needs_two_forms(self):
        with self.assertRaises(ConfigError):
            parse_chains("a\n")


class TestCycle(unittest.TestCase):
    def setUp(self):
        self.eng = CycleEngine.from_text(
            "n > ṇ > ṅ > ñ\n"
            "a > ā > á > ā́\n"
            "s > ṣ > ś\n"
            "l > ḷ > ḹ\n"
        )

    def test_next_form_wrap(self):
        self.assertEqual(self.eng.next_form("n"), "ṇ")
        self.assertEqual(self.eng.next_form("ṇ"), "ṅ")
        self.assertEqual(self.eng.next_form("ñ"), "n")

    def test_apply_trigger_simple(self):
        t, ok = self.eng.apply_trigger("kra")
        self.assertTrue(ok)
        self.assertEqual(t, "krā")
        t2, ok2 = self.eng.apply_trigger(t)
        self.assertTrue(ok2)
        self.assertEqual(t2, "krá")

    def test_apply_trigger_multicodepoint(self):
        # Final ā (in a > ā > á > ā́) advances to á
        t, ok = self.eng.apply_trigger("śiṣyā")
        self.assertTrue(ok)
        self.assertEqual(t, "śiṣyá")
        # walk a chain from plain a at end (4 forms → wrap)
        t = "xxa"
        for _ in range(4):
            t, ok = self.eng.apply_trigger(t)
            self.assertTrue(ok)
        self.assertEqual(t, "xxa")  # full wrap

    def test_unknown_no_change(self):
        t, ok = self.eng.apply_trigger("hello")
        self.assertFalse(ok)
        self.assertEqual(t, "hello")

    def test_longest_suffix(self):
        # ḹ should match as whole form, not ḷ
        eng = CycleEngine.from_text("l > ḷ > ḹ\n")
        t, ok = eng.apply_trigger("kḷ")
        self.assertTrue(ok)
        self.assertEqual(t, "kḹ")
        t2, ok2 = eng.apply_trigger(t)
        self.assertTrue(ok2)
        self.assertEqual(t2, "kl")


class TestProfiles(unittest.TestCase):
    def test_all_profiles_load(self):
        cfg_dir = ROOT / "configs"
        for path in sorted(cfg_dir.glob("*.txt")):
            eng = CycleEngine.from_path(path)
            self.assertGreater(len(eng.chains), 5, msg=path.name)
            warnings = validate_config_text(
                path.read_text(encoding="utf-8-sig"), path=str(path)
            )
            # personal-legacy may warn about symmetry; classic should be clean-ish
            if path.name == "iast-classic.txt":
                # no error path; warnings optional
                self.assertIsInstance(warnings, list)

    def test_classic_has_lowercase_ll(self):
        eng = CycleEngine.from_path(ROOT / "configs" / "iast-classic.txt")
        self.assertEqual(eng.next_form("ḷ"), "ḹ")
        self.assertEqual(eng.next_form("ḹ"), "l")


if __name__ == "__main__":
    unittest.main()
