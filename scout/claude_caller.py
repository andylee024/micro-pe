#!/usr/bin/env python3
"""
Claude API Caller for Agent Loop

Handles calling Claude API with proper error handling and token management.
"""

import os
import time
from typing import Optional

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def call_claude_api(
    prompt: str,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    model: str = "claude-sonnet-4-5-20250929"
) -> str:
    """
    Call Claude API and return response text.

    Args:
        prompt: The prompt to send to Claude
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature (0-1)
        model: Claude model to use

    Returns:
        Response text from Claude
    """
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY not set!")
        print("   Set it: export ANTHROPIC_API_KEY=your-key-here")
        print("   Using simulation mode...")
        return _simulated_response(prompt)

    try:
        # Try importing anthropic SDK
        from anthropic import Anthropic
    except ImportError:
        print("\n⚠️  anthropic package not installed!")
        print("   Run: pip install anthropic")
        print("   Using simulation mode...")
        return _simulated_response(prompt)

    # Call API
    try:
        client = Anthropic(api_key=api_key)

        print(f"\n📞 Calling Claude API...")
        print(f"   Model: {model}")
        print(f"   Prompt: {len(prompt)} chars")
        print(f"   Max tokens: {max_tokens}")

        start_time = time.time()

        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        elapsed = time.time() - start_time

        response_text = message.content[0].text

        print(f"   ✅ Response: {len(response_text)} chars")
        print(f"   ⏱️  Time: {elapsed:.1f}s")
        print(f"   🪙 Tokens: {message.usage.input_tokens} in, {message.usage.output_tokens} out")

        return response_text

    except Exception as e:
        print(f"\n❌ API Error: {e}")
        print("   Falling back to simulation mode...")
        return _simulated_response(prompt)


def _simulated_response(prompt: str) -> str:
    """
    Return simulated response for testing without API.
    """
    print("\n🎭 Using simulated response (no real API call)")

    # Detect if it's bootstrap phase
    if "bootstrap" in prompt.lower() and "TODO.md" in prompt:
        return _simulated_bootstrap_response(prompt)

    # Detect if it's worker phase
    if "Worker Agent" in prompt:
        return _simulated_worker_response(prompt)

    # Detect if it's janitor phase
    if "Janitor Agent" in prompt:
        return _simulated_janitor_response(prompt)

    # Detect if it's architect phase
    if "Architect Agent" in prompt:
        return _simulated_architect_response(prompt)

    return "---ACTION---\nSimulated response - implement actual API call\n"


