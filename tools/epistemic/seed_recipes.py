#!/usr/bin/env python3
"""seed_recipes.py — auto-seed RECIPES.md candidate rows (H356, high automation).

Two seed sources, both cheap and high-yield:
  1. Every kosha-manifest dataset row already names a builder script → emit a recipe stub with
     the builder prefilled as the Command.
  2. Every FINDINGS row whose Evidence/Source cites a runnable `*.py` / `*.sh` / `curl …`
     → emit a stub with that command prefilled.

Emits ⚙️ candidate RECIPES rows to stdout. A human fills the Expected number (tying it back to
the FINDINGS §N) and the Env/runtime line.

Usage:
    python seed_recipes.py [--manifest <datasets.json>] [--findings <FINDINGS.md>] \
        --today DD-MM-YYYY [--repo <name>]
"""
import argparse
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

CMD = re.compile(r"`([^`]*\.(?:py|sh)[^`]*)`|`(curl [^`]+)`")
# a FINDINGS finding boundary, either layout
FINDING = re.compile(r"^(?:### §(\d+)\.|(?:🔴|🟠|🟡)\s*\*\*§(\d+)\.)", re.M)


def manifest_builders(manifest_obj):
    """Yield (dataset_id, builder) where a manifest entry names a build script."""
    out = []

    def visit(node):
        if isinstance(node, dict):
            ds = None
            for key in ("id", "slug", "name"):
                v = node.get(key)
                if isinstance(v, str) and v.strip():
                    ds = v.strip()
                    break
            builder = None
            for key in ("builder", "build", "script", "source_script", "provenance"):
                v = node.get(key)
                if isinstance(v, str) and re.search(r"\.(py|sh)\b", v):
                    builder = v.strip()
                    break
            if ds and builder:
                out.append((ds, builder))
            for v in node.values():
                visit(v)
        elif isinstance(node, list):
            for v in node:
                visit(v)

    visit(manifest_obj)
    return out


def findings_with_commands(text):
    """Yield (section_num, command) for findings that cite a runnable command."""
    bounds = list(FINDING.finditer(text))
    for i, m in enumerate(bounds):
        num = m.group(1) or m.group(2)
        start = m.start()
        end = bounds[i + 1].start() if i + 1 < len(bounds) else len(text)
        block = text[start:end]
        for cm in CMD.finditer(block):
            cmd = cm.group(1) or cm.group(2)
            yield num, cmd.strip()
            break  # one representative command per finding


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--findings")
    ap.add_argument("--today", required=True)
    ap.add_argument("--repo", default="<repo>")
    args = ap.parse_args()

    n = 0
    if args.manifest:
        with open(args.manifest, encoding="utf-8") as f:
            manifest = json.load(f)
        builders = manifest_builders(manifest)
        print(f"<!-- seed_recipes.py: {len(builders)} manifest datasets name a builder "
              f"— ⚙️ UNCONFIRMED stubs -->\n")
        for ds, builder in builders:
            n += 1
            print(f"### §AUTO-{n}. `{ds}` → reproduce")
            print(f"🟠 ⚙️ (stub from manifest `{ds}`)")
            print("Inputs: <the source files + sibling repos the builder needs>")
            print(f"Command: `{builder}`")
            print(f"Expected: <the row count / number the manifest records for `{ds}`>")
            print("Env/runtime: <python ver, offline?, ~cost>")
            print(f"> **Source:** manifest `{ds}` · {args.repo} · {args.today} "
                  f"· auto (seed_recipes.py)\n")

    if args.findings:
        with open(args.findings, encoding="utf-8") as f:
            text = f.read()
        cmds = list(findings_with_commands(text))
        print(f"<!-- seed_recipes.py: {len(cmds)} FINDINGS rows cite a runnable command -->\n")
        for num, cmd in cmds:
            n += 1
            print(f"### §AUTO-{n}. FINDINGS §{num} → reproduce")
            print(f"🟡 ⚙️ (stub from FINDINGS §{num} Evidence)")
            print("Inputs: <the inputs the finding's command needs>")
            print(f"Command: `{cmd}`")
            print(f"Expected: <the number FINDINGS §{num} reports>")
            print("Env/runtime: <where it must run>")
            print(f"> **Source:** FINDINGS §{num} · {args.repo} · {args.today} "
                  f"· auto (seed_recipes.py)\n")

    if not n:
        print("<!-- seed_recipes: pass --manifest and/or --findings -->")


if __name__ == "__main__":
    main()
