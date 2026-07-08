#!/usr/bin/env python3
"""seed_gaps.py — auto-seed GAPS.md candidate rows (H356, high automation).

Set-difference: which derived datasets exist in the manifest / FEATURES_INDEX but have NO
FINDINGS row measuring them? Each such dataset is a candidate GAP ("we have this data but
have not characterised it"). Emits ⚙️ candidate GAPS rows to stdout.

Matching is deliberately loose — a dataset is "covered" if its id, or any ≥4-char token of
its id, appears anywhere in FINDINGS.md (case-insensitive). This over-counts coverage
(favours false "covered"), so a surfaced gap is a high-confidence candidate.

Usage:
    python seed_gaps.py --manifest <datasets.json> --findings <FINDINGS.md> \
        --today DD-MM-YYYY [--repo <name>]

The manifest is expected to be the kosha data-hub manifest (a JSON object/array whose
dataset entries carry an "id"/"name"/"slug" field); --findings is a FINDINGS.md file.
"""
import argparse
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def dataset_ids(manifest_obj):
    """Best-effort pull of dataset identifiers from a manifest of unknown exact shape."""
    ids = []

    def visit(node):
        if isinstance(node, dict):
            for key in ("id", "slug", "name", "dataset"):
                v = node.get(key)
                if isinstance(v, str) and v.strip():
                    ids.append(v.strip())
                    break
            for v in node.values():
                visit(v)
        elif isinstance(node, list):
            for v in node:
                visit(v)

    visit(manifest_obj)
    # de-dupe, keep order
    seen, out = set(), []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def covered(dataset_id, findings_lower):
    if dataset_id.lower() in findings_lower:
        return True
    toks = [t for t in re.split(r"[^a-z0-9]+", dataset_id.lower()) if len(t) >= 4]
    # require ALL significant tokens present to call it covered (conservative)
    return bool(toks) and all(t in findings_lower for t in toks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--findings", required=True)
    ap.add_argument("--today", required=True)
    ap.add_argument("--repo", default="kosha")
    args = ap.parse_args()

    with open(args.manifest, encoding="utf-8") as f:
        manifest = json.load(f)
    with open(args.findings, encoding="utf-8") as f:
        findings_lower = f.read().lower()

    ids = dataset_ids(manifest)
    gaps = [i for i in ids if not covered(i, findings_lower)]

    print(f"<!-- seed_gaps.py: {len(ids)} datasets in manifest, {len(gaps)} with no FINDINGS row "
          f"— ⚙️ UNCONFIRMED candidates -->\n")
    if not gaps:
        print("<!-- every manifest dataset has at least a loose FINDINGS mention -->")
        return
    for i, ds in enumerate(gaps, 1):
        print(f"### §AUTO-{i}. `{ds}` is unmeasured")
        print(f"🟡 ⚙️ **We have the `{ds}` dataset but NO FINDINGS row characterising it.**")
        print("Why it matters: <what a measurement of it would unblock>")
        print("Blocker: <data access | no tool | needs a schema-aware parse>")
        print(f"How to close: parse `{ds}`, measure the obvious statistic, append a FINDINGS row.")
        print(f"> **Source:** manifest `{ds}` · {args.repo} · {args.today} · auto (seed_gaps.py)\n")


if __name__ == "__main__":
    main()
