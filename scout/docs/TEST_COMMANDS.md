# Scout V0 - Test Commands Quick Reference

## Run All UI Tests

```bash
cd /Users/andylee/Projects/micro-pe/scout
pytest tests/test_terminal.py tests/test_keyboard.py tests/test_ui_integration.py -v
```

**Expected Output:** 72 tests passing in ~12 seconds

---

## Run Tests with Coverage

```bash
pytest tests/test_terminal.py tests/test_keyboard.py tests/test_ui_integration.py \
  --cov=scout/ui --cov-report=term-missing
```

**Expected Coverage:** 85% overall

---

## Run Specific Test Files

### Terminal Tests Only
```bash
pytest tests/test_terminal.py -v
```
**Expected:** 26 tests passing

### Keyboard Tests Only
```bash
pytest tests/test_keyboard.py -v
```
**Expected:** 23 tests passing

### Integration Tests Only
```bash
pytest tests/test_ui_integration.py -v
```
**Expected:** 23 tests passing

---

## Run Specific Test Classes

### Full UI Pipeline Tests
```bash
pytest tests/test_ui_integration.py::TestFullUIPipeline -v
```

### Keyboard Interaction Tests
```bash
pytest tests/test_ui_integration.py::TestKeyboardInteraction -v
```

### Scrolling Edge Cases
```bash
pytest tests/test_ui_integration.py::TestScrollingEdgeCases -v
```

### Performance Tests
```bash
pytest tests/test_ui_integration.py::TestPerformance -v
```

---

## Run Specific Individual Tests

### Test Scrolling
```bash
pytest tests/test_terminal.py::test_scroll_down -v
```

### Test Export
```bash
pytest tests/test_keyboard.py::TestCharacterKeys::test_e_key_lowercase -v
```

### Test End-to-End Pipeline
```bash
pytest tests/test_ui_integration.py::TestFullUIPipeline::test_full_ui_pipeline_fresh_data -v
```

---

## Run Tests with Different Output Modes

### Quiet Mode (less output)
```bash
pytest tests/test_terminal.py tests/test_keyboard.py tests/test_ui_integration.py -q
```

### Verbose Mode with Short Traceback
```bash
pytest tests/test_terminal.py tests/test_keyboard.py tests/test_ui_integration.py -v --tb=short
```

### Show Only Failed Tests
```bash
pytest tests/test_terminal.py tests/test_keyboard.py tests/test_ui_integration.py --tb=short -x
```

---

## Run All Project Tests

```bash
pytest tests/ -v
```

**Expected:** 146+ tests (includes UI, export, parser, integration, etc.)

---

## Performance Testing

### Time Tests Only
```bash
pytest tests/test_ui_integration.py::TestPerformance -v --durations=10
```

### Profile Slow Tests
```bash
pytest tests/ --durations=0
```

---

## Manual Testing Commands

### Launch Scout with Default Settings
```bash
scout research "HVAC in Los Angeles"
```

### Launch with Specific Options
```bash
scout research "HVAC in Los Angeles" --max-results 500 --no-cache
```

### Launch in No-UI Mode
```bash
scout research "HVAC in Los Angeles" --no-ui
```

### Get Help
```bash
scout --help
scout research --help
```

---

## Debugging Commands

### Run Tests with Print Statements
```bash
pytest tests/test_terminal.py -v -s
```

### Run Tests with PDB Debugger on Failure
```bash
pytest tests/test_terminal.py --pdb
```

### Run Tests with Warnings Displayed
```bash
pytest tests/test_terminal.py -v -W default
```

---

## Continuous Testing

### Watch Mode (requires pytest-watch)
```bash
pip install pytest-watch
ptw tests/test_terminal.py tests/test_keyboard.py tests/test_ui_integration.py -- -v
```

### Run Tests on File Change
```bash
# macOS/Linux
while true; do
  clear
  pytest tests/test_terminal.py tests/test_keyboard.py tests/test_ui_integration.py -v
  sleep 5
done
```

---

## CI/CD Pipeline Commands

### Full Test Suite with Coverage
```bash
pytest tests/ --cov=scout --cov-report=html --cov-report=term
```

### Generate Coverage Badge
```bash
pytest tests/ --cov=scout --cov-report=json
coverage-badge -o docs/coverage.svg
```

### Test in Strict Mode (warnings as errors)
```bash
pytest tests/ -W error
```

---

## Expected Test Results

| Test Suite | Tests | Time | Coverage |
|------------|-------|------|----------|
| Terminal Tests | 26 | ~2s | 80-90% |
| Keyboard Tests | 23 | ~4s | 90-95% |
| Integration Tests | 23 | ~6s | 75-85% |
| **Total UI Tests** | **72** | **~12s** | **85%** |

---

## Troubleshooting

### If Tests Fail:

1. **Check Environment:**
   ```bash
   python --version  # Should be 3.8+
   pip list | grep pytest  # Check pytest is installed
   ```

2. **Reinstall Dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Clear Cache:**
   ```bash
   pytest --cache-clear tests/
   ```

4. **Run Single Failing Test:**
   ```bash
   pytest tests/test_terminal.py::test_scroll_down -v --tb=long
   ```

### If Coverage is Low:

1. **Check Which Lines Missing:**
   ```bash
   pytest tests/ --cov=scout/ui --cov-report=term-missing
   ```

2. **Generate HTML Report:**
   ```bash
   pytest tests/ --cov=scout/ui --cov-report=html
   open htmlcov/index.html
   ```

---

## Quick Test Verification (Before Commit)

```bash
# Run all UI tests with coverage
pytest tests/test_terminal.py tests/test_keyboard.py tests/test_ui_integration.py \
  --cov=scout/ui --cov-report=term -v

# Expected output:
# - 72 passed
# - Coverage >= 85%
# - Time < 15 seconds
```

---

## Links

- Manual Testing Guide: `/Users/andylee/Projects/micro-pe/scout/docs/MANUAL_TESTING_GUIDE.md`
- Integration Summary: `/Users/andylee/Projects/micro-pe/scout/docs/V0_INTEGRATION_SUMMARY.md`
- Test Files:
  - `/Users/andylee/Projects/micro-pe/scout/tests/test_terminal.py`
  - `/Users/andylee/Projects/micro-pe/scout/tests/test_keyboard.py`
  - `/Users/andylee/Projects/micro-pe/scout/tests/test_ui_integration.py`
