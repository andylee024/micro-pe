# Claude Development Guidelines

This document defines the development process and standards for working with Claude Code on this project.

---

## Feature Development Process

Every feature MUST follow this structured process:

### 1. Feature Setup

When starting a new feature, create the feature directory structure:

```
docs/feature/<feature-name>/
├── research.md    # Research findings, data sources, technical investigation
└── plan.md        # Implementation plan, architecture, milestones
```

**Example:**
```
docs/feature/scout-v0/
├── research.md
└── plan.md

docs/feature/data-pipeline-v0/
├── research.md
└── plan.md
```

### 2. Research Phase

**File:** `docs/feature/<feature-name>/research.md`

**Purpose:** Comprehensive research before planning implementation

**Content includes:**
- Problem statement and business value
- Technical investigation (APIs, libraries, approaches)
- Data source analysis
- Competitive analysis
- Risks and constraints
- Web research findings with sources cited
- First principles reasoning

**Deliverable:** Complete research document (typically 1,000-3,000+ lines for major features)

### 3. Planning Phase

**File:** `docs/feature/<feature-name>/plan.md`

**Purpose:** Detailed implementation roadmap

**Content includes:**
- Architecture design
- File structure (what files to create/modify)
- Implementation details (methods, functions, data structures)
- Testing strategy
- Success metrics
- Timeline and milestones
- Critical files to reference
- Dependencies and prerequisites

**CRITICAL RULE:** Always review `plan.md` thoroughly before starting implementation

### 4. Implementation Phase

**Process:**
1. **Review plan.md** - Understand the full scope before writing code
2. **Follow the plan** - Implement according to the documented architecture
3. **Test incrementally** - Write and run tests as you implement
4. **Update plan if needed** - If requirements change, update plan.md first

**Best practices:**
- Use agent teams for parallel work when appropriate
- Break large tasks into smaller, incremental pieces
- Run tests frequently to catch issues early
- Document any deviations from the plan

### 5. Completion Phase

**Cleanup checklist:**
- ✅ All tests passing
- ✅ Code committed to git (feature branch)
- ✅ Documentation updated (README, inline comments)
- ✅ Remove debug files (debug_*.py, debug_*.html, *.png screenshots)
- ✅ Clean up temporary files and outputs
- ✅ Update plan.md with "COMPLETED" status and completion date
- ✅ Create PR description if needed

**File cleanup examples:**
```bash
# Remove debug files
rm debug_*.py debug_*.html *.png

# Remove temporary outputs
rm -rf /tmp/feature-outputs

# Clean up test cache
rm -rf .pytest_cache __pycache__
```

---

## Development Standards

### Git Workflow

**Branch naming:**
```
feature/<feature-name>    # New features
fix/<bug-name>           # Bug fixes
refactor/<scope>         # Refactoring work
```

