# Scout Agent Loop - No-Docker Version

A Python implementation of the agent-coding-container pattern without Docker dependency.

## 🎯 Concept

Autonomous coding system with three specialized agents:
- **Worker Agent** (every cycle): Implements 1 task from TODO.md
- **Janitor Agent** (every 4 cycles): Cleans tech debt
- **Architect Agent** (every 8 cycles): Reviews alignment with PRD

**Key Innovation:** Fresh context per iteration (no conversation history bloat)
**Memory:** Git commits + markdown files (TODO.md, ARCHITECTURE.md, LEARNINGS.md)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Claude API SDK (optional - works in simulation mode without it)
pip install anthropic

# Or add to requirements.txt
echo "anthropic>=0.39.0" >> requirements.txt
pip install -r requirements.txt
```

### 2. Set API Key (Optional)

```bash
# If you want real Claude API calls
export ANTHROPIC_API_KEY=your-key-here

# Or add to .env
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

**Note:** System works in simulation mode without API key (good for testing)

### 3. Create a Workspace

```bash
mkdir workspace-test
cd workspace-test

# Create your PRD
cat > PRD.md <<'EOF'
# Product Requirements: Your Project

## Goal
[What you want to build]

## Requirements
1. [Requirement 1]
2. [Requirement 2]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
EOF
```

### 4. Run Agent Loop

```bash
# From scout/ directory
python agent_loop.py --workspace ./workspace-test --cycles 5

# Options:
#   --workspace PATH    Workspace directory (default: ./workspace-test)
#   --cycles N          Max cycles to run (default: unlimited)
#   --interval SECS     Seconds between cycles (default: 60)
```

---

## 📁 File Structure

### Your Workspace

```
workspace-test/
├── PRD.md                  # YOU CREATE: Project requirements
├── TODO.md                 # GENERATED: Task breakdown
├── ARCHITECTURE.md         # GENERATED: System design
├── LEARNINGS.md            # GENERATED: Patterns & decisions
├── .state.json             # GENERATED: Loop state
├── comms/
│   ├── inbox/              # YOU CREATE: Responses to agent questions
│   └── outbox/             # GENERATED: Agent blockers/questions
└── src/                    # GENERATED: Your code
    ├── your_module.py
    └── test_your_module.py
```

### What Gets Generated

**Bootstrap Phase (first run):**
1. Architect reads PRD.md
2. Creates TODO.md with task breakdown
3. Creates ARCHITECTURE.md with design
4. Creates LEARNINGS.md (initially empty)
5. Initializes git repository

**Each Cycle:**
1. Worker implements 1 task → git commit
2. Updates TODO.md (marks task complete)
3. Updates LEARNINGS.md (if new patterns)

**Every 4th Cycle:**
- Janitor cleans code, removes completed tasks

**Every 8th Cycle:**
- Architect reviews alignment, refines tasks

---

## 🔄 Workflow

### Example: 5-Cycle Run

```
Cycle 1 (0 min):   👷 Worker → Implements task #1 → git commit
Cycle 2 (1 min):   👷 Worker → Implements task #2 → git commit
Cycle 3 (2 min):   👷 Worker → Implements task #3 → git commit
Cycle 4 (3 min):   👷 Worker → Implements task #4 → git commit
                   🧹 Janitor → Cleans code → git commit
Cycle 5 (4 min):   👷 Worker → Implements task #5 → git commit
```

### Watch Progress

```bash
# Terminal 1: Run agent loop
python agent_loop.py --workspace ./workspace-test --cycles 10

# Terminal 2: Watch TODO.md
watch -n 5 'cat workspace-test/TODO.md'

# Terminal 3: Watch git commits
watch -n 5 'cd workspace-test && git log --oneline -10'
```

---

## 💬 Human Communication (Blockers)

### When Agent Gets Stuck

If Worker can't complete a task, it creates a blocker:

```
workspace-test/comms/outbox/blocker-001.md
```

**Blocker Example:**
```markdown
# Blocker: Missing API Key

I need a Google Maps API key to implement the search function.

Options:
1. Provide key in .env file
2. Use mock data for testing
3. Skip this feature

Please advise.

- Worker Agent, Cycle 7
```

### You Respond

Create a response file:

```bash
cat > workspace-test/comms/inbox/response-001.md <<'EOF'
# Re: Missing API Key

Use option 2 (mock data) for now.

Create a `mock_data.py` with sample responses.
We'll add real API later.

- Andy
EOF
```

**Next cycle:** Worker reads your response and continues!

---

## 🧪 Test with Simple Project

### Calculator Example

