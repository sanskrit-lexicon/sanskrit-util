#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for cologne_search (dalnorm + scheme → SLP1)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from cologne_search import dalnorm_normalize, prepare, to_slp1


class TestDalnorm(unittest.TestCase):
    def test_anusvara_before_k(self):
        # aMk → aNk (ṅk)
        self.assertEqual(dalnorm_normalize("aMk"), "aNk")

    def test_anusvara_before_p(self):
        # M only expands before stops; before s it stays (Cologne rule)
        self.assertEqual(dalnorm_normalize("aMp"), "amp")
        self.assertEqual(dalnorm_normalize("saMskfta"), "saMskfta")

    def test_aH_ending(self):
        self.assertEqual(dalnorm_normalize("rAmaH"), "rAma")

    def test_ttr(self):
        self.assertEqual(dalnorm_normalize("pattra"), "patra")

    def test_ant_ending(self):
        self.assertEqual(dalnorm_normalize("gacCant"), "gacCat")

    def test_vowel_C(self):
        # aC → acC
        self.assertEqual(dalnorm_normalize("aC"), "acC")


class TestToSlp1(unittest.TestCase):
    def test_iast(self):
        slp, sch = to_slp1("rāma", "iast")
        self.assertEqual(sch, "iast")
        self.assertEqual(slp, "rAma")

    def test_hk(self):
        slp, sch = to_slp1("rAma", "hk")
        self.assertEqual(sch, "hk")
        self.assertEqual(slp, "rAma")

    def test_slp1_passthrough(self):
        slp, sch = to_slp1("rAma", "slp1")
        self.assertEqual(slp, "rAma")
        self.assertEqual(sch, "slp1")


class TestPrepare(unittest.TestCase):
    def test_urls(self):
        q = prepare("rāma", scheme="iast", dict_code="mw")
        self.assertIn("rAma", q.slp1)
        self.assertIn("getword_list", q.api_url)
        self.assertIn("dict=mw", q.api_url)
        self.assertIn("input=iast", q.api_url)
        self.assertIn("key=", q.api_url)

    def test_hk_prepare(self):
        q = prepare("ziva", scheme="hk")
        # śiva → Siva in SLP1
        self.assertIn("S", q.slp1)
        self.assertEqual(q.cologne_input, "hk")


if __name__ == "__main__":
    unittest.main()
