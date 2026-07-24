#!/usr/bin/env bash
# KeySwap one-shot macOS helper (Swift package / Accessibility).
# Usage:
#   bash tools/KeySwap/packaging/install-macos.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
KEYSWAP="$(cd "$HERE/.." && pwd)"
APPLE="$KEYSWAP/apple"

echo "KeySwap macOS install helper"
echo "  package: $APPLE"

if ! command -v swift >/dev/null 2>&1; then
  echo "swift not found — install Xcode Command Line Tools:"
  echo "  xcode-select --install"
  exit 1
fi

cd "$APPLE"
if swift build 2>/dev/null; then
  echo "swift build OK"
  BIN="$(swift build --show-bin-path 2>/dev/null || true)"
  if [[ -n "${BIN:-}" ]]; then
    echo "  bin: $BIN"
  fi
else
  echo "swift build failed or needs Xcode project — open apple/ in Xcode and run KeySwapMacApp."
fi

echo ""
echo "Grant Accessibility: System Settings → Privacy & Security → Accessibility"
echo "  (add Terminal / KeySwap so system-wide = cycle works)"
open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility" 2>/dev/null || true

echo ""
echo "Python helpers (Cologne / convert) need python3 on PATH."
echo "Docs: tools/KeySwap/packaging/INSTALL.md"
echo "Done."