```bash
# Create workspace
mkdir workspace-calculator
cd workspace-calculator

# Create PRD
cat > PRD.md <<'EOF'
# Product Requirements: Python Calculator

## Goal
Build a calculator module with basic arithmetic operations.

## Requirements
1. Create `calculator.py` module
2. Implement functions:
   - add(a, b)
   - subtract(a, b)
   - multiply(a, b)
   - divide(a, b) - handle divide by zero
3. Write test suite with >80% coverage

## Success Criteria
- [ ] All 4 functions work correctly
- [ ] Tests pass
- [ ] Handles edge cases

## Deliverables
- calculator.py
- test_calculator.py
- README.md
EOF

# Run for 10 cycles (10 minutes)
cd ..
python agent_loop.py --workspace ./workspace-calculator --cycles 10 --interval 60

# After 10 minutes, check output:
cd workspace-calculator
ls -la                    # See generated files
cat TODO.md               # See task progress
git log --oneline         # See commits
python calculator.py      # Test implementation!
```

---

## 🎛️ Configuration

### Simulation Mode (Default)

No API calls, simulated responses. Good for:
- Testing the loop logic
- Understanding the flow
- Developing without API costs

**Usage:** Just run without ANTHROPIC_API_KEY

### Real Claude API Mode

Actual Claude API calls. Better for:
- Real implementation
- Production usage
- Complex tasks

**Setup:**
```bash
export ANTHROPIC_API_KEY=your-key-here
python agent_loop.py --workspace ./workspace-test --cycles 10
```

### Adjusting Intervals

```python
# Fast testing (5 second cycles)
python agent_loop.py --workspace ./test --cycles 10 --interval 5

# Normal (60 second cycles)
python agent_loop.py --workspace ./test --cycles 10 --interval 60

# Slow/careful (5 minute cycles)
python agent_loop.py --workspace ./test --cycles 10 --interval 300
```

---

## 🔍 Monitoring

### Check State

```bash
# View current state
cat workspace-test/.state.json

# Example output:
{
  "cycle_count": 7,
  "last_worker_cycle": 7,
  "last_janitor_cycle": 4,
  "last_architect_cycle": 0,
  "blockers": [],
  "status": "running"
}
```

### View Progress

```bash
# Task completion
grep -c "\\[x\\]" workspace-test/TODO.md  # Completed tasks
grep -c "\\[ \\]" workspace-test/TODO.md  # Remaining tasks

# Git activity
cd workspace-test
git log --oneline --since="1 hour ago"

# Code changes
git diff HEAD~5  # Last 5 commits
```

---

## 🛑 Stopping & Resuming

### Manual Stop

```bash
# Ctrl+C in terminal running agent_loop.py
# State is saved to .state.json
```

### Resume

```bash
# Just run again in same workspace
python agent_loop.py --workspace ./workspace-test

# It continues from last cycle_count in .state.json
```

### Completion (Automatic)

When all tasks done, Worker creates `.done` file:

```bash
# Check for completion
ls workspace-test/.done

# If exists, agent loop stops automatically
```

---

## 📊 Real-World Example: Wisconsin FDD Scraper

### Create PRD

```bash
mkdir workspace-wisconsin
cd workspace-wisconsin

cat > PRD.md <<'EOF'
# Product Requirements: Wisconsin FDD Scraper

## Goal
Build tools/wisconsin_fdd.py following Minnesota pattern.

## Reference
../tools/minnesota_fdd.py (449 lines) - GOLD STANDARD

## Requirements
1. Inherit from Tool base class
2. Implement Chrome driver with anti-detection
3. Parse ASP.NET GridView results
4. Download PDFs
5. Extract Item 19 text
6. Add 90-day caching
7. Write comprehensive test suite

## Wisconsin Specifics
- URL: https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx
- Form ID: ctl00_MainContent_txtSearch
- Table ID: ctl00_MainContent_gvResults
- Direct PDF downloads (easier than Minnesota)

## Success Criteria
- [ ] search("car wash") finds 10+ FDDs
- [ ] Follows minnesota_fdd.py pattern exactly
- [ ] All tests pass
- [ ] Code is clean and documented
EOF
```

### Run Agent Loop

```bash
cd ..
python agent_loop.py --workspace ./workspace-wisconsin --cycles 20 --interval 120

# 20 cycles × 2 minutes = 40 minutes runtime
# Should complete most of implementation
```

### Monitor Progress

```bash
# Terminal 2
watch -n 10 'cat workspace-wisconsin/TODO.md | head -20'

# Terminal 3
watch -n 10 'cd workspace-wisconsin && git log --oneline -5'
```

### Handle Blockers

```bash
# Check for blockers
ls workspace-wisconsin/comms/outbox/

# If blocker exists, read it
cat workspace-wisconsin/comms/outbox/blocker-*.md

# Respond
cat > workspace-wisconsin/comms/inbox/response-001.md <<'EOF'
[Your answer]
EOF
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

**Solution:** Either install it OR run in simulation mode

```bash
# Option 1: Install
pip install anthropic

