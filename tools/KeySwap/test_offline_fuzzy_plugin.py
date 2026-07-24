#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scaffold tests for plugins/offline_fuzzy (H1581) — no AHK coupling."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from plugins.offline_fuzzy import NEVER_AUTOLOAD, PLUGIN_ID  # noqa: E402
from plugins.offline_fuzzy.fuzzy_lookup import (  # noqa: E402
    load_manifest,
    lookup,
)


class OfflineFuzzyScaffoldTests(unittest.TestCase):
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
        self.assertFalse(r.fuzzy_ready)

    def test_lookup_seed_exact_when_present(self) -> None:
        # Seed list is small; use a key that is almost always present.
        # If the seed is missing in a sparse checkout, accept no-wordlist.
        r = lookup("rAma")
        if r.status == "no-wordlist":
            self.skipTest("local_headwords.txt not present")
        # Either exact hit or clear not-in-seed; never pretends fuzzy works.
        self.assertFalse(r.fuzzy_ready)
        self.assertIn(r.status, ("exact", "not-in-seed; fuzzy-index-not-built"))
        if r.found:
            self.assertEqual(r.match, "rAma")
            self.assertEqual(r.source, "offline_fuzzy+seed-exact")

    def test_manifest_json_parseable(self) -> None:
        p = ROOT / "plugins" / "offline_fuzzy" / "manifest.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(data["entry"], "fuzzy_lookup:lookup")


if __name__ == "__main__":
    unittest.main()
