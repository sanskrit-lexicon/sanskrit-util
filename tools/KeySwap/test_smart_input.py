#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for KeySwap 2.0 smart_input + convert_bridge."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from cycle_engine import CycleEngine
from smart_input import SmartTables, long_press_menu


class TestSmart(unittest.TestCase):
    def setUp(self):
        self.smart = SmartTables.default()

    def test_aa(self):
        t, ok = self.smart.apply("rmaa")
        # ends with aa → … + ā
        self.assertTrue(ok)
        self.assertTrue(t.endswith("ā"))

    def test_sh(self):
        t, ok = self.smart.apply("aash")
        # longest: might match sh at end of aash → aaś? ends with sh
        self.assertTrue(ok)
        self.assertTrue(t.endswith("ś"))

    def test_no_match(self):
        t, ok = self.smart.apply("hello")
        self.assertFalse(ok)
        self.assertEqual(t, "hello")


class TestWriterScheme(unittest.TestCase):
    def setUp(self):
        self.w = SmartTables.writer()

    def test_macron_a(self):
        t, ok = self.w.apply("x-a")
        self.assertTrue(ok)
        self.assertTrue(t.endswith("ā"))

    def test_tilde_n(self):
        t, ok = self.w.apply("~n")
        self.assertTrue(ok)
        self.assertEqual(t, "ñ")

    def test_apostrophe_s(self):
        t, ok = self.w.apply("'s")
        self.assertTrue(ok)
        self.assertEqual(t, "ś")

    def test_h_dot(self):
        t, ok = self.w.apply("h.")
        self.assertTrue(ok)
        self.assertEqual(t, "ḥ")

    def test_profile_name(self):
        self.assertIs(type(SmartTables.for_profile("writer-scheme")), SmartTables)
        t, ok = SmartTables.for_profile("writer-scheme").apply("-u")
        self.assertTrue(ok)
        self.assertTrue(t.endswith("ū"))

    def test_config_loads(self):
        eng = CycleEngine.from_path(ROOT / "configs" / "writer-scheme.txt")
        self.assertGreater(len(eng.chains), 10)


class TestLongPress(unittest.TestCase):
    def test_menu(self):
        eng = CycleEngine.from_path(ROOT / "configs" / "iast-classic.txt")
        menu = long_press_menu(eng, "n")
        self.assertEqual(menu[0], "n")
        self.assertIn("ṇ", menu)
        self.assertIn("ṅ", menu)


class TestConvert(unittest.TestCase):
    def test_rama(self):
        sys.path.insert(0, str(ROOT.parents[1] / "py"))
        from convert_bridge import convert

        deva = convert("rāma", "deva")
        self.assertIn("र", deva)
        back = convert(deva, "iast")
        self.assertIn("rāma", back.replace(" ", ""))


class TestVedicSvaraProfile(unittest.TestCase):
    def test_loads(self):
        eng = CycleEngine.from_path(ROOT / "configs" / "vedic-svara.txt")
        self.assertGreater(len(eng.chains), 10)
        self.assertIsNotNone(eng.next_form("a"))


class TestPaliLiteProfile(unittest.TestCase):
    def test_loads(self):
        eng = CycleEngine.from_path(ROOT / "configs" / "pali-lite.txt")
        self.assertGreater(len(eng.chains), 8)
        self.assertIsNotNone(eng.next_form("a"))


if __name__ == "__main__":
    unittest.main()
