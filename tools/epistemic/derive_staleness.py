#!/usr/bin/env python3
"""derive_staleness.py — FULLY auto-generate a STALENESS.md confidence-decay table
from a FINDINGS.md file (H356 Wave 0, the epistemic-registry automation proof-of-concept).

STALENESS is the only *fully* generated epistemic sibling registry: do NOT hand-edit its
table. It parses each FINDINGS finding's dates (the discovery date in its Source line, plus any
later inline re-verification date), diffs against a `--today` passed in on the command line
(NO Date.now()/system clock is read for the decay math, so a re-run on the same inputs + same
--today is byte-identical and diffable), and emits a sorted table:

    | FINDINGS § | Discovered | Last re-verified | Age | Flag | Re-check recipe |

Flag = 🔴 >6mo since last re-verify · 🟡 3-6mo · 🟢 fresh (<3mo).

Two FINDINGS layouts are supported (the two org sides look different):
  * SanskritLexicography side: `### §N. <title>` ATX headings.
  * Uprava (infra) side:       `🔴 **§N. <title>**` inline bold, no ATX heading.

Usage:
    python derive_staleness.py --findings <FINDINGS.md> --today DD-MM-YYYY \
        --side {sanskrit|infra} --repo-url <blob-base> --out <STALENESS.md>

The "Re-check recipe" column is filled from `--verifiability` (the H1362 verifiability.json):
each finding's class-appropriate re-check path — a RECIPES §, its own primary script (class A),
a host to re-probe (B), or why it does not rerun (C/D). Without `--verifiability` the column
falls back to the legacy `RECIPES §TBD` placeholder.
"""
import argparse
import re
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# --- date extraction -------------------------------------------------------
ISO = re.compile(r"\b(20\d{2})-(\d{2})(?:-(\d{2}))?\b")          # 2026-07-03 or 2026-07
DMY = re.compile(r"\b(\d{2})-(\d{2})-(20\d{2})\b")               # 03-07-2026


def _mk(y, m, d):
    try:
        return date(int(y), int(m), int(d or 1))
    except ValueError:
        return None


def dates_in(text):
    """All valid dates in a text block, as datetime.date, deduped, sorted ascending."""
    found = set()
    for y, m, d in ISO.findall(text):
        dt = _mk(y, m, d)
        if dt:
            found.add(dt)
    for d, m, y in DMY.findall(text):
        dt = _mk(y, m, d)
        if dt:
            found.add(dt)
    return sorted(found)


def parse_today(s):
    m = DMY.match(s.strip())
    if not m:
        raise SystemExit(f"--today must be DD-MM-YYYY, got {s!r}")
    d, mo, y = m.groups()
    return date(int(y), int(mo), int(d))


# --- finding splitting -----------------------------------------------------
ATX = re.compile(r"^### §(\d+)\.\s*(.+?)\s*$", re.M)
INLINE = re.compile(r"^(?:🔴|🟠|🟡)\s*\*\*§(\d+)\.\s*(.+?)\*\*", re.M)


def gh_slug(heading):
    """Reproduce GitHub's heading-anchor slug: lowercase, drop punctuation (§, ., /, …),
    keep unicode letters/digits, spaces → hyphens. Verified against the existing FINDINGS
    index anchors (e.g. '§1. Whitney accent-mobility…' → '1-whitney-accent-mobility…')."""
    out = []
    for ch in heading.strip().lower():
        if ch in " -":
            out.append(ch)
        elif ch.isalnum():          # unicode-aware; keeps ā, ī, ṣ …
            out.append(ch)
    return "".join(out).replace(" ", "-")


def split_findings(text):
    """Yield (num:int, title:str, body:str, has_anchor:bool). ATX headings get a real GitHub
    anchor; the inline-bold (infra) layout has no heading, so no fragment."""
    matches = list(ATX.finditer(text))
    has_anchor = True
    if not matches:
        matches = list(INLINE.finditer(text))
        has_anchor = False
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        num = int(m.group(1))
        title = m.group(2).strip()
        yield num, title, text[start:end], has_anchor


# --- flag ------------------------------------------------------------------
def flag_for(age_days):
    if age_days > 183:      # > ~6 months
        return "🔴"
    if age_days >= 91:      # 3-6 months
        return "🟡"
    return "🟢"             # fresh


