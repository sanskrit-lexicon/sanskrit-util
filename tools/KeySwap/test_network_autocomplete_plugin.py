#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for plugins/network_autocomplete (V3-7) — mocked network, no live API."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from plugins.discovery import plugin_enabled  # noqa: E402
from plugins.network_autocomplete import (  # noqa: E402
    NEVER_AUTOLOAD,
    PLUGIN_ID,
    REQUIRES,
)
from plugins.network_autocomplete.autocomplete import (  # noqa: E402
    load_manifest,
    offline_is_confident,
    suggest,
    suggest_from_network,
)
from plugins.offline_fuzzy.fuzzy_lookup import clear_index_cache  # noqa: E402
from typing_check import check_word  # noqa: E402


class NetworkAutocompleteUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        clear_index_cache()

    def test_plugin_id_and_never_autoload(self) -> None:
        self.assertEqual(PLUGIN_ID, "network_autocomplete")
        self.assertTrue(NEVER_AUTOLOAD)
        self.assertIn("offline_fuzzy", REQUIRES)

    def test_manifest_never_autoload(self) -> None:
        m = load_manifest()
        self.assertEqual(m["id"], "network_autocomplete")
        self.assertIs(m["never_autoload"], True)
        self.assertEqual(m["v3_item"], "V3-7")
        self.assertIn("offline_fuzzy", m.get("requires") or [])

    def test_offline_confident_helper(self) -> None:
        self.assertTrue(offline_is_confident("exact"))
        self.assertTrue(offline_is_confident("fuzzy-unique"))
        self.assertFalse(offline_is_confident("fuzzy-multi"))
        self.assertFalse(offline_is_confident("not-found"))

    def test_suggest_prefers_offline_exact_no_network(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "wl.txt"
            p.write_text("rAma\nkfzRa\n", encoding="utf-8")
            clear_index_cache()
            called = {"n": 0}

            def boom(*_a, **_k):
                called["n"] += 1
                raise AssertionError("network must not run for exact offline")

            r = suggest("rAma", scheme="slp1", wordlist=p, fetch=boom)
            self.assertEqual(called["n"], 0)
            self.assertTrue(r.found)
            self.assertEqual(r.source, "offline_fuzzy")
            self.assertEqual(r.status, "exact")
            self.assertFalse(r.network_used)

    def test_suggest_fuzzy_unique_skips_network(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "wl.txt"
            p.write_text("rAma\n", encoding="utf-8")
            clear_index_cache()
            called = {"n": 0}

            def boom(*_a, **_k):
                called["n"] += 1
                return ["should-not-appear"]

            r = suggest("rAm", scheme="slp1", wordlist=p, fetch=boom)
            self.assertEqual(called["n"], 0)
            self.assertFalse(r.network_used)
            self.assertEqual(r.source, "offline_fuzzy")
            self.assertIn(r.status, ("fuzzy-unique", "fuzzy-multi", "exact"))

    def test_suggest_not_found_uses_network(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "wl.txt"
            p.write_text("rAma\n", encoding="utf-8")
            clear_index_cache()

            def fake_fetch(_q, timeout=5.0):  # noqa: ARG001
                return ["zyxxy", "zyxxyḥ"]

            r = suggest(
                "zyxxy",
                scheme="slp1",
                wordlist=p,
                fetch=fake_fetch,
            )
            self.assertTrue(r.network_used)
            self.assertEqual(r.source, "network_autocomplete")
            self.assertTrue(r.found)
            self.assertEqual(r.status, "network-multi")
            self.assertIn("zyxxy", r.suggestions)

    def test_suggest_network_error_hud(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "wl.txt"
            p.write_text("rAma\n", encoding="utf-8")
            clear_index_cache()

            def fail(_q, timeout=5.0):  # noqa: ARG001
                raise TimeoutError("x")

            r = suggest("zzzzz", scheme="slp1", wordlist=p, fetch=fail)
            self.assertTrue(r.network_used)
            self.assertEqual(r.status, "network-error")
            self.assertIn("timeout", r.error)

    def test_force_network_skips_offline(self) -> None:
        def fake_fetch(_q, timeout=5.0):  # noqa: ARG001
            return ["only-net"]

        r = suggest(
            "rAma",
            scheme="slp1",
            force_network=True,
            fetch=fake_fetch,
        )
        self.assertTrue(r.network_used)
        self.assertEqual(r.source, "network_autocomplete")
        self.assertEqual(r.suggestions, ("only-net",))

    def test_suggest_from_network_empty(self) -> None:
        r = suggest_from_network("")
        self.assertEqual(r.status, "empty-query")

    def test_discovery_disabled_by_default(self) -> None:
        old = os.environ.pop("KEYSWAP_PLUGINS", None)
        try:
            self.assertFalse(plugin_enabled("network_autocomplete", [], env=""))
            self.assertTrue(
                plugin_enabled("network_autocomplete", ["network_autocomplete"])
            )
        finally:
            if old is not None:
                os.environ["KEYSWAP_PLUGINS"] = old

    def test_typing_check_offline_first_no_network_call(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "wl.txt"
            p.write_text("rAma\n", encoding="utf-8")
            clear_index_cache()
            with patch(
                "plugins.network_autocomplete.autocomplete.fetch_results"
            ) as fr:
                r = check_word(
                    "rAma",
                    scheme="slp1",
                    wordlist=p,
                    plugins=["network_autocomplete"],
                )
                fr.assert_not_called()
            self.assertEqual(r.source, "offline_fuzzy")
            self.assertTrue(r.known)
            self.assertFalse(r.network_used)

    def test_typing_check_escalates_to_network(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "wl.txt"
            p.write_text("rAma\n", encoding="utf-8")
            clear_index_cache()
            with patch(
                "plugins.network_autocomplete.autocomplete.fetch_results",
                return_value=["ghost"],
            ) as fr:
                r = check_word(
                    "ghost",
                    scheme="slp1",
                    wordlist=p,
                    plugins=["network_autocomplete"],
                )
                fr.assert_called_once()
            self.assertEqual(r.source, "network_autocomplete")
            self.assertTrue(r.network_used)
            self.assertTrue(r.known)
            self.assertIn("net", r.hud_line())

    def test_local_only_does_not_network_even_with_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "wl.txt"
            p.write_text("rAma\n", encoding="utf-8")
            clear_index_cache()
            with patch(
                "plugins.network_autocomplete.autocomplete.fetch_results"
            ) as fr:
                r = check_word(
                    "ghost",
                    scheme="slp1",
                    wordlist=p,
                    local_only=True,
                    plugins=["network_autocomplete"],
                )
                fr.assert_not_called()
            # offline path (fuzzy implied); ghost not in list
            self.assertIn(r.source, ("offline_fuzzy", "local", ""))
            self.assertFalse(r.network_used)

    def test_without_plugin_stays_api_first(self) -> None:
        with patch("typing_check.fetch_results", return_value=["rāma"]) as fr:
            r = check_word("rāma", plugins=[])
            fr.assert_called_once()
        self.assertEqual(r.source, "api")

    def test_manifest_json_parseable(self) -> None:
        p = ROOT / "plugins" / "network_autocomplete" / "manifest.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(data["entry"], "autocomplete:suggest")


if __name__ == "__main__":
    unittest.main()