def _simulated_bootstrap_response(prompt: str) -> str:
    """Simulated bootstrap response based on PRD"""

    # Extract industry/goal from prompt if possible
    goal = "Build FDD scrapers"
    if "Wisconsin" in prompt:
        goal = "Build Wisconsin FDD scraper"
    elif "5 scrapers" in prompt or "five scrapers" in prompt:
        goal = "Build 5-scraper FDD system"

    return f"""---TODO.md---
# Scout FDD Scraper Implementation - TODO

## Phase 1: Wisconsin FDD Scraper (Priority)
- [ ] Create tools/wisconsin_fdd.py skeleton (#1)
- [ ] Add Chrome driver setup with anti-detection (#2)
- [ ] Implement ASP.NET form filling (#3)
- [ ] Parse GridView results table (#4)
- [ ] Extract franchise metadata (#5)
- [ ] Implement PDF download (#6)
- [ ] Implement Item 19 extraction (#7)
- [ ] Add caching layer (90-day TTL) (#8)
- [ ] Create test_wisconsin_fdd.py (#9)
- [ ] Test with validation queries (#10)

## Phase 2: NASAA FRED Scraper
- [ ] Create tools/nasaa_fred_fdd.py skeleton (#11)
- [ ] Implement multi-state search (#12)
- [ ] Add state provenance tracking (#13)
- [ ] Test across 7 states (#14)

## Phase 3: California FDD Scraper
- [ ] Create tools/california_fdd.py skeleton (#15)
- [ ] Handle slow database (7-10s waits) (#16)
- [ ] Implement pagination (#17)
- [ ] Add document type filtering (#18)

## Phase 4: FDD Aggregator
- [ ] Create tools/fdd_aggregator.py (#19)
- [ ] Implement search_all method (#20)
- [ ] Add deduplication logic (#21)
- [ ] Add coverage statistics (#22)

## Phase 5: BizBuySell Enhancement
- [ ] Enhance tools/bizbuysell_tool.py (#23)
- [ ] Add error handling (#24)
- [ ] Test with real queries (#25)

---ARCHITECTURE.md---
# Scout FDD Scraper System - Architecture

## Goal
{goal}

## System Overview

```
User Query → FDD Aggregator → Wisconsin/California/NASAA Scrapers → Cache → JSON
```

## Components

### 1. Wisconsin FDD Scraper (tools/wisconsin_fdd.py)
- Inherits from Tool base class
- Selenium + BeautifulSoup
- ASP.NET GridView parsing
- Direct PDF downloads
- 90-day cache TTL

### 2. NASAA FRED Scraper (tools/nasaa_fred_fdd.py)
- Multi-state coverage (7 states)
- State provenance tracking
- Same Tool pattern

### 3. California Scraper (tools/california_fdd.py)
- Largest state database
- Pagination support
- Document filtering

### 4. FDD Aggregator (tools/fdd_aggregator.py)
- Unified query interface
- Cross-state deduplication
- Coverage statistics

## Design Patterns

**Tool Pattern:**
- All scrapers inherit from tools/base.py
- Consistent search() API
- 90-day caching
- Clean JSON responses

**Reference Implementation:**
- tools/minnesota_fdd.py (449 lines)
- Copy structure, adapt specifics

**Anti-Detection:**
- Chrome CDP overrides
- User-agent spoofing
- Rate limiting (2-5s waits)

---LEARNINGS.md---
# Scout FDD Scraper - Learnings

## Project Context
Building multi-state FDD scraper system for SMB due diligence

## Reference Implementation
tools/minnesota_fdd.py (449 lines) - GOLD STANDARD
Copy this structure for all new scrapers

## Key Patterns
(Will be updated as implementation progresses)
"""


def _simulated_worker_response(prompt: str) -> str:
    """Simulated worker response"""
    return """---ACTION---
Creating wisconsin_fdd.py skeleton following minnesota_fdd.py pattern

---FILES---
- tools/wisconsin_fdd.py (create)

---CODE---
filepath: tools/wisconsin_fdd.py
```python
\"\"\"Wisconsin FDD Scraper\"\"\"

from pathlib import Path
from typing import Dict, Any
from datetime import datetime

try:
    from .base import Tool
except ImportError:
    from base import Tool


class WisconsinFDDScraper(Tool):
    \"\"\"Search Wisconsin DFI for FDD documents\"\"\"

    BASE_URL = "https://apps.dfi.wi.gov/apps/FranchiseSearch/MainSearch.aspx"
    CACHE_TTL_DAYS = 90

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = Path("outputs/fdds/wisconsin")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def search(
        self,
        industry: str,
        max_results: int = 10,
        download_pdfs: bool = True,
        extract_item19: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        \"\"\"
        Search for Wisconsin FDD documents.

        Args:
            industry: Business type (e.g., "car wash")
            max_results: Max FDD documents to return
            download_pdfs: Whether to download PDF files
            extract_item19: Whether to extract Item 19 text
            use_cache: Whether to use cached results

        Returns:
            Dict with FDD search results
        \"\"\"
        # TODO: Implement search logic
        pass
```

---TODO_UPDATE---
# Scout FDD Scraper Implementation - TODO

## Phase 1: Wisconsin FDD Scraper (Priority)
- [x] Create tools/wisconsin_fdd.py skeleton (#1)
- [ ] Add Chrome driver setup with anti-detection (#2)
- [ ] Implement ASP.NET form filling (#3)
- [ ] Parse GridView results table (#4)
- [ ] Extract franchise metadata (#5)
- [ ] Implement PDF download (#6)
- [ ] Implement Item 19 extraction (#7)
- [ ] Add caching layer (90-day TTL) (#8)
- [ ] Create test_wisconsin_fdd.py (#9)
- [ ] Test with validation queries (#10)

## Phase 2: NASAA FRED Scraper
- [ ] Create tools/nasaa_fred_fdd.py skeleton (#11)
- [ ] Implement multi-state search (#12)
- [ ] Add state provenance tracking (#13)
- [ ] Test across 7 states (#14)

## Phase 3: California FDD Scraper
- [ ] Create tools/california_fdd.py skeleton (#15)
- [ ] Handle slow database (7-10s waits) (#16)
- [ ] Implement pagination (#17)
- [ ] Add document type filtering (#18)

## Phase 4: FDD Aggregator
- [ ] Create tools/fdd_aggregator.py (#19)
- [ ] Implement search_all method (#20)
- [ ] Add deduplication logic (#21)
- [ ] Add coverage statistics (#22)

## Phase 5: BizBuySell Enhancement
- [ ] Enhance tools/bizbuysell_tool.py (#23)
- [ ] Add error handling (#24)
- [ ] Test with real queries (#25)

---COMMIT_MESSAGE---
Create WisconsinFDDScraper skeleton (#1)
"""


