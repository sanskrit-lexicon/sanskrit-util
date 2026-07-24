#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Opt-in plugin id parsing for KeySwap (v3).

Never loads plugin *code* — only parses which ids the user requested via CLI
or ``KEYSWAP_PLUGINS``. Core modules call this, then import plugins lazily.
"""
from __future__ import annotations

import os
from collections.abc import Iterable

ENV_PLUGINS = "KEYSWAP_PLUGINS"


def parse_plugin_ids(
    cli: Iterable[str] | None = None,
    *,
    env: str | None = None,
) -> frozenset[str]:
    """Return requested plugin ids (empty = none; default Startup loads zero)."""
    ids: set[str] = set()
    if cli is not None:
        for item in cli:
            for part in str(item).split(","):
                p = part.strip()
                if p:
                    ids.add(p)
    raw = env if env is not None else os.environ.get(ENV_PLUGINS, "")
    for part in (raw or "").split(","):
        p = part.strip()
        if p:
            ids.add(p)
    return frozenset(ids)


def plugin_enabled(
    plugin_id: str,
    cli: Iterable[str] | None = None,
    *,
    env: str | None = None,
) -> bool:
    """True only when the user explicitly opted into ``plugin_id``."""
    return plugin_id in parse_plugin_ids(cli, env=env)
