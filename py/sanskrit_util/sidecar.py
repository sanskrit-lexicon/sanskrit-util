# -*- coding: utf-8 -*-
"""Data-layer sidecar: the ONE provenance record written beside a derived layer.

Why this exists
---------------
A formal artifact is worth what its use is, not what its correctness is
(H6979, grill 18-10-2026, decisions:
https://github.com/gasyoun/kosha/blob/main/reports/DATA_CONSUMER_PROVENANCE_DECISIONS_18.10.26.md).
The estate's own diagnosis is D-HUB-2c "one-shot deliverables never wired to
consumers": layers get built, registered, and then nobody consumes them. The
mechanical answer is a sidecar file — ``<layer>.meta.json`` — written by the
builder itself, carrying who made the layer, on which handoff/model, and WHO
CONSUMES IT. A layer with no consumer is not an error, but it must SAY so:
``status: dormant`` plus an ``owner`` and a ``review_after`` date.

The gate (this module is the gate, not a formatter)
---------------------------------------------------
:func:`write_sidecar` REFUSES to write a payload that:

1. has no ``made_by`` (WHO made it is not optional);
2. has no consumers and is not ``dormant`` (an unused layer must be declared
   dormant, not quietly registered as an asset);
3. is ``dormant`` without ``owner`` + ``review_after`` (a dormant layer without
   a name and a date is a black hole);
4. claims ``human_gold`` without a ``roundtrip`` block (decision #9: the
   length/round-trip check is mandatory exactly for layers feeding human gold);
5. has no ``novelty`` (decision #10: "what does this add over what exists?" is
   the paragraph that stops re-derivation of a known result).

Fields
------
``layer``        layer id (the registered dataset id where one exists)
``made_by``      ``human`` | ``ai`` | ``human+ai`` | ``upstream`` | ``unknown``
``model``        exact model id used, e.g. ``claude-sonnet-5`` (null if human)
``handoff``      ``H####`` that executed the build (null when none)
``consumers``    list of ``{"kind": repo|paper|surface, "id": ..., "use": ...}``
``status``       ``active`` | ``dormant`` | ``retired``
``owner``        required iff dormant
``review_after`` ``YYYY-MM-DD``, required iff dormant
``novelty``      one paragraph: what this layer adds over what already exists
``roundtrip``    ``{"checked": bool, "rows_in": int, "rows_out": int}``
``human_gold``   bool — when true a valid ``roundtrip`` is mandatory
``built_at``     ``YYYY-MM-DD`` (optional)
``builder``      script path or upstream provenance string (optional)

Unknown extra keys are preserved verbatim, so a builder can keep its own
counts/sources block beside the contract fields.

Usage::

    from sanskrit_util import write_sidecar, sidecar_path_for

    write_sidecar(sidecar_path_for(artifact), {
        "layer": "union-headwords",
        "made_by": "ai",
        "model": "claude-sonnet-5",
        "handoff": "H6068",
        "consumers": [{"kind": "repo", "id": "kosha",
                       "use": "spellcheck dictionary source"}],
        "status": "active",
        "novelty": "adds MWderivations key2 spellings the 15-dict union misses",
    })
"""
from __future__ import annotations

import datetime
import json
import os
import re
import tempfile
from pathlib import Path

SIDECAR_SUFFIX = ".meta.json"

MADE_BY_VALUES = ("human", "ai", "human+ai", "upstream", "unknown")
STATUS_VALUES = ("active", "dormant", "retired")
CONSUMER_KINDS = ("repo", "paper", "surface")

