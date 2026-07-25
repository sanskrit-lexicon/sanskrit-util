#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for plugins/tray_state.py (H1639 tray opt-in persistence) — no AHK/Swift coupling."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from plugins.tray_state import load_enabled, save_enabled, toggle  # noqa: E402


class TrayStateTests(unittest.TestCase):
    def _state_path(self, td: str) -> Path:
        return Path(td) / "plugins.ini"

    def test_missing_file_means_off(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = self._state_path(td)
            self.assertEqual(load_enabled(p), frozenset())

    def test_toggle_on_then_off_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = self._state_path(td)
            self.assertEqual(load_enabled(p), frozenset())

            after_on = toggle("offline_fuzzy", p)
            self.assertEqual(after_on, frozenset({"offline_fuzzy"}))
            self.assertEqual(load_enabled(p), frozenset({"offline_fuzzy"}))

            after_on2 = toggle("network_autocomplete", p)
            self.assertEqual(
                after_on2, frozenset({"offline_fuzzy", "network_autocomplete"})
            )

            after_off = toggle("offline_fuzzy", p)
            self.assertEqual(after_off, frozenset({"network_autocomplete"}))
            self.assertEqual(load_enabled(p), frozenset({"network_autocomplete"}))

            after_off2 = toggle("network_autocomplete", p)
            self.assertEqual(after_off2, frozenset())
            self.assertEqual(load_enabled(p), frozenset())

    def test_save_enabled_empty_matches_never_toggled(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = self._state_path(td)
            save_enabled(["offline_fuzzy"], p)
            self.assertEqual(load_enabled(p), frozenset({"offline_fuzzy"}))
            save_enabled([], p)
            self.assertEqual(load_enabled(p), frozenset())

    def test_cli_list_and_toggle_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = self._state_path(td)
            script = ROOT / "plugins" / "tray_state.py"

            out = subprocess.run(
                [sys.executable, str(script), "--list", "--state-path", str(p)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
            )
            self.assertEqual(out.stdout, "")

            out = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--toggle",
                    "offline_fuzzy",
                    "--state-path",
                    str(p),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
            )
            self.assertEqual(out.stdout, "offline_fuzzy")

            out = subprocess.run(
                [sys.executable, str(script), "--list", "--state-path", str(p)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
            )
            self.assertEqual(out.stdout, "offline_fuzzy")

    def test_state_file_never_enables_by_default(self) -> None:
        # A file that exists but has no "enabled=" body still means off.
        with tempfile.TemporaryDirectory() as td:
            p = self._state_path(td)
            p.write_text("# empty tray state\n", encoding="utf-8")
            self.assertEqual(load_enabled(p), frozenset())


if __name__ == "__main__":
    unittest.main()
