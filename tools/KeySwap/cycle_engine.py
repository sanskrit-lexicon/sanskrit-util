#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KeySwap cycle engine — shared semantics for configs, AHK parity tests, docs.

Behaviour (matches the classic Keyswap model):
  - Each non-comment line is a chain: ``base > form1 > form2 > …``
  - Chains are independent; base letters must be unique across the file
  - On trigger, the longest suffix of the text that is a known form advances
    to the next form in its chain (wrapping)
  - Forms may be multi-codepoint (e.g. ā́ = ā + combining acute)

Not part of the sanskrit-util library API — tools/ only.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

__all__ = [
    "CycleEngine",
    "ConfigError",
    "load_config",
    "validate_config_text",
    "parse_chains",
    "nfc",
]

# KeySwap toolkit version (shells / docs should match tools/KeySwap/VERSION)
KEYSWAP_VERSION = "2.4.0"


class ConfigError(ValueError):
    """Invalid KeySwap config."""


_COMMENT = re.compile(r"^\s*#")
_BLANK = re.compile(r"^\s*$")


def nfc(s: str) -> str:
    """NFC-normalize a string (public; used by smart_input / convert helpers)."""
    return unicodedata.normalize("NFC", s)


# Back-compat alias
_nfc = nfc


def parse_chains(text: str, *, path: str | None = None) -> list[list[str]]:
    """Parse config text into chains of NFC forms.

    Raises ConfigError on empty chains, blank forms, or duplicate bases.
    """
    chains: list[list[str]] = []
    seen_bases: dict[str, int] = {}
    where = path or "<config>"

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or _COMMENT.match(line) or _BLANK.match(line):
            continue
        # Allow inline comments after the chain
        if " #" in line:
            line = line.split(" #", 1)[0].rstrip()
        parts = [p.strip() for p in line.split(">")]
        if any(not p for p in parts):
            raise ConfigError(f"{where}:{lineno}: empty form in chain: {raw!r}")
        forms = [_nfc(p) for p in parts]
        if len(forms) < 2:
            raise ConfigError(
                f"{where}:{lineno}: chain needs base + at least one form: {raw!r}"
            )
        base = forms[0]
        if base in seen_bases:
            raise ConfigError(
                f"{where}:{lineno}: duplicate base {base!r} "
                f"(first at line {seen_bases[base]})"
            )
        seen_bases[base] = lineno
        # Forms after base must be unique within the chain
        rest = forms[1:]
        if len(set(rest)) != len(rest):
            raise ConfigError(f"{where}:{lineno}: duplicate form inside chain: {raw!r}")
        chains.append(forms)
    if not chains:
        raise ConfigError(f"{where}: no chains found")
    return chains


def validate_config_text(text: str, *, path: str | None = None) -> list[str]:
    """Return human-readable warnings; raise ConfigError on hard failures."""
    chains = parse_chains(text, path=path)
    warnings: list[str] = []
    form_owner: dict[str, str] = {}
    for chain in chains:
        base = chain[0]
        for form in chain:
            if form in form_owner and form_owner[form] != base:
                warnings.append(
                    f"form {form!r} appears in chains {form_owner[form]!r} and {base!r} "
                    f"(longest-match still works; ambiguous reverse maps)"
                )
            else:
                form_owner[form] = base
        # Lower/upper symmetry soft check for single Latin letters
        if len(base) == 1 and base.isalpha() and base.islower():
            upper = base.upper()
            upper_bases = {c[0] for c in chains}
            if upper not in upper_bases and upper != base:
                warnings.append(f"lowercase base {base!r} has no uppercase twin {upper!r}")
    return warnings


def load_config(path: str | Path) -> "CycleEngine":
    p = Path(path)
    text = p.read_text(encoding="utf-8-sig")
    return CycleEngine.from_text(text, path=str(p))


@dataclass(frozen=True)
class _Hit:
    start: int
    end: int
    chain_index: int
    form_index: int


class CycleEngine:
    """Apply trigger cycles to plain text (caret at end of ``prefix``)."""

    def __init__(self, chains: list[list[str]]):
        if not chains:
            raise ConfigError("empty chains")
        self.chains: list[list[str]] = [
            [_nfc(f) for f in chain] for chain in chains
        ]
        # form -> list of (chain_index, form_index); prefer longer forms when matching
        self._by_form: dict[str, list[tuple[int, int]]] = {}
        for ci, chain in enumerate(self.chains):
            for fi, form in enumerate(chain):
                self._by_form.setdefault(form, []).append((ci, fi))
        self._max_form_len = max(len(f) for chain in self.chains for f in chain)

    @classmethod
    def from_text(cls, text: str, *, path: str | None = None) -> "CycleEngine":
        return cls(parse_chains(text, path=path))

    @classmethod
    def from_path(cls, path: str | Path) -> "CycleEngine":
        return load_config(path)

    def next_form(self, current: str) -> str | None:
        """Next form in the chain for ``current``, or None if unknown."""
        cur = _nfc(current)
        hits = self._by_form.get(cur)
        if not hits:
            return None
        ci, fi = hits[0]
        chain = self.chains[ci]
        return chain[(fi + 1) % len(chain)]

    def _find_suffix_hit(self, text: str) -> _Hit | None:
        """Longest known form that is a suffix of text (by Unicode code points)."""
        if not text:
            return None
        t = _nfc(text)
        cps = list(t)
        n = len(cps)
        for length in range(min(n, self._max_form_len), 0, -1):
            suffix = "".join(cps[-length:])
            hits = self._by_form.get(suffix)
            if hits:
                ci, fi = hits[0]
                start_cp = n - length
                start = len("".join(cps[:start_cp]))
                return _Hit(start=start, end=len(t), chain_index=ci, form_index=fi)
        return None

    def apply_trigger(self, text_before_caret: str) -> tuple[str, bool]:
        """Replace the longest known suffix with the next form.

        Returns (new_text_before_caret, changed).
        """
        t = _nfc(text_before_caret)
        hit = self._find_suffix_hit(t)
        if hit is None:
            return t, False
        chain = self.chains[hit.chain_index]
        nxt = chain[(hit.form_index + 1) % len(chain)]
        new_text = t[: hit.start] + nxt
        return new_text, new_text != t

    def cycle_char(self, ch: str) -> str:
        """Convenience: cycle a single form; return unchanged if unknown."""
        nxt = self.next_form(ch)
        return nxt if nxt is not None else _nfc(ch)


def iter_config_paths(configs_dir: str | Path) -> Iterable[Path]:
    d = Path(configs_dir)
    yield from sorted(d.glob("*.txt"))