**Commit message format:**
```
<type>: <description>

<optional body>

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types:** feat, fix, refactor, test, docs, chore

### Code Quality

**Testing requirements:**
- ✅ Write tests for all new functionality
- ✅ Aim for >80% code coverage
- ✅ Include unit tests and integration tests
- ✅ Add validation tests for scrapers/APIs

**Code organization:**
- Follow existing project structure
- Use descriptive names for files, functions, classes
- Add docstrings to public APIs
- Keep functions focused and single-purpose

**Anti-patterns to avoid:**
- ❌ Don't create files without reading plan.md first
- ❌ Don't skip the research phase for complex features
- ❌ Don't implement without reviewing the plan
- ❌ Don't leave debug files in the repo
- ❌ Don't commit broken tests

### Documentation

**Inline documentation:**
- Docstrings for all classes and public methods
- Comments for complex logic only (code should be self-documenting)
- Type hints for function signatures

**Project documentation:**
- Update README.md when adding major features
- Keep docs/feature/<feature-name>/ structure updated
- Document API changes and breaking changes

---

## Agent Team Development

When using Claude Code's agent teams:

### When to use agents

**Good use cases:**
- Parallel implementation of independent components
- Large features that can be broken into 3-5 sub-tasks
- Research tasks that require extensive investigation
- Incremental development of related features

**Bad use cases:**
- Single, simple tasks (just do it directly)
- Highly interdependent tasks (sequential work required)
- Tasks requiring constant back-and-forth with user

### Agent task breakdown

**Principles:**
- Break down tasks into incremental parts
- Each agent should have clear, specific objectives
- Agents should work in parallel when possible
- Aim for 3-5 agents max per feature

**Example breakdown:**
```
Feature: Terminal UI for Scout V0
├── Agent 1: UI Components (panels, tables, headers)
├── Agent 2: Keyboard Handler (input processing)
├── Agent 3: Terminal Controller (main app logic)
└── Agent 4: Integration & Testing (wire everything together)
```

### Agent coordination

- Provide each agent with context (plan.md, reference files)
- Set clear success criteria
- Review agent outputs before merging
- Run tests after agent work completes

---

## Current Project Structure

```
scout/                              # Project root (renamed from micro-pe)
├── docs/
│   ├── prd.md                      # Product requirements
│   ├── feature/
│   │   ├── scout-v0/               # ✅ COMPLETED
│   │   │   ├── research.md
│   │   │   ├── plan.md
│   │   │   └── PR_DESCRIPTION.md
│   │   └── data-pipeline-v0/       # 🔄 IN PROGRESS
│   │       ├── research.md         # ✅ Complete
│   │       └── plan.md             # 📋 Ready for implementation
│   └── RESEARCH.md                 # Legacy research (pre-structure)
├── scout/                          # Scout terminal application
│   ├── main.py                     # CLI entry point
│   ├── ui/                         # Terminal UI components
│   └── config.py                   # Configuration
├── core/                           # Core infrastructure
│   ├── base.py                     # Base classes (Tool, Scraper)
│   └── utils/                      # Shared utilities
│       ├── export.py               # CSV/JSON export
│       ├── errors.py               # Custom exceptions
│       └── query_parser.py         # NLP query parsing
├── sources/                        # Data source scrapers (by type)
│   ├── fdd/                        # FDD scrapers
│   │   ├── minnesota.py           # ✅ Minnesota CARDS
│   │   └── wisconsin.py           # ✅ Wisconsin DFI
│   ├── maps/                       # Directory scrapers
│   │   └── google_maps.py         # Google Maps API
│   └── marketplaces/               # Business marketplaces
│       └── bizbuysell.py          # BizBuySell
├── tests/                          # Test suite (mirrors source structure)
│   ├── core/
│   ├── sources/
│   │   ├── fdd/
│   │   │   └── test_wisconsin.py  # ✅ 14 tests passing
│   │   └── maps/
│   └── scout/
├── scripts/                        # Utility scripts
├── outputs/                        # Data outputs (gitignored)
└── CLAUDE.md                       # Development guidelines
```

---

## Feature Status Tracking

### Completed Features ✅

| Feature | Status | Branch | Tests | Notes |
|---------|--------|--------|-------|-------|
| scout-v0 | ✅ Complete | `feature/scout-v0` | 194 passing (85% coverage) | Terminal UI with Google Maps integration |
| wisconsin-fdd-fix | ✅ Complete | `main` | 14 passing (100%) | Fixed scraper after website changes |
| directory-restructure | ✅ Complete | `main` | All passing | Migrated to Option 1 (Type-Based) structure |

### In Progress 🔄

| Feature | Status | Phase | Next Steps |
|---------|--------|-------|------------|
| data-pipeline-v0 | 🔄 Research complete | Planning | Review plan.md, begin implementation |

### Planned 📋

- NASAA FRED FDD Scraper (7 states)
- California DocQNet FDD Scraper
- FDD Aggregator (unified interface)
- Reddit sentiment monitoring
- Secretary of State bulk data integration

---

## Working with Claude Code

### Before starting ANY feature work:

1. ✅ Create `docs/feature/<feature-name>/` directory
2. ✅ Write `research.md` with comprehensive research
3. ✅ Write `plan.md` with implementation details
4. ✅ Review plan.md to understand full scope
5. ✅ Only then begin implementation

### During implementation:

- Reference the plan.md frequently
- Test incrementally
- Update plan.md if scope changes
- Clean up debug files as you go

### After completing feature:

- Run full test suite
- Clean up all temporary files
- Mark feature as COMPLETED in plan.md
- Create PR description if needed
- Commit and push to feature branch

---

## Questions?

If you're unsure about any part of this process:
1. Read the plan.md for the feature
2. Check similar completed features for examples
3. Ask the user for clarification

---

**Last Updated:** 2026-02-19
**Project:** Scout (SMB Research & Due Diligence Platform)
**Maintainer:** Andy Lee