def _simulated_janitor_response(prompt: str) -> str:
    """Simulated janitor response"""
    return """---ACTION---
Reviewing code for cleanup opportunities. Code looks clean so far.

---TODO_UPDATE---
# Scout FDD Scraper Implementation - TODO

## Phase 1: Wisconsin FDD Scraper (Priority)
- [ ] Add Chrome driver setup with anti-detection (#2)
- [ ] Implement ASP.NET form filling (#3)
- [ ] Parse GridView results table (#4)
- [ ] Extract franchise metadata (#5)
- [ ] Implement PDF download (#6)
- [ ] Implement Item 19 extraction (#7)
- [ ] Add caching layer (90-day TTL) (#8)
- [ ] Create test_wisconsin_fdd.py (#9)
- [ ] Test with validation queries (#10)

## Phase 2: NASAA FRED Scraper
- [ ] Create tools/nasaa_fred_fdd.py skeleton (#11)
- [ ] Implement multi-state search (#12)
- [ ] Add state provenance tracking (#13)
- [ ] Test across 7 states (#14)

## Phase 3: California FDD Scraper
- [ ] Create tools/california_fdd.py skeleton (#15)
- [ ] Handle slow database (7-10s waits) (#16)
- [ ] Implement pagination (#17)
- [ ] Add document type filtering (#18)

## Phase 4: FDD Aggregator
- [ ] Create tools/fdd_aggregator.py (#19)
- [ ] Implement search_all method (#20)
- [ ] Add deduplication logic (#21)
- [ ] Add coverage statistics (#22)

## Phase 5: BizBuySell Enhancement
- [ ] Enhance tools/bizbuysell_tool.py (#23)
- [ ] Add error handling (#24)
- [ ] Test with real queries (#25)

---COMMIT_MESSAGE---
Janitor: Clean up completed tasks from TODO
"""


def _simulated_architect_response(prompt: str) -> str:
    """Simulated architect response"""
    return """---ACTION---
Reviewing alignment with PRD. Progress on track, task breakdown looks good.

---COMMIT_MESSAGE---
Architect: Review alignment (cycle 8)
"""


if __name__ == "__main__":
    # Test the API caller
    prompt = "Hello Claude! Please respond with a short test message."
    response = call_claude_api(prompt, max_tokens=100)
    print(f"\nResponse:\n{response}")
