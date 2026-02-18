#!/usr/bin/env python3
"""
PRD manipulation utilities for the Scout Ralph loop.

All JSON reads/writes go through here — keeps loop.sh clean and correct.

Commands:
  select <prd>                                    print next eligible story ID
                                                  or NONE (all done) / WAITING (blocked)
  start  <prd> <story_id>                         mark story in_progress
  reset  <prd> <story_id>                         reset in_progress -> open (failed iter)
  render <template> <prd> <story_id> <progress>   render prompt, print to stdout
  status <prd>                                    print story status summary
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


# ── I/O ──────────────────────────────────────────────────────────────────────

def load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def save(path: str, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


# ── Commands ──────────────────────────────────────────────────────────────────

def select(prd_path: str):
    """
    Find the next story to work on:
      - status == "open"
      - all items in depends_on are "done"

    Prints one of:
      <story_id>  — ready to work
      NONE        — all stories are done
      WAITING     — open stories exist but all are blocked by dependencies
    """
    prd = load(prd_path)
    stories = prd["stories"]

    done_ids = {s["id"] for s in stories if s["status"] == "done"}
    open_stories = [s for s in stories if s["status"] == "open"]
    in_progress = [s for s in stories if s["status"] == "in_progress"]

    # Everything done, nothing in flight
    if not open_stories and not in_progress:
        print("NONE")
        return

    # Find first open story whose dependencies are all satisfied
    for story in open_stories:
        deps = story.get("depends_on", [])
        if all(dep in done_ids for dep in deps):
            print(story["id"])
            return

    # Open stories exist but every one is blocked
    if open_stories:
        print("WAITING")
    else:
        # Only in_progress stories remain (a loop is still running or stalled)
        print("WAITING")


def start(prd_path: str, story_id: str):
    """Mark a story as in_progress with a timestamp."""
    prd = load(prd_path)
    for story in prd["stories"]:
        if story["id"] == story_id:
            story["status"] = "in_progress"
            story["started_at"] = datetime.now(timezone.utc).isoformat()
    save(prd_path, prd)


def reset(prd_path: str, story_id: str):
    """Reset an in_progress story back to open (called when no COMPLETE signal)."""
    prd = load(prd_path)
    for story in prd["stories"]:
        if story["id"] == story_id:
            story["status"] = "open"
            story.pop("started_at", None)
    save(prd_path, prd)


def render(template_path: str, prd_path: str, story_id: str, progress_path: str):
    """
    Render the prompt template with current story context.
    Prints the rendered prompt to stdout (captured by loop.sh).
    """
    prd = load(prd_path)
    story = next(s for s in prd["stories"] if s["id"] == story_id)

    # Story board: all stories with status, for the agent's awareness
    story_board = "\n".join(
        f"  {s['id']} [{s['status'].upper():12}] {s['title']}"
        for s in prd["stories"]
    )

    with open(template_path) as f:
        template = f.read()

    replacements = {
        "{{PROJECT}}":           prd.get("project", "Scout"),
        "{{INDUSTRY}}":          prd.get("industry", ""),
        "{{LOCATION}}":          prd.get("location", ""),
        "{{STORY_ID}}":          story["id"],
        "{{STORY_TITLE}}":       story["title"],
        "{{STORY_DESCRIPTION}}": story.get("description", ""),
        "{{STORY_OUTPUT_FILE}}": story.get("output_file", "outputs/"),
        "{{PRD_PATH}}":          prd_path,
        "{{PROGRESS_PATH}}":     progress_path,
        "{{STORY_BOARD}}":       story_board,
    }

    result = template
    for key, val in replacements.items():
        result = result.replace(key, val)

    print(result)


def status(prd_path: str):
    """Print a human-readable status summary of all stories."""
    prd = load(prd_path)
    print(f"\nProject: {prd.get('project', prd_path)}")
    print(f"Created: {prd.get('created_at', 'unknown')}\n")

    counts = {"open": 0, "in_progress": 0, "done": 0}
    for story in prd["stories"]:
        s = story["status"]
        counts[s] = counts.get(s, 0) + 1
        marker = {"open": "○", "in_progress": "◐", "done": "●"}.get(s, "?")
        print(f"  {marker} {story['id']}  {story['title']}")
        if s == "done" and story.get("completed_at"):
            print(f"       Completed: {story['completed_at']}")

    total = len(prd["stories"])
    print(f"\n  {counts['done']}/{total} done  |  "
          f"{counts['in_progress']} in progress  |  "
          f"{counts['open']} open\n")


# ── Entry point ───────────────────────────────────────────────────────────────

COMMANDS = {
    "select": select,
    "start":  start,
    "reset":  reset,
    "render": render,
    "status": status,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: prd_utils.py <{'|'.join(COMMANDS)}> [args...]", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]
    COMMANDS[cmd](*args)
