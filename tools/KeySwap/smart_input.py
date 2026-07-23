#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KeySwap 2.0 smart input — double-letter vowels and long-press menus.

Complements cycle_engine (trigger cycles). Used by CLI tests, PWA data export,
and as the reference for AHK / Swift ports.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from cycle_engine import CycleEngine, _nfc

# Double ASCII → IAST (classical). Order: longer keys first when matching suffixes.
_SMART_DEFAULT: list[tuple[str, str]] = [
    ("aa", "ā"),
    ("ii", "ī"),
    ("uu", "ū"),
    ("rr", "ṛ"),
    ("ll", "ḷ"),
    ("mm", "ṃ"),
    ("hh", "ḥ"),
    ("RR", "Ṛ"),
    ("LL", "Ḷ"),
    ("MM", "Ṃ"),
    ("HH", "Ḥ"),
    ("AA", "Ā"),
    ("II", "Ī"),
    ("UU", "Ū"),
    # Common digraph-ish shortcuts (not true HK, but high value)
    ("sh", "ś"),
    ("Sh", "Ś"),
    ("SH", "Ś"),
    ("ss", "ṣ"),
    ("Ss", "Ṣ"),
    ("SS", "Ṣ"),
    ("ng", "ṅ"),
    ("Ng", "Ṅ"),
    ("NG", "Ṅ"),
    ("ny", "ñ"),
    ("Ny", "Ñ"),
    ("NY", "Ñ"),
    ("nn", "ṇ"),
    ("Nn", "Ṇ"),
    ("NN", "Ṇ"),
    ("tt", "ṭ"),
    ("Tt", "Ṭ"),
    ("TT", "Ṭ"),
    ("dd", "ḍ"),
    ("Dd", "Ḍ"),
    ("DD", "Ḍ"),
]


@dataclass(frozen=True)
class SmartTables:
    """Suffix replacements for smart mode (longest match wins)."""

    pairs: tuple[tuple[str, str], ...]

    @classmethod
    def default(cls) -> "SmartTables":
        # longest keys first
        pairs = tuple(sorted(_SMART_DEFAULT, key=lambda kv: (-len(kv[0]), kv[0])))
        return cls(pairs=pairs)

    def apply(self, text_before_caret: str) -> tuple[str, bool]:
        t = _nfc(text_before_caret)
        for src, dst in self.pairs:
            if t.endswith(src):
                return t[: -len(src)] + _nfc(dst), True
        return t, False


def long_press_menu(engine: CycleEngine, base: str) -> list[str]:
    """Forms to show on long-press for a base key (includes base first)."""
    base = _nfc(base)
    for chain in engine.chains:
        if chain[0] == base:
            return list(chain)
    # case fold: if user long-presses shifted key
    return [base]


def export_long_press_json(engine: CycleEngine) -> dict[str, list[str]]:
    """Map base letter → forms (for PWA / iOS)."""
    out: dict[str, list[str]] = {}
    for chain in engine.chains:
        out[chain[0]] = list(chain)
    return out
