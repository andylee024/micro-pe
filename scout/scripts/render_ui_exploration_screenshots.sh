#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DIR="$ROOT/docs/feature/hex-ui-exploration/web"
OUT_DIR="$ROOT/docs/feature/hex-ui-exploration/artifacts/screenshots"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT=8134

mkdir -p "$OUT_DIR"

if [[ ! -x "$CHROME" ]]; then
  echo "Chrome binary not found at: $CHROME" >&2
  exit 1
fi

python3 -m http.server "$PORT" --directory "$WEB_DIR" >/tmp/scout_ui_http.log 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" >/dev/null 2>&1 || true' EXIT
sleep 1

render() {
  local url="$1"
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
    "$url"
}

render "http://127.0.0.1:$PORT/concept-a-thesis-canvas.html" "$OUT_DIR/concept-a-thesis-canvas.png"
render "http://127.0.0.1:$PORT/concept-b-target-workbench.html" "$OUT_DIR/concept-b-target-workbench.png"
render "http://127.0.0.1:$PORT/index.html" "$OUT_DIR/home-search.png"

echo "Rendered screenshots to $OUT_DIR"
