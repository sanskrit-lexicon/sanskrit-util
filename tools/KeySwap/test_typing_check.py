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

from cologne_search import format_api_error
from typing_check import TypingCheck, check_word, last_token


class TestGlossUrl(unittest.TestCase):
    def test_local_known_has_gloss(self):
        r = check_word("rāma", local_only=True, verify=True)
        self.assertTrue(r.known)
        self.assertIn("getword.php", r.gloss_url)
        self.assertIn("Ctrl+Alt+G", r.hud_line())


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
        # Pin pure API path (local seed would otherwise recover offline)
        with patch("typing_check.fetch_results", side_effect=TimeoutError("x")):
            r = check_word("rāma", verify=True, use_local=False)
        self.assertIsNone(r.known)
        self.assertIn("timeout", r.error)

    def test_http_429_hud(self):
        import urllib.error

        err = urllib.error.HTTPError(
            url="http://example", code=429, msg="Too Many Requests", hdrs=None, fp=None
        )
        with patch("typing_check.fetch_results", side_effect=err):
            r = check_word("rāma", verify=True, use_local=False)
        self.assertIsNone(r.known)
        self.assertTrue(r.error.startswith("rate-limited"))
        hud = r.hud_line()
        self.assertIn("rate-limited", hud)
        self.assertIn("Ctrl+Alt+C", hud)
        self.assertNotIn("HTTPError", hud)

    def test_http_429_recovers_via_local(self):
        import urllib.error

        err = urllib.error.HTTPError(
            url="http://example", code=429, msg="Too Many Requests", hdrs=None, fp=None
        )
        with patch("typing_check.fetch_results", side_effect=err):
            r = check_word("rāma", verify=True, use_local=True)
        self.assertTrue(r.known)
        self.assertEqual(r.source, "local")
        self.assertIn("✓", r.hud_line())


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


class TestFormatApiError(unittest.TestCase):
    def test_429(self):
        import urllib.error

        e = urllib.error.HTTPError("http://x", 429, "Too Many", None, None)
        msg = format_api_error(e)
        self.assertIn("rate-limited", msg)
        self.assertIn("Ctrl+Alt+C", msg)

    def test_500(self):
        import urllib.error

        e = urllib.error.HTTPError("http://x", 503, "Unavailable", None, None)
        self.assertEqual(format_api_error(e), "api server 503")


if __name__ == "__main__":
    unittest.main()
