#!/usr/bin/env bash
# Scout Ralph Loop — stateless, file-based agent loop
#
# Usage:
#   bash ralph/loop.sh <prd.json> [max_iterations]
#
# Each iteration spawns a fresh Claude instance with one story to complete.
# Memory lives in: PRD JSON (status), .ralph/progress.md (log), outputs/ (data)
#
# Completion signal: <promise>COMPLETE</promise> in agent output

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRD="${1:?Usage: loop.sh <prd.json> [max_iterations]}"
MAX_ITER="${2:-20}"

PROMPT_TEMPLATE="$SCRIPT_DIR/PROMPT.md"
PROGRESS=".ralph/progress.md"
RUNS_DIR=".ralph/runs"

mkdir -p "$RUNS_DIR"

# Initialize progress log on first run
if [ ! -f "$PROGRESS" ]; then
    {
        echo "# Scout Progress Log"
        echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "PRD: $PRD"
        echo "---"
    } > "$PROGRESS"
fi

echo ""
echo "══════════════════════════════════════════"
echo "  Scout Ralph Loop"
echo "  PRD: $PRD"
echo "  Max iterations: $MAX_ITER"
echo "══════════════════════════════════════════"

for i in $(seq 1 "$MAX_ITER"); do
    echo ""
    echo "━━━ Iteration $i / $MAX_ITER ━━━"

    # Select the next eligible story
    STORY_ID=$(python3 "$SCRIPT_DIR/prd_utils.py" select "$PRD")

    if [ "$STORY_ID" = "NONE" ]; then
        echo "✓ All stories complete"
        exit 0
    fi

    if [ "$STORY_ID" = "WAITING" ]; then
        echo "⏳ All open stories are blocked by unfinished dependencies"
        echo "   Check for stalled in_progress stories in: $PRD"
        exit 1
    fi

    echo "→ Story: $STORY_ID"

    # Mark story as in_progress
    python3 "$SCRIPT_DIR/prd_utils.py" start "$PRD" "$STORY_ID"

    # Render the prompt for this story
    PROMPT=$(python3 "$SCRIPT_DIR/prd_utils.py" render "$PROMPT_TEMPLATE" "$PRD" "$STORY_ID" "$PROGRESS")

    # Run Claude — fresh instance, no --resume (stateless by design)
    RUN_LOG="$RUNS_DIR/iter_$(printf '%03d' "$i")_${STORY_ID}.log"
    echo "$PROMPT" | claude --dangerously-skip-permissions --print 2>&1 | tee "$RUN_LOG"
    OUTPUT=$(cat "$RUN_LOG")

    # Check for completion signal from agent
    if echo "$OUTPUT" | grep -q "<promise>COMPLETE</promise>"; then
        echo ""
        echo "✓ $STORY_ID complete"
        # Agent is responsible for setting status=done in the PRD
    else
        echo ""
        echo "⚠  No COMPLETE signal — resetting $STORY_ID to open for retry"
        python3 "$SCRIPT_DIR/prd_utils.py" reset "$PRD" "$STORY_ID"
    fi

    sleep 2
done

echo ""
echo "Max iterations ($MAX_ITER) reached without completing all stories"
exit 1
