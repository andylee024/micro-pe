#!/usr/bin/env python3
"""
Scout Agent Loop - Autonomous coding system

Implements the agent-coding-container pattern:
- Worker Agent: Implements 1 task per cycle
- Janitor Agent: Cleans tech debt (every 4 cycles)
- Architect Agent: Reviews alignment (every 8 cycles)

Usage:
    python agent_loop.py --workspace ./workspace-name --cycles 10
"""

import os
import json
import time
import argparse
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars set manually


class AgentLoop:
    """Main agent loop coordinator"""

    def __init__(self, workspace: Path, tick_interval: int = 60):
        self.workspace = Path(workspace).absolute()
        self.tick_interval = tick_interval  # Seconds between cycles
        self.state_file = self.workspace / ".state.json"

        # Ensure workspace exists
        self.workspace.mkdir(parents=True, exist_ok=True)

        # Initialize git if not present
        if not (self.workspace / ".git").exists():
            self._run_command("git init", cwd=self.workspace)
            self._run_command("git config user.name 'Agent Worker'", cwd=self.workspace)
            self._run_command("git config user.email 'agent@scout.local'", cwd=self.workspace)

    def _run_command(self, cmd: str, cwd: Optional[Path] = None) -> tuple:
        """Run shell command and return output"""
        import shlex
        result = subprocess.run(
            shlex.split(cmd),
            cwd=cwd or self.workspace,
            capture_output=True,
            text=True
        )
        return result.stdout, result.stderr, result.returncode

    def load_state(self) -> Dict:
        """Load state from .state.json"""
        if not self.state_file.exists():
            return {
                "cycle_count": 0,
                "last_worker_cycle": 0,
                "last_janitor_cycle": 0,
                "last_architect_cycle": 0,
                "blockers": [],
                "status": "running"
            }

        with open(self.state_file) as f:
            return json.load(f)

    def save_state(self, state: Dict):
        """Save state to .state.json"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def bootstrap(self):
        """Bootstrap phase - Architect initializes project"""
        print("\n" + "="*60)
        print("🎬 BOOTSTRAP PHASE")
        print("="*60)

        prd_file = self.workspace / "PRD.md"
        if not prd_file.exists():
            print("❌ No PRD.md found in workspace!")
            print(f"   Create {prd_file} with your requirements first.")
            return False

        # Check if already bootstrapped
        if (self.workspace / "TODO.md").exists():
            print("✅ Already bootstrapped (TODO.md exists)")
            return True

        print("\n🏗️  Running Architect Agent (bootstrap)...")

        # Load PRD
        with open(prd_file) as f:
            prd_content = f.read()

        # Create bootstrap prompt
        prompt = f"""You are the Architect Agent in bootstrap mode.

Your job is to read the PRD and initialize the project structure.

PRD.md:
{prd_content}