_HANDOFF_RE = re.compile(r"^H\d{3,5}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class SidecarError(ValueError):
    """Raised when a sidecar payload fails the provenance gate."""

    def __init__(self, problems, payload=None):
        self.problems = list(problems)
        self.payload = payload
        super().__init__(
            "sidecar refused (" + str(len(self.problems)) + " problem(s)): "
            + "; ".join(self.problems)
        )


def sidecar_path_for(output, layer=None):
    """Where the sidecar for ``output`` lives.

    ``layer`` given  -> ``<dir>/<layer>.meta.json`` (one sidecar per layer).
    ``layer`` absent -> ``<output>.meta.json`` (one sidecar per artifact;
    the convention several repos already use).
    """
    out = Path(output)
    if layer:
        if not isinstance(layer, str) or not layer.strip():
            raise SidecarError(["layer must be a non-empty string"])
        if os.sep in layer or (os.altsep and os.altsep in layer):
            raise SidecarError(["layer must be a bare id, not a path: %r" % layer])
        return out.parent / (layer + SIDECAR_SUFFIX)
    return Path(str(out) + SIDECAR_SUFFIX)


def _is_blank(value):
    return value is None or (isinstance(value, str) and not value.strip())


def validate_sidecar(payload):
    """Return the list of contract problems; empty list == valid.

    Pure function, never raises on a malformed payload — the caller decides
    whether to collect (``write_sidecar`` raises once with all problems) or to
    inspect a hand-written sidecar.
    """
    problems = []
    if not isinstance(payload, dict):
        return ["payload must be a JSON object, got %s" % type(payload).__name__]

    layer = payload.get("layer")
    if _is_blank(layer) or not isinstance(layer, str):
        problems.append("missing layer (the layer id is mandatory)")

    made_by = payload.get("made_by")
    if _is_blank(made_by):
        problems.append("missing made_by (human|ai|human+ai|upstream|unknown)")
    elif made_by not in MADE_BY_VALUES:
        problems.append(
            "made_by %r is not one of %s" % (made_by, "|".join(MADE_BY_VALUES)))

    status = payload.get("status")
    if _is_blank(status):
        problems.append("missing status (active|dormant|retired)")
    elif status not in STATUS_VALUES:
        problems.append(
            "status %r is not one of %s" % (status, "|".join(STATUS_VALUES)))

    consumers = payload.get("consumers")
    if consumers is None:
        consumers = []
    if not isinstance(consumers, list):
        problems.append("consumers must be a list of {kind,id,use} objects")
        consumers = []
    else:
        for i, entry in enumerate(consumers):
            if not isinstance(entry, dict):
                problems.append(
                    "consumers[%d] must be an object {kind,id,use}, got %r"
                    % (i, entry))
                continue
            kind = entry.get("kind")
            if kind not in CONSUMER_KINDS:
                problems.append(
                    "consumers[%d].kind %r is not one of %s"
                    % (i, kind, "|".join(CONSUMER_KINDS)))
            if _is_blank(entry.get("id")):
                problems.append("consumers[%d].id is empty" % i)

    if status != "dormant" and not consumers:
        problems.append(
            "no consumers and status is not dormant — an unused layer must be "
            "declared dormant with an owner and a review_after date")

    if status == "dormant":
        if _is_blank(payload.get("owner")):
            problems.append("dormant layer requires owner")
        review_after = payload.get("review_after")
        if _is_blank(review_after):
            problems.append("dormant layer requires review_after (YYYY-MM-DD)")
        elif not _DATE_RE.match(str(review_after)):
            problems.append(
                "review_after %r is not YYYY-MM-DD" % (review_after,))
        else:
            try:
                datetime.date.fromisoformat(str(review_after))
            except ValueError:
                problems.append(
                    "review_after %r is not a real date" % (review_after,))

    if _is_blank(payload.get("novelty")):
        problems.append(
            "missing novelty — state what this layer adds over what already "
            "exists (an empty paragraph is a refusal, not a default)")

    handoff = payload.get("handoff")
    if handoff is not None:
        if not isinstance(handoff, str) or not _HANDOFF_RE.match(handoff):
            problems.append("handoff %r is not an H#### id" % (handoff,))

    model = payload.get("model")
    if model is not None and not isinstance(model, str):
        problems.append("model must be a string or null")

    roundtrip = payload.get("roundtrip")
    human_gold = bool(payload.get("human_gold"))
    if roundtrip is not None:
        if not isinstance(roundtrip, dict):
            problems.append("roundtrip must be an object {checked,rows_in,rows_out}")
        else:
            if not roundtrip.get("checked"):
                problems.append("roundtrip.checked is false — an unchecked "
                                "round-trip is not evidence")
            for key in ("rows_in", "rows_out"):
                val = roundtrip.get(key)
                if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                    problems.append(
                        "roundtrip.%s must be a non-negative integer" % key)
    if human_gold:
        if roundtrip is None:
            problems.append(
                "human_gold layer requires a roundtrip block (decision #9)")
        elif isinstance(roundtrip, dict):
            rows_in, rows_out = roundtrip.get("rows_in"), roundtrip.get("rows_out")
            if isinstance(rows_in, int) and isinstance(rows_out, int) \
                    and rows_in != rows_out:
                problems.append(
                    "human_gold roundtrip lost rows: rows_in=%d rows_out=%d"
                    % (rows_in, rows_out))

    return problems


def write_sidecar(dest, payload, *, layer=None, dry_run=False):
    """Validate ``payload`` and write it as ``dest`` (atomically).

    ``dest`` may be a directory (then the file is named after ``layer`` or
    ``payload["layer"]``), or the sidecar file path itself. Refuses — raising
    :class:`SidecarError` with every problem listed — when the payload fails
    the provenance gate. UTF-8, no BOM, LF, indent=2, deterministic key order
    is NOT imposed (builders keep their own section order).

    Returns the written :class:`pathlib.Path` (the target path under
    ``dry_run``), never a partially written file.
    """
    problems = validate_sidecar(payload)
    if problems:
        raise SidecarError(problems, payload)

    target = Path(dest)
    if target.is_dir() or str(dest).endswith(os.sep):
        # a directory: name the file after the layer id
        name = layer or payload.get("layer")
        target = target / (str(name) + SIDECAR_SUFFIX)
    # otherwise ``dest`` is the exact sidecar path (use sidecar_path_for())

    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if dry_run:
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(target.parent), prefix=".sidecar-",
                               suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        os.replace(tmp, target)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return target


def load_sidecar(path):
    """Read a sidecar file back; returns ``(payload, problems)``."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return payload, validate_sidecar(payload)
