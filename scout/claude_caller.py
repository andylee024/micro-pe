#!/usr/bin/env python3
"""
Claude API Caller for Agent Loop

This module handles calling Claude API with proper error handling,
retries, and token management.
"""

import os
import json
import time
from typing import Optional

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars set manually


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
    try:
        # Try importing anthropic SDK
        from anthropic import Anthropic
    except ImportError:
        print("\n⚠️  anthropic package not installed!")
        print("   Run: pip install anthropic")
        return _simulated_response(prompt)

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n⚠️  ANTHROPIC_API_KEY not set!")
        print("   Set it: export ANTHROPIC_API_KEY=your-key-here")
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
        return _simulated_response(prompt)


def _simulated_response(prompt: str) -> str:
    """
    Return simulated response for testing without API.

    This analyzes the prompt and returns reasonable mock data.
    """
    print("\n🎭 Using simulated response (no API call)")

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
    """Simulated bootstrap response"""
    return """---TODO.md---
# Data Validator TODO

## Implementation Tasks
- [ ] Create validator.py skeleton (#1)
- [ ] Implement validate() function signature (#2)
- [ ] Add type checking logic (#3)
- [ ] Add required field checking (#4)
- [ ] Add error messages (#5)
- [ ] Create test_validator.py skeleton (#6)
- [ ] Add test cases for valid data (#7)
- [ ] Add test cases for missing fields (#8)
- [ ] Add test cases for wrong types (#9)
- [ ] Create README.md with examples (#10)

---ARCHITECTURE.md---
# Data Validator Architecture

## Goal
Simple Python module for validating dictionaries against type schemas.

## Structure
```
workspace-test/
├── validator.py        (core validation logic)
├── test_validator.py   (test suite)
└── README.md           (documentation)
```

## Design
- Single `validate(data, schema)` function
- Schema defines expected types for each field
- Returns True/False with optional error messages
- No external dependencies (pure Python)

## Patterns
- Type hints for clarity
- Comprehensive docstrings
- pytest for testing

---LEARNINGS.md---
# Data Validator - Learnings

## Patterns & Decisions

(Will be updated as implementation progresses)
"""


def _simulated_worker_response(prompt: str) -> str:
    """Simulated worker response"""
    # Detect current task from TODO
    if "Create validator.py skeleton" in prompt or "task #1" in prompt.lower():
        return """---ACTION---
Creating validator.py skeleton with basic structure

---FILES---
- validator.py (create)

---CODE---
filepath: validator.py
```python
\"\"\"Simple data validator module\"\"\"

from typing import Dict, Any, Type


def validate(data: Dict[str, Any], schema: Dict[str, Type]) -> bool:
    \"\"\"
    Validate data dictionary against schema.

    Args:
        data: Dictionary to validate
        schema: Schema with field names -> expected types

    Returns:
        True if valid, False otherwise

    Example:
        >>> schema = {"name": str, "age": int}
        >>> validate({"name": "John", "age": 30}, schema)
        True
    \"\"\"
    # TODO: Implement validation logic
    pass
```

---TODO_UPDATE---
# Data Validator TODO

## Implementation Tasks
- [x] Create validator.py skeleton (#1)
- [ ] Implement validate() function signature (#2)
- [ ] Add type checking logic (#3)
- [ ] Add required field checking (#4)
- [ ] Add error messages (#5)
- [ ] Create test_validator.py skeleton (#6)
- [ ] Add test cases for valid data (#7)
- [ ] Add test cases for missing fields (#8)
- [ ] Add test cases for wrong types (#9)
- [ ] Create README.md with examples (#10)

---COMMIT_MESSAGE---
Create validator.py skeleton (#1)
"""

    return """---ACTION---
Simulated worker action - implement actual Claude API

---COMMIT_MESSAGE---
Simulated worker commit
"""


def _simulated_janitor_response(prompt: str) -> str:
    """Simulated janitor response"""
    return """---ACTION---
Reviewing code for cleanup opportunities

Found:
- No unused imports yet
- Code structure looks clean

Updating TODO.md to remove completed tasks.

---TODO_UPDATE---
# Data Validator TODO

## Implementation Tasks
- [ ] Implement validate() function signature (#2)
- [ ] Add type checking logic (#3)
- [ ] Add required field checking (#4)
- [ ] Add error messages (#5)
- [ ] Create test_validator.py skeleton (#6)
- [ ] Add test cases for valid data (#7)
- [ ] Add test cases for missing fields (#8)
- [ ] Add test cases for wrong types (#9)
- [ ] Create README.md with examples (#10)

---COMMIT_MESSAGE---
Janitor: Clean up completed tasks
"""


def _simulated_architect_response(prompt: str) -> str:
    """Simulated architect response"""
    return """---ACTION---
Reviewing alignment with PRD

Progress looks good:
- Task #1 completed
- Following simple architecture
- On track with requirements

No major changes needed at this time.

---COMMIT_MESSAGE---
Architect: Review alignment (cycle 8)
"""


if __name__ == "__main__":
    # Test the API caller
    prompt = "Hello Claude! Please respond with a short test message."
    response = call_claude_api(prompt, max_tokens=100)
    print(f"\nResponse:\n{response}")