# Option 2: Use simulation (no install needed)
unset ANTHROPIC_API_KEY
python agent_loop.py --workspace ./test
```

### "No PRD.md found in workspace"

**Solution:** Create PRD.md before running

```bash
echo "# PRD\n\nGoal: Build X\n\nRequirements:\n1. Y" > workspace/PRD.md
```

### "Git not initialized"

**Solution:** Agent loop auto-initializes git, but you can do it manually:

```bash
cd workspace-test
git init
git config user.name "Agent Worker"
git config user.email "agent@scout.local"
```

### Agent Gets Stuck (Same Task Repeatedly)

**Cause:** Worker can't complete task, no blocker created

**Solution:**
1. Check TODO.md - what task is it on?
2. Manually implement that task
3. Update TODO.md to mark [x]
4. Git commit
5. Resume agent loop

### API Rate Limits

**Symptom:** 429 errors from Claude API

**Solution:**
```bash
# Increase interval between cycles
python agent_loop.py --workspace ./test --interval 300  # 5 min

# Or reduce max_tokens
# (Edit claude_caller.py, reduce default max_tokens)
```

---

## 🔧 Extending the System

### Add Custom Agent

Edit `agent_loop.py`, add new agent method:

```python
def run_custom_agent(self, cycle: int):
    """Your custom agent logic"""
    context = self.get_fresh_context("custom")
    prompt = f"Your custom prompt...\n\n{context}"
    response = self._call_claude(prompt)
    # Apply changes...

# Update run_cycle() to call it
def run_cycle(self, cycle: int, state: Dict):
    # ...
    run_custom = (cycle % 16 == 0)  # Every 16th cycle
    if run_custom:
        self.run_custom_agent(cycle)
```

### Customize Prompts

Edit agent prompts in `agent_loop.py`:
- `run_worker_agent()` - Worker prompt
- `run_janitor_agent()` - Janitor prompt
- `run_architect_agent()` - Architect prompt

### Change Agent Intervals

```python
# In run_cycle()
run_janitor = (cycle % 4 == 0)   # Change 4 to your interval
run_architect = (cycle % 8 == 0) # Change 8 to your interval
```

---

## 📚 Files Reference

| File | Purpose | Generated By |
|------|---------|--------------|
| `agent_loop.py` | Main orchestration loop | You (already created) |
| `claude_caller.py` | Claude API interface | You (already created) |
| `workspace-test/PRD.md` | Requirements | You (manual) |
| `workspace-test/TODO.md` | Task breakdown | Architect (bootstrap) |
| `workspace-test/ARCHITECTURE.md` | System design | Architect (bootstrap) |
| `workspace-test/LEARNINGS.md` | Patterns | Agents (ongoing) |
| `workspace-test/.state.json` | Loop state | Agent Loop (automatic) |
| `workspace-test/comms/outbox/` | Agent questions | Worker (when blocked) |
| `workspace-test/comms/inbox/` | Your responses | You (manual) |

---

## 🎓 Next Steps

1. **Try the Simple Test:**
   ```bash
   python agent_loop.py --workspace ./workspace-test --cycles 5 --interval 10
   # Uses the pre-created PRD in workspace-test/
   ```

2. **Watch It Work:**
   - See TODO.md update with [x] marks
   - See git commits being created
   - See files being generated

3. **Test with Real API:**
   ```bash
   export ANTHROPIC_API_KEY=your-key
   python agent_loop.py --workspace ./workspace-test --cycles 10
   ```

4. **Build Wisconsin Scraper:**
   - Create workspace-wisconsin/PRD.md
   - Run for 20-30 cycles
   - Get working scraper implementation!

---

## 💡 Tips

- **Start Small:** Test with simple projects (calculator, validator)
- **Use Simulation:** Develop loop logic without API costs
- **Monitor Actively:** Watch TODO.md and git commits
- **Respond to Blockers:** Check comms/outbox/ regularly
- **Iterate:** Refine PRDs based on what works

---

## 🆚 vs Docker Version

| Feature | Docker Version | Python Version (This) |
|---------|----------------|-----------------------|
| Setup | Complex (Docker, Kilo Code) | Simple (pip install) |
| Runtime | Rust binary | Python script |
| API | Kilo Code | Claude API direct |
| Debugging | Hard (container logs) | Easy (print statements) |
| Customization | Rebuild container | Edit Python file |
| Dependencies | Docker, Docker Compose | Python 3.8+ |

---

**Ready to test? Run:**

```bash
python agent_loop.py --workspace ./workspace-test --cycles 5 --interval 10
```

This will run 5 cycles (50 seconds) and you'll see the agent loop in action!
