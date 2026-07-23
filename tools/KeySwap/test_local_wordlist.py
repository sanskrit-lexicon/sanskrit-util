#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for local_wordlist + typing_check offline fallback."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from local_wordlist import clear_cache, load_wordlist, lookup, resolve_wordlist_path
from typing_check import check_word


class TestLoadWordlist(unittest.TestCase):
    def test_seed_file_exists(self):
        p = resolve_wordlist_path()
        self.assertIsNotNone(p)
        assert p is not None
        keys = load_wordlist(p)
        self.assertIn("rAma", keys)
        self.assertGreater(len(keys), 100)

    def test_bom_and_comments(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "w.txt"
            p.write_text("\ufeff# comment\nrAma\nkfzNa\n", encoding="utf-8")
            keys = load_wordlist(p)
            self.assertEqual(keys, frozenset({"rAma", "kfzNa"}))

    def test_lookup(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "w.txt"
            p.write_text("rAma\nSiva\n", encoding="utf-8")
            clear_cache()
            self.assertTrue(lookup("rAma", "rAma", path=p))
            self.assertFalse(lookup("xyzzy", "xyzzy", path=p))
            self.assertIsNone(lookup("rAma", "rAma", path=Path(td) / "missing.txt"))
            clear_cache()


class TestLocalOnly(unittest.TestCase):
    def test_known_local(self):
        r = check_word("rāma", local_only=True, verify=True)
        self.assertTrue(r.known)
        self.assertEqual(r.source, "local")
        self.assertIn("local", r.hud_line())
        self.assertIn("✓", r.hud_line())

    def test_unknown_local(self):
        r = check_word("xyzzyqqq", scheme="iast", local_only=True, verify=True)
        self.assertFalse(r.known)
        self.assertEqual(r.source, "local")
        self.assertIn("✗", r.hud_line())


class TestApiFallback(unittest.TestCase):
    def test_timeout_falls_back_to_local(self):
        with patch("typing_check.fetch_results", side_effect=TimeoutError("x")):
            r = check_word("rāma", verify=True, use_local=True)
        self.assertTrue(r.known)
        self.assertEqual(r.source, "local")
        self.assertIn("✓", r.hud_line())
        self.assertNotIn("timeout", r.hud_line())

    def test_timeout_no_local_flag(self):
        with patch("typing_check.fetch_results", side_effect=TimeoutError("x")):
            r = check_word("rāma", verify=True, use_local=False)
        self.assertIsNone(r.known)
        self.assertIn("timeout", r.error)

    def test_api_success_still_api(self):
        with patch("typing_check.fetch_results", return_value=["rāma"]):
            r = check_word("rāma", verify=True)
        self.assertTrue(r.known)
        self.assertEqual(r.source, "api")


if __name__ == "__main__":
    unittest.main()
