#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for plugins/offline_fuzzy (V3-2 implementation) — no AHK coupling."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from plugins.discovery import parse_plugin_ids, plugin_enabled  # noqa: E402
from plugins.offline_fuzzy import NEVER_AUTOLOAD, PLUGIN_ID  # noqa: E402
from plugins.offline_fuzzy.fuzzy_lookup import (  # noqa: E402
    clear_index_cache,
    load_manifest,
    lookup,
)
from typing_check import check_word  # noqa: E402


class OfflineFuzzyImplTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_index_cache()

    def test_plugin_id_and_never_autoload(self) -> None:
        self.assertEqual(PLUGIN_ID, "offline_fuzzy")
        self.assertTrue(NEVER_AUTOLOAD)

    def test_manifest_never_autoload(self) -> None:
        m = load_manifest()
        self.assertEqual(m["id"], "offline_fuzzy")
        self.assertIs(m["never_autoload"], True)
        self.assertEqual(m["v3_item"], "V3-2")

    def test_lookup_empty(self) -> None:
        r = lookup("")
        self.assertFalse(r.found)
        self.assertEqual(r.status, "empty-query")
        self.assertTrue(r.fuzzy_ready)

    def test_lookup_seed_exact(self) -> None:
        r = lookup("rAma")
        if r.status == "no-wordlist":
            self.skipTest("local_headwords.txt not present")
        self.assertTrue(r.found)
        self.assertEqual(r.status, "exact")
        self.assertEqual(r.match, "rAma")
        self.assertTrue(r.fuzzy_ready)
        self.assertEqual(r.distance, 0)

    def test_lookup_prefix_or_edit(self) -> None:
        # Seed has rAma; probe with a truncated / near form.
        r = lookup("rAm")
        if r.status == "no-wordlist":
            self.skipTest("local_headwords.txt not present")
        self.assertTrue(r.fuzzy_ready)
        self.assertIn(r.status, ("fuzzy-unique", "fuzzy-multi", "exact", "not-found"))
        if r.status.startswith("fuzzy"):
            self.assertTrue(r.suggestions or r.match)
            # At least one suggestion should relate to rAma
            pool = list(r.suggestions) + ([r.match] if r.match else [])
            self.assertTrue(any(s.startswith("rAm") for s in pool))

    def test_lookup_tiny_custom_list(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "wl.txt"
            p.write_text("# test\nrAma\nkfzRa\nSiva\n", encoding="utf-8")
            clear_index_cache()
            exact = lookup("rAma", path=p)
            self.assertTrue(exact.found)
            self.assertEqual(exact.status, "exact")

            # single-char edit: kfzRa <- kfza (missing n) may multi/unique
            near = lookup("kfzR", path=p)  # prefix of kfzRa
            self.assertTrue(near.fuzzy_ready)
            self.assertIn(near.status, ("fuzzy-unique", "fuzzy-multi"))
            pool = list(near.suggestions) + ([near.match] if near.match else [])
            self.assertIn("kfzRa", pool)

            miss = lookup("zzzzz", path=p)
            self.assertFalse(miss.found)
            self.assertEqual(miss.status, "not-found")

    def test_discovery_env_and_cli(self) -> None:
        self.assertEqual(parse_plugin_ids(None, env=""), frozenset())
        self.assertEqual(
            parse_plugin_ids(["offline_fuzzy"], env=""),
            frozenset({"offline_fuzzy"}),
        )
        self.assertEqual(
            parse_plugin_ids(None, env="offline_fuzzy,other"),
            frozenset({"offline_fuzzy", "other"}),
        )
        self.assertTrue(plugin_enabled("offline_fuzzy", ["offline_fuzzy"]))
        self.assertFalse(plugin_enabled("offline_fuzzy", [], env=""))

    def test_typing_check_plugin_exact(self) -> None:
        r = check_word(
            "rāma",
            local_only=True,
            plugins=["offline_fuzzy"],
        )
        if r.error and "no local" in r.error:
            self.skipTest("no wordlist")
        self.assertTrue(r.known)
        self.assertEqual(r.source, "offline_fuzzy")
        self.assertEqual(r.fuzzy_status, "exact")
        self.assertIn("✓", r.hud_line())

    def test_typing_check_plugin_fuzzy_near(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "wl.txt"
            p.write_text("rAma\nkfzRa\n", encoding="utf-8")
            r = check_word(
                "rAm",
                local_only=True,
                wordlist=p,
                plugins=["offline_fuzzy"],
                scheme="slp1",
            )
            self.assertEqual(r.source, "offline_fuzzy")
            self.assertTrue(r.fuzzy_status.startswith("fuzzy") or r.known)
            self.assertTrue(r.top or r.known)
            hud = r.hud_line()
            self.assertTrue("~" in hud or "✓" in hud)

    def test_typing_check_without_plugin_stays_exact_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "wl.txt"
            p.write_text("rAma\n", encoding="utf-8")
            r = check_word(
                "rAm",
                local_only=True,
                wordlist=p,
                plugins=[],
                scheme="slp1",
            )
            self.assertEqual(r.source, "local")
            self.assertFalse(r.known)
            self.assertNotEqual(r.source, "offline_fuzzy")

    def test_default_env_does_not_enable_plugin(self) -> None:
        old = os.environ.pop("KEYSWAP_PLUGINS", None)
        try:
            r = check_word("rāma", local_only=True, plugins=None)
            if r.known:
                self.assertEqual(r.source, "local")
        finally:
            if old is not None:
                os.environ["KEYSWAP_PLUGINS"] = old

    def test_manifest_json_parseable(self) -> None:
        p = ROOT / "plugins" / "offline_fuzzy" / "manifest.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(data["entry"], "fuzzy_lookup:lookup")


if __name__ == "__main__":
    unittest.main()
