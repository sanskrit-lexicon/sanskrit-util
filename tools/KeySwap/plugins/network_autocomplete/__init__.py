# -*- coding: utf-8 -*-
"""KeySwap plugin network_autocomplete (V3-7) — opt-in only; never autoload.

Runs **after** offline fuzzy (V3-2): network is used only when the local index
is insufficient. Default Startup AHK never imports this package.
"""

from __future__ import annotations

__all__ = ["PLUGIN_ID", "NEVER_AUTOLOAD", "REQUIRES"]

PLUGIN_ID = "network_autocomplete"
NEVER_AUTOLOAD = True
# Soft dependency: enabling this plugin implies offline_fuzzy pre-pass.
REQUIRES = ("offline_fuzzy",)
