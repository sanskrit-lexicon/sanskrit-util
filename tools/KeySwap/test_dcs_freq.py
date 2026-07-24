#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for optional DCS-2026 frequency support."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from cologne_search import CologneHit, prepare  # noqa: E402
from dcs_freq import clear_cache, dcs_freq_enabled, freq_of, load_dcs_freq
from typing_check import check_word


class TestDcsFreqTable(unittest.TestCase):
    def test_shipped_table(self):
        from dcs_freq import get_dcs_freq

        tab = get_dcs_freq()
        self.assertIsNotNone(tab)
        assert tab is not None
        self.assertGreater(len(tab), 1000)
        # high-frequency core from wf1 docs
        self.assertIn("tad", tab)
        self.assertGreater(tab["tad"], 1000)

    def test_freq_of_rAma(self):
        n = freq_of("rAma", "rAma")
        self.assertIsNotNone(n)
        self.assertGreaterEqual(n or 0, 0)

    def test_enabled_env(self):
        old = os.environ.get("KEYSWAP_DCS_FREQ")
        try:
            os.environ["KEYSWAP_DCS_FREQ"] = "1"
            self.assertTrue(dcs_freq_enabled())
            os.environ["KEYSWAP_DCS_FREQ"] = "0"
            self.assertFalse(dcs_freq_enabled())
            self.assertTrue(dcs_freq_enabled(True))
        finally:
            if old is None:
                os.environ.pop("KEYSWAP_DCS_FREQ", None)
            else:
                os.environ["KEYSWAP_DCS_FREQ"] = old


class TestTypingCheckDcs(unittest.TestCase):
    def test_local_only_with_dcs_hud(self):
        r = check_word("rāma", local_only=True, verify=True, dcs_freq=True)
        self.assertTrue(r.known)
        self.assertIsNotNone(r.dcs_n)
        self.assertIn("dcs=", r.hud_line())

    def test_default_off_no_dcs_in_hud(self):
        # clear env influence
        old = os.environ.pop("KEYSWAP_DCS_FREQ", None)
        try:
            r = check_word("rāma", local_only=True, verify=True, dcs_freq=False)
            self.assertTrue(r.known)
            self.assertIsNone(r.dcs_n)
            self.assertNotIn("dcs=", r.hud_line())
        finally:
            if old is not None:
                os.environ["KEYSWAP_DCS_FREQ"] = old

    def test_prepare_freqsrc(self):
        q = prepare("rāma", freqsrc="wf1")
        self.assertIn("freqsrc=wf1", q.api_url)
        q0 = prepare("rāma", freqsrc="wf0")
        self.assertIn("freqsrc=wf0", q0.api_url)


class TestLoadCustom(unittest.TestCase):
    def test_custom_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "f.txt"
            p.write_text("# c\nrAma 42\ntad 99\n", encoding="utf-8")
            clear_cache()
            d = load_dcs_freq(p)
            self.assertEqual(d["rAma"], 42)
            self.assertEqual(d["tad"], 99)
            clear_cache()


if __name__ == "__main__":
    unittest.main()
