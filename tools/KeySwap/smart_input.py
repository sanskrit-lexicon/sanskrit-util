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

# Sanskrit Writer–style: “draw” diacritic top→bottom then letter
# (Auroville SRI scheme; also used by Bhasha “IAST Simplified”).
_WRITER_SCHEME: list[tuple[str, str]] = [
    # macron / long vowels: -a → ā
    ("-a", "ā"),
    ("-i", "ī"),
    ("-u", "ū"),
    ("-A", "Ā"),
    ("-I", "Ī"),
    ("-U", "Ū"),
    # tilde: ~n → ñ, ~m → ṃ (common SW-adjacent)
    ("~n", "ñ"),
    ("~N", "Ñ"),
    ("~m", "ṃ"),
    ("~M", "Ṃ"),
    # acute / apostrophe: 's → ś
    ("'s", "ś"),
    ("'S", "Ś"),
    # underdot after letter: h. → ḥ (SW “h.”)
    ("h.", "ḥ"),
    ("H.", "Ḥ"),
    ("r.", "ṛ"),
    ("R.", "Ṛ"),
    ("l.", "ḷ"),
    ("L.", "Ḷ"),
    ("m.", "ṃ"),
    ("M.", "Ṃ"),
    ("n.", "ṇ"),
    ("N.", "Ṇ"),
    ("t.", "ṭ"),
    ("T.", "Ṭ"),
    ("d.", "ḍ"),
    ("D.", "Ḍ"),
    ("s.", "ṣ"),
    ("S.", "Ṣ"),
    # underdot before letter (alternate order)
    (".h", "ḥ"),
    (".H", "Ḥ"),
    (".r", "ṛ"),
    (".R", "Ṛ"),
    (".l", "ḷ"),
    (".L", "Ḷ"),
    (".m", "ṃ"),
    (".M", "Ṃ"),
    (".n", "ṇ"),
    (".N", "Ṇ"),
    (".t", "ṭ"),
    (".T", "Ṭ"),
    (".d", "ḍ"),
    (".D", "Ḍ"),
    (".s", "ṣ"),
    (".S", "Ṣ"),
    # keep classic doubles too
    ("aa", "ā"),
    ("ii", "ī"),
    ("uu", "ū"),
    ("rr", "ṛ"),
    ("ll", "ḷ"),
    ("sh", "ś"),
    ("ss", "ṣ"),
    ("ng", "ṅ"),
    ("ny", "ñ"),
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

    @classmethod
    def writer(cls) -> "SmartTables":
        """Sanskrit Writer–style top-to-bottom digraphs (+ classic doubles)."""
        # de-dupe while preserving first occurrence
        seen: set[str] = set()
        raw: list[tuple[str, str]] = []
        for src, dst in _WRITER_SCHEME + _SMART_DEFAULT:
            if src in seen:
                continue
            seen.add(src)
            raw.append((src, dst))
        pairs = tuple(sorted(raw, key=lambda kv: (-len(kv[0]), kv[0])))
        return cls(pairs=pairs)

    @classmethod
    def for_profile(cls, name: str) -> "SmartTables":
        n = (name or "").lower().replace("_", "-")
        if "writer" in n:
            return cls.writer()
        return cls.default()

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