def iso_to_dmy(dt):
    return dt.strftime("%d-%m-%Y")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", required=True)
    ap.add_argument("--today", required=True, help="DD-MM-YYYY (NOT read from the clock)")
    ap.add_argument("--side", choices=["sanskrit", "infra"], required=True)
    ap.add_argument("--repo-url", required=True,
                    help="blob base, e.g. https://github.com/gasyoun/Uprava/blob/main")
    ap.add_argument("--out", required=True)
    ap.add_argument("--verifiability", default=None,
                    help="optional verifiability.json (H1362) — fills the Re-check recipe column "
                         "from each finding's class/recipe instead of the RECIPES §TBD placeholder")
    args = ap.parse_args()

    verif = {}
    if args.verifiability:
        import json
        with open(args.verifiability, encoding="utf-8") as vf:
            verif = json.load(vf).get("findings", {})

    today = parse_today(args.today)
    # Preserve the real creation date across regenerations: this file is auto-generated, but its
    # `_Created:` must stay the first-ever date (the file-dates convention), not today's.
    import os
    created = today
    if os.path.exists(args.out):
        with open(args.out, encoding="utf-8") as ef:
            cm = re.search(r"_Created:\s*(\d{2})-(\d{2})-(20\d{2})", ef.read())
            if cm:
                created = date(int(cm.group(3)), int(cm.group(2)), int(cm.group(1)))

    with open(args.findings, encoding="utf-8") as f:
        text = f.read()

    rows = []
    for num, title, body, has_anchor in split_findings(text):
        ds = dates_in(body)
        if not ds:
            discovered = last = None
            age = None
        else:
            discovered = ds[0]
            last = ds[-1] if len(ds) > 1 else None
            newest = ds[-1]
            age = (today - newest).days
        anchor = f"#{gh_slug(f'§{num}. {title}')}" if has_anchor else ""
        rows.append((num, title, discovered, last, age, anchor))

    # sort most-stale first: unknown-date rows last, else by age desc
    rows.sort(key=lambda r: (r[4] is None, -(r[4] or 0)))

    side_name = ("Sanskrit-data" if args.side == "sanskrit" else "infra / process")
    findings_link = f"{args.repo_url}/FINDINGS.md"
    total = len(rows)
    red = sum(1 for r in rows if r[4] is not None and r[4] > 183)
    yellow = sum(1 for r in rows if r[4] is not None and 91 <= r[4] <= 183)
    green = sum(1 for r in rows if r[4] is not None and 0 <= r[4] < 91)
    unknown = sum(1 for r in rows if r[4] is None)

    out = []
    out.append("# STALENESS — confidence-decay table over "
               f"[`FINDINGS.md`]({findings_link})")
    out.append("")
    out.append(f"_Created: {iso_to_dmy(created)} · Last updated: {iso_to_dmy(today)}_")
    out.append("")
    out.append(f"**⚙️ FULLY AUTO-GENERATED — do not hand-edit the table below.** "
               "Regenerate with "
               "[`sanskrit-util/tools/epistemic/derive_staleness.py`]"
               "(https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/derive_staleness.py). "
               "This is the STALENESS epistemic sibling of "
               f"[`FINDINGS.md`]({findings_link}) ({side_name} side) — one of the seven "
               "registries minted under "
               "[H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/"
               "H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md). It answers "
               "the one question FINDINGS structurally cannot: *when was each fact last "
               "re-checked, and which are decaying?*")
    out.append("")
    out.append("Every FINDINGS finding measures a fact **at a moment**. A count true in June may "
               "be stale by December (`csl-orig` moved, a corpus was re-exported, a host came "
               "back). This table dates each finding's discovery, its most recent re-verification "
               "(if any), and flags the age.")
    out.append("")
    out.append("**Flag** — the FINDINGS 🔴🟠🟡 dots re-purposed onto a decay axis (§2 of the "
               "H356 handoff: *the dot always rates importance, but what it rates varies by "
               "layer*; here it rates re-check urgency, and adds 🟢 for fresh):")
    out.append("")
    out.append("- 🔴 **>6 months** since the last dated activity — re-verify before citing.")
    out.append("- 🟡 **3–6 months** — verify if the underlying source may have moved.")
    out.append("- 🟢 **fresh** (<3 months) — trust as-is.")
    out.append("")
    out.append(f"**Snapshot ({iso_to_dmy(today)}):** {total} findings — "
               f"🔴 {red} · 🟡 {yellow} · 🟢 {green}"
               + (f" · ⬜ {unknown} undated" if unknown else "") + ".")
    out.append("")
    out.append("> **Discovered** = earliest date in the finding's block · **Last re-verified** = "
               "latest date if the block carries more than one (a re-check leaves a second date) "
               "· **Age** = days from the newest dated activity to the regeneration date · "
               "**Re-check recipe** = how to re-verify this finding, by its H1362 verifiability "
               "class (a RECIPES § or its own script for class A · a host to re-probe for B · "
               "why it does not rerun for C/D).")
    out.append("")
    out.append("| FINDINGS § | Discovered | Last re-verified | Age | Flag | Re-check recipe |")
    out.append("|------------|-----------|------------------|-----|------|-----------------|")
    for num, title, discovered, last, age, anchor in rows:
        d_str = iso_to_dmy(discovered) if discovered else "—"
        l_str = iso_to_dmy(last) if last else "—"
        a_str = f"{age}d" if age is not None else "—"
        fl = flag_for(age) if age is not None else "⬜"
        link = f"{findings_link}{anchor}"
        recipe = verif.get(str(num), {}).get("cell", "RECIPES §TBD")
        out.append(f"| [§{num}]({link}) | {d_str} | {l_str} | {a_str} | {fl} | {recipe} |")
    out.append("")
    out.append("_Auto-generated by "
               "[`derive_staleness.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/derive_staleness.py); "
               "regenerate on FINDINGS change, do not edit by hand._")
    out.append("")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"wrote {args.out}: {total} rows (🔴{red}/🟡{yellow}/🟢{green}/⬜{unknown})")


if __name__ == "__main__":
    main()