Tasks:
1. Create TODO.md with a breakdown of implementation tasks
   - Each task should be 1-2 hours of work
   - Use format: - [ ] Task description (#N)
   - Number tasks sequentially
   - Break down large requirements into specific implementation steps

2. Create ARCHITECTURE.md with high-level system design
   - Describe directory structure
   - Key components and their responsibilities
   - Design patterns to follow

3. Create LEARNINGS.md (initially empty, but include header)
   - This will store patterns/decisions as work progresses

Output your response in this exact format:

---TODO.md---
[TODO content here]

---ARCHITECTURE.md---
[ARCHITECTURE content here]

---LEARNINGS.md---
[LEARNINGS content here]
"""

        # Call Claude
        response = self._call_claude(prompt, max_tokens=4000)

        # Parse response and create files
        self._parse_and_create_files(response)

        # Initial git commit
        self._run_command("git add .", cwd=self.workspace)
        self._run_command("git commit -m 'Bootstrap: Initialize project structure'", cwd=self.workspace)

        print("✅ Bootstrap complete!")
        return True

    def _call_claude(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Call Claude API via claude_caller module
        """
        from claude_caller import call_claude_api
        return call_claude_api(prompt, max_tokens=max_tokens)

    def _parse_and_create_files(self, response: str):
        """Parse agent response and create files"""
        # Find sections marked with ---FILENAME---
        pattern = r'---([A-Z_\.a-z]+)---\n(.*?)(?=\n---[A-Z_\.a-z]+---|$)'
        matches = re.findall(pattern, response, re.DOTALL)

        for filename, content in matches:
            filepath = self.workspace / filename
            filepath.write_text(content.strip() + "\n")
            print(f"   ✅ Created {filename}")

    def get_fresh_context(self, agent_type: str) -> str:
        """Load fresh context for agent (NO conversation history)"""
        context_parts = []

        # 1. PRD (always include)
        prd_file = self.workspace / "PRD.md"
        if prd_file.exists():
            context_parts.append(f"# PRD.md\n\n{prd_file.read_text()}")

        # 2. TODO (always include)
        todo_file = self.workspace / "TODO.md"
        if todo_file.exists():
            context_parts.append(f"\n# TODO.md\n\n{todo_file.read_text()}")

        # 3. ARCHITECTURE (always include)
        arch_file = self.workspace / "ARCHITECTURE.md"
        if arch_file.exists():
            context_parts.append(f"\n# ARCHITECTURE.md\n\n{arch_file.read_text()}")

        # 4. LEARNINGS (always include)
        learn_file = self.workspace / "LEARNINGS.md"
        if learn_file.exists():
            context_parts.append(f"\n# LEARNINGS.md\n\n{learn_file.read_text()}")

        # 5. Git log (last 10 commits)
        git_log, _, _ = self._run_command("git log --oneline -10", cwd=self.workspace)
        if git_log.strip():
            context_parts.append(f"\n# Recent Git Commits\n\n```\n{git_log}\n```")

        # 6. Comms inbox (human responses)
        inbox_dir = self.workspace / "comms" / "inbox"
        if inbox_dir.exists():
            inbox_files = list(inbox_dir.glob("*.md"))
            if inbox_files:
                context_parts.append("\n# Human Responses (comms/inbox/)\n")
                for f in inbox_files:
                    context_parts.append(f"\n## {f.name}\n\n{f.read_text()}")

        # 7. Current code files (agent-specific, limited)
        if agent_type == "worker":
            context_parts.append("\n# Available Code Files\n")
            # List Python files but don't load all (keep context small)
            py_files = list(self.workspace.glob("*.py"))
            if py_files:
                context_parts.append("\nPython files in workspace:\n")
                for f in sorted(py_files)[:5]:  # Limit to 5 files
                    context_parts.append(f"- {f.name}\n")

        return "\n".join(context_parts)

    def run_worker_agent(self, cycle: int):
        """Run Worker Agent - implements ONE task"""
        print(f"\n👷 Running Worker Agent (Cycle {cycle})...")

        # Load fresh context
        context = self.get_fresh_context("worker")

        # Worker prompt
        prompt = f"""You are the Worker Agent. Your job is to implement ONE task from TODO.md.

{context}

Instructions:
1. Read TODO.md and find the FIRST incomplete task (marked [ ])
2. Implement that task (write code, tests, documentation)
3. Keep changes focused and incremental (quality over quantity)
4. If blocked, create a file in comms/outbox/blocker-XXX.md explaining the issue
5. Mark task complete in TODO.md by changing [ ] to [x]

Output Format:

---ACTION---
[Describe what you're doing - 1-2 sentences]

---FILES---
[List files you're modifying/creating]

---CODE---
filepath: path/to/file.py
```python
[Full file content]
```

filepath: path/to/another.py
```python
[Full file content]
```

---TODO_UPDATE---
[Updated TODO.md content with task marked [x]]

---COMMIT_MESSAGE---
[Git commit message - one line, clear description]

---BLOCKER--- (only if blocked, otherwise omit this section)
[Blocker description if you can't complete task]

IMPORTANT:
- Only work on ONE task
- Provide COMPLETE file contents, not diffs
- Update TODO.md to mark the task [x] complete
- Write clear, working code
"""

        response = self._call_claude(prompt, max_tokens=4000)

        # Parse and apply changes
        self._apply_worker_changes(response, cycle)

    def _apply_worker_changes(self, response: str, cycle: int):
        """Apply Worker Agent changes"""
        print("   Applying changes...")

        # Parse response sections
        sections = {}
        pattern = r'---([A-Z_]+)---\n(.*?)(?=\n---[A-Z_]+---|$)'
        matches = re.findall(pattern, response, re.DOTALL)

        for section_name, content in matches:
            sections[section_name] = content.strip()

        # Show action
        if 'ACTION' in sections:
            print(f"   📝 {sections['ACTION'][:100]}...")

        # 1. Write code files
        if 'CODE' in sections:
            code_blocks = re.findall(
                r'filepath:\s*(.+?)\n```(?:python|bash|json|yaml)?\n(.*?)```',
                sections['CODE'],
                re.DOTALL
            )
            for filepath, code in code_blocks:
                filepath = filepath.strip()
                full_path = self.workspace / filepath
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(code.strip() + "\n")
                print(f"   ✅ Wrote {filepath}")

        # 2. Update TODO.md
        if 'TODO_UPDATE' in sections:
            todo_file = self.workspace / "TODO.md"
            todo_file.write_text(sections['TODO_UPDATE'] + "\n")
            print("   ✅ Updated TODO.md")

        # 3. Create git commit
        if 'COMMIT_MESSAGE' in sections:
            self._run_command("git add .", cwd=self.workspace)
            commit_msg = sections['COMMIT_MESSAGE'].replace('"', '\\"')[:100]
            self._run_command(f'git commit -m "{commit_msg}"', cwd=self.workspace)
            print(f"   ✅ Git commit: {sections['COMMIT_MESSAGE'][:50]}...")

        # 4. Create blocker if needed
        if 'BLOCKER' in sections:
            blockers_dir = self.workspace / "comms" / "outbox"
            blockers_dir.mkdir(parents=True, exist_ok=True)
            blocker_file = blockers_dir / f"blocker-{cycle:03d}.md"
            blocker_file.write_text(sections['BLOCKER'])
            print(f"   ⚠️  Created blocker: {blocker_file.name}")

    def run_janitor_agent(self, cycle: int):
        """Run Janitor Agent - cleans tech debt"""
        print(f"\n🧹 Running Janitor Agent (Cycle {cycle})...")

        context = self.get_fresh_context("janitor")

        prompt = f"""You are the Janitor Agent. Your job is to clean up technical debt.

{context}

Instructions:
1. Review completed tasks in TODO.md
2. Check code for:
   - Unused imports
   - Dead code
   - Inconsistent naming
   - Missing error handling
   - Code duplication
   - Debug print statements
3. Refactor/clean as needed
4. Remove completed tasks from TODO.md (keep active tasks only)
5. Git commit your cleanup changes

Output same format as Worker Agent (ACTION, FILES, CODE, TODO_UPDATE, COMMIT_MESSAGE)
"""

        response = self._call_claude(prompt, max_tokens=3000)
        self._apply_janitor_changes(response, cycle)

    def _apply_janitor_changes(self, response: str, cycle: int):
        """Apply Janitor Agent changes"""
        print("   Cleaning up...")
        # Use same parsing logic as Worker
        self._apply_worker_changes(response, cycle)

    def run_architect_agent(self, cycle: int):
        """Run Architect Agent - ensures alignment"""
        print(f"\n🏗️  Running Architect Agent (Cycle {cycle})...")

        context = self.get_fresh_context("architect")

        prompt = f"""You are the Architect Agent. Your job is to ensure long-term alignment.

{context}

Instructions:
1. Compare PRD.md goals vs current TODO.md progress
2. Check if actual code matches ARCHITECTURE.md design
3. Identify gaps or misalignments
4. Break down large/unclear tasks in TODO.md
5. Update ARCHITECTURE.md if design evolved
6. Update TODO.md with refined tasks

Output same format as Worker Agent (ACTION, FILES, CODE, TODO_UPDATE, COMMIT_MESSAGE)
Focus on TODO.md and ARCHITECTURE.md updates, not code.
"""

        response = self._call_claude(prompt, max_tokens=3000)
        self._apply_architect_changes(response, cycle)

    def _apply_architect_changes(self, response: str, cycle: int):
        """Apply Architect Agent changes"""
        print("   Reviewing alignment...")
        # Use same parsing logic as Worker
        self._apply_worker_changes(response, cycle)

    def run_cycle(self, cycle: int, state: Dict):
        """Run one cycle of the agent loop"""
        print("\n" + "="*60)
        print(f"🔄 CYCLE {cycle}")
        print("="*60)

        # Determine which agents run
        run_worker = True
        run_janitor = (cycle % 4 == 0)
        run_architect = (cycle % 8 == 0)

        print(f"\n   Worker: {'✓' if run_worker else '–'}")
        print(f"   Janitor: {'✓' if run_janitor else '–'}")
        print(f"   Architect: {'✓' if run_architect else '–'}")

        # Run agents
        try:
            if run_worker:
                self.run_worker_agent(cycle)
                state["last_worker_cycle"] = cycle

            if run_janitor:
                self.run_janitor_agent(cycle)
                state["last_janitor_cycle"] = cycle

            if run_architect:
                self.run_architect_agent(cycle)
                state["last_architect_cycle"] = cycle

        except Exception as e:
            print(f"\n❌ Error in cycle {cycle}: {e}")
            import traceback
            traceback.print_exc()

        # Update state
        state["cycle_count"] = cycle
        self.save_state(state)

        print(f"\n✅ Cycle {cycle} complete")

    def check_termination(self) -> bool:
        """Check if should terminate"""
        done_file = self.workspace / ".done"
        if done_file.exists():
            print("\n" + "="*60)
            print("✅ .done file detected - Project complete!")
            print("="*60)
            return True
        return False

    def run(self, max_cycles: Optional[int] = None):
        """Main loop"""
        print("\n" + "="*60)
        print("🚀 SCOUT AGENT LOOP")
        print("="*60)
        print(f"\nWorkspace: {self.workspace}")
        print(f"Tick interval: {self.tick_interval}s")
        print(f"Max cycles: {max_cycles or 'unlimited'}")

        # Bootstrap if needed
        if not self.bootstrap():
            return

        # Load state
        state = self.load_state()
        start_cycle = state["cycle_count"] + 1

        # Main loop
        try:
            cycle = start_cycle
            while True:
                # Check max cycles
                if max_cycles and cycle > max_cycles:
                    print(f"\n⏹️  Reached max cycles ({max_cycles})")
                    break

                # Run cycle
                self.run_cycle(cycle, state)

                # Check termination
                if self.check_termination():
                    break

                # Sleep until next cycle (skip for first cycle)
                if cycle > start_cycle:
                    print(f"\n💤 Sleeping {self.tick_interval}s until next cycle...")
                    time.sleep(self.tick_interval)

                cycle += 1

        except KeyboardInterrupt:
            print("\n\n⏹️  Interrupted by user")
            self.save_state(state)

        print("\n" + "="*60)
        print("👋 Agent loop stopped")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Scout Agent Loop")
    parser.add_argument(
        "--workspace",
        type=str,
        default="./workspace-test",
        help="Path to workspace directory"
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=None,
        help="Max cycles to run (default: unlimited)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Seconds between cycles (default: 60)"
    )

    args = parser.parse_args()

    loop = AgentLoop(
        workspace=Path(args.workspace),
        tick_interval=args.interval
    )

    loop.run(max_cycles=args.cycles)


if __name__ == "__main__":
    main()
