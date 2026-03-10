#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DIR="$ROOT/docs/feature/hex-ui-exploration/web"
OUT_DIR="$ROOT/docs/feature/hex-ui-exploration/artifacts/screenshots"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

mkdir -p "$OUT_DIR"

if [[ ! -x "$CHROME" ]]; then
  echo "Chrome binary not found at: $CHROME" >&2
  exit 1
fi

render() {
  local page="$1"
  local out="$2"

  "$CHROME" \
    --headless=new \
    --disable-gpu \
    --no-sandbox \
    --hide-scrollbars \
    --run-all-compositor-stages-before-draw \
    --virtual-time-budget=1500 \
    --window-size=1680,1400 \
    --screenshot="$out" \
    "file://$WEB_DIR/$page"
}

render "concept-a-thesis-canvas.html" "$OUT_DIR/concept-a-thesis-canvas.png"
render "concept-b-target-workbench.html" "$OUT_DIR/concept-b-target-workbench.png"
render "index.html" "$OUT_DIR/home-search.png"

echo "Rendered screenshots to $OUT_DIR"
