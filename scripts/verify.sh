#!/usr/bin/env bash
# H3325 VCR primitive pilot gate — the ONLY component allowed to set a feature to passing.
#
# Usage:
#   scripts/verify.sh <feature-id> <planned|active|verified|passing>   # gated transition
#   scripts/verify.sh --check                                          # full checks + audit-trail integrity
#
# Rules enforced:
#   1. State machine: planned -> active -> verified -> passing (no skips, no backwards).
#   2. 'verified'/'passing' transitions run the feature's acceptance_cmd / the FULL repo
#      checks respectively; on failure the flip is REFUSED and a refusal line is audited.
#   3. Every transition appends an audit line to scripts/verify_audit.log.
#   4. Anti-bypass: --check re-derives 'passing' from the audit trail; a feature whose JSON
#      state says passing without a matching audit line is TAMPERED -> exit 1. Editing
#      feature_list.json directly can therefore never self-certify.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FEATURES="$ROOT/feature_list.json"
AUDIT="$ROOT/scripts/verify_audit.log"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
SHA="$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo nosha)"

gate_py() { python3 - "$FEATURES" "$AUDIT" "$TS" "$SHA" "$@" <<'EOF'
import json, subprocess, sys

features_path, audit_path, ts, sha = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
mode = sys.argv[5]
ORDER = ["planned", "active", "verified", "passing"]

def audit(feature, frm, to, status, note=""):
    with open(audit_path, "a", encoding="utf-8") as f:
        f.write(f"{ts}\t{sha}\t{feature}\t{frm}->{to}\t{status}\t{note}\n")

def run(cmd):
    return subprocess.run(["bash", "-c", cmd]).returncode == 0

data = json.load(open(features_path, encoding="utf-8"))
feats = {f["id"]: f for f in data["features"]}
# Audit trail is the SOLE authority for state: replay OK/PASS lines; the last
# transition per feature is its derived state. JSON must match exactly, so a
# hand-edit of feature_list.json (any direction, any feature) is TAMPERED.
derived = {fid: "planned" for fid in feats}
try:
    for line in open(audit_path, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 5 and p[4] in ("OK", "PASS") and "->" in p[3]:
            derived[p[2]] = p[3].split("->")[1]
except FileNotFoundError:
    pass

if mode == "--check":
    rc = 0
    tampered = [fid for fid, f in feats.items() if f["state"] != derived[fid]]
    if tampered:
        print(f"REFUSED: TAMPERED state diverges from audit trail: {tampered}")
        rc = 1
    for cmd in ["cd js && npm test", "python3 -m pytest py/tests -q"]:
        if not run(cmd):
            print(f"REFUSED: full checks failed: {cmd}")
            rc = 1
    act = [f for f in feats.values() if f["state"] in ("active", "verified", "passing")]
    ver = [f for f in feats.values() if f["state"] in ("verified", "passing")]
    pas = [f for f in feats.values() if f["state"] == "passing"]
    print(f"VCR: {len(ver)}/{len(act) or 1} verified/active; passing={len(pas)}; WIP(active)={len([f for f in feats.values() if f['state']=='active'])}")
    sys.exit(rc)

fid, target = sys.argv[5], sys.argv[6]
if fid not in feats:
    print(f"REFUSED: unknown feature {fid}"); sys.exit(1)
f = feats[fid]
cur = f["state"]
if ORDER.index(target) != ORDER.index(cur) + 1:
    audit(fid, cur, target, "REFUSE", "illegal transition")
    print(f"REFUSED: {fid}: {cur} -> {target} is not the next state"); sys.exit(1)
if target == "verified":
    ok = run(f["acceptance_cmd"]); note = "acceptance_cmd"
elif target == "passing":
    ok = all(run(c) for c in ["cd js && npm test", "python3 -m pytest py/tests -q"]); note = "full checks"
else:
    ok, note = True, "state-only"
if not ok:
    audit(fid, cur, target, "REFUSE", note)
    print(f"REFUSED: {fid}: checks failed, {cur} -> {target} NOT applied"); sys.exit(1)
f["state"] = target
data["features"] = sorted(feats.values(), key=lambda x: x["id"])
json.dump(data, open(features_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(features_path, "a", encoding="utf-8").write("\n")
audit(fid, cur, target, "PASS" if target == "passing" else "OK", note)
print(f"OK: {fid}: {cur} -> {target} ({note})")
EOF
}

mkdir -p "$(dirname "$AUDIT")"
if [ "${1:-}" = "--check" ]; then
    gate_py --check
else
    [ $# -eq 2 ] || { echo "usage: verify.sh <feature-id> <state> | verify.sh --check"; exit 1; }
    gate_py "$1" "$2"
fi
