#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scheme_bridge + convert --from (KeySwap 2.1 backlog)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from scheme_bridge import (
    detect_scheme,
    hk_to_iast,
    itrans_to_iast,
    scheme_to_iast,
    velthuis_to_iast,
)


class TestHK(unittest.TestCase):
    def test_samskrta(self):
        # saMskRta → saṃskṛta
        out = hk_to_iast("saMskRta")
        self.assertIn("ṃ", out)
        self.assertIn("ṛ", out)
        self.assertTrue(out.startswith("sa"))

    def test_siva(self):
        self.assertEqual(hk_to_iast("ziva"), "śiva")

    def test_long_vowels(self):
        self.assertEqual(hk_to_iast("rAma"), "rāma")
        self.assertEqual(hk_to_iast("Iza"), "īśa")


class TestItrans(unittest.TestCase):
    def test_aa(self):
        self.assertEqual(itrans_to_iast("raama"), "rāma")

    def test_sh(self):
        self.assertEqual(itrans_to_iast("shiva"), "śiva")

    def test_retroflex(self):
        self.assertIn("ṭ", itrans_to_iast("pa.ta"))


class TestVelthuis(unittest.TestCase):
    def test_aa(self):
        self.assertEqual(velthuis_to_iast("raama"), "rāma")

    def test_dot_r(self):
        self.assertIn("ṛ", velthuis_to_iast("k.r.s.na"))


class TestDetect(unittest.TestCase):
    def test_hk(self):
        self.assertEqual(detect_scheme("saMskRta"), "hk")

    def test_iast(self):
        self.assertEqual(detect_scheme("saṃskṛta"), "iast")

    def test_velthuis(self):
        self.assertEqual(detect_scheme("k.r.s.na"), "velthuis")


class TestConvertFrom(unittest.TestCase):
    def test_hk_to_deva(self):
        from convert_bridge import convert

        deva = convert("rAma", "deva", frm="hk")
        self.assertIn("र", deva)

    def test_itrans_to_iast(self):
        from convert_bridge import convert

        self.assertEqual(convert("raama", "iast", frm="itrans"), "rāma")


if __name__ == "__main__":
    unittest.main()
