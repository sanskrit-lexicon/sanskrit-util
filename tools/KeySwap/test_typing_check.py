#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for typing_check (offline unit tests; live API optional)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from typing_check import TypingCheck, check_word, last_token


class TestLastToken(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(last_token("rāma"), "rāma")

    def test_phrase(self):
        self.assertEqual(last_token("iti rāmaḥ"), "rāmaḥ")

    def test_multiline(self):
        self.assertEqual(last_token("foo\nkṛṣṇa."), "kṛṣṇa")


class TestCheckOffline(unittest.TestCase):
    def test_keys_only(self):
        r = check_word("rāma", verify=False)
        self.assertIsNone(r.known)
        self.assertEqual(r.slp1, "rAma")
        self.assertNotIn("✓", r.hud_line())
        self.assertIn("slp1=", r.hud_line())

    def test_empty(self):
        r = check_word("   ", verify=False)
        self.assertEqual(r.error, "empty")


class TestCheckMocked(unittest.TestCase):
    def test_known(self):
        with patch("typing_check.fetch_results", return_value=["rāma", "rāmaḥ"]):
            r = check_word("rāma", verify=True)
        self.assertTrue(r.known)
        self.assertEqual(r.n_hits, 2)
        self.assertIn("✓", r.hud_line())

    def test_unknown(self):
        with patch("typing_check.fetch_results", return_value=[]):
            r = check_word("xyzzy", verify=True, scheme="iast")
        self.assertFalse(r.known)
        self.assertIn("✗", r.hud_line())

    def test_api_error(self):
        with patch("typing_check.fetch_results", side_effect=TimeoutError("x")):
            r = check_word("rāma", verify=True)
        self.assertIsNone(r.known)
        self.assertIn("api:", r.error)


class TestHud(unittest.TestCase):
    def test_hud_truncates(self):
        t = TypingCheck(
            query="x" * 80,
            known=True,
            n_hits=1,
            top=["a"],
            slp1="x",
            normkey="x",
            scheme="iast",
            dict="mw",
        )
        self.assertLessEqual(len(t.hud_line()), 120)


if __name__ == "__main__":
    unittest.main()
