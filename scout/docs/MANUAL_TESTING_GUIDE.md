# Scout V0 - Manual Testing Guide

This guide provides step-by-step manual testing scenarios for the Scout Terminal UI.

## Prerequisites

1. Ensure you have a valid `GOOGLE_MAPS_API_KEY` in your `.env` file
2. Install Scout: `pip install -e .`
3. Verify installation: `scout --help`

## Test Scenario 1: Happy Path - Full Workflow

**Objective:** Test complete end-to-end flow from query to export

### Steps:

1. **Launch Scout with a real query:**
   ```bash
   scout research "HVAC in Los Angeles"
   ```

2. **Verify Initial Display:**
   - [ ] Terminal UI launches within 2 seconds
   - [ ] Header shows "SCOUT - Market Research" with query "HVAC in Los Angeles"
   - [ ] Status bar shows "Searching Google Maps..."
   - [ ] Progress panel displays with spinner

3. **Verify Data Loaded:**
   - [ ] After 5-15 seconds, business table appears
   - [ ] Table shows business names, phone numbers, websites, and addresses
   - [ ] Status bar shows "Ready" with count (e.g., "500 businesses found")
   - [ ] Footer shows keyboard shortcuts: [↑↓] Scroll [E]xport CSV [Q]uit [H]elp

4. **Test Scrolling:**
   - [ ] Press ↓ (down arrow) - table scrolls down by 1 row
   - [ ] Press ↑ (up arrow) - table scrolls up by 1 row
   - [ ] Press Page Down - scrolls down 20 rows
   - [ ] Press Page Up - scrolls up 20 rows
   - [ ] Press Home - jumps to top of list
   - [ ] Press End - jumps to bottom of list

5. **Test Help Panel:**
   - [ ] Press `H` - help panel appears showing keyboard shortcuts
   - [ ] Press `H` again - help panel disappears, business table reappears

6. **Test Export:**
   - [ ] Press `E` - status shows "Exporting to CSV..."
   - [ ] After 1-2 seconds, status shows "✅ Exported 500 businesses to hvac_los_angeles_YYYY-MM-DD.csv"
   - [ ] Status returns to "Ready" after 2 seconds
   - [ ] Check `outputs/` directory - CSV file exists
   - [ ] Open CSV file - verify data is correct with headers: name, address, phone, website, category

7. **Test Quit:**
   - [ ] Press `Q` - terminal exits gracefully
   - [ ] No error messages displayed

**Expected Result:** All steps complete successfully with no errors.

---

## Test Scenario 2: Cache Hit - Second Run

**Objective:** Test that cached data loads instantly

### Steps:

1. **First Run (Fresh Data):**
   ```bash
   scout research "HVAC in San Diego"
   ```
   - [ ] Wait for data to load (5-15 seconds)
   - [ ] Verify data appears
   - [ ] Note the timestamp in status bar

2. **Second Run (Cached Data):**
   ```bash
   scout research "HVAC in San Diego"
   ```
   - [ ] Data loads instantly (<1 second)
   - [ ] Status bar shows "Cached for 90 days" in yellow
   - [ ] Business count matches first run
   - [ ] All businesses displayed correctly

3. **Test Refresh:**
   - [ ] Press `R` - forces fresh data fetch
   - [ ] Status shows "Refreshing data..."
   - [ ] Data reloads from API (5-15 seconds)
   - [ ] Status shows "Fresh data" (green) instead of "Cached"

**Expected Result:** Cached run is instant; refresh forces new API call.

---

## Test Scenario 3: Scrolling Performance - 500 Businesses

**Objective:** Test UI remains responsive with large dataset

### Steps:

1. **Load Large Dataset:**
   ```bash
   scout research "restaurants in New York"
   ```
   - [ ] Wait for data to load
   - [ ] Verify 500+ businesses loaded

2. **Scroll Through All Data:**
   - [ ] Hold down ↓ arrow key for 5 seconds
   - [ ] UI remains responsive (no lag)
   - [ ] Scroll position updates smoothly
   - [ ] No crashes or freezes

3. **Jump to End:**
   - [ ] Press End key
   - [ ] Instantly jumps to bottom
   - [ ] Last businesses visible

4. **Jump to Top:**
   - [ ] Press Home key
   - [ ] Instantly jumps to top
   - [ ] First businesses visible

5. **Rapid Scrolling:**
   - [ ] Rapidly press ↓ 50 times
   - [ ] No crashes
   - [ ] All keypresses registered

**Expected Result:** UI remains smooth and responsive with 500+ businesses.

---

## Test Scenario 4: Export Verification

**Objective:** Verify CSV export is complete and accurate

### Steps:

1. **Load Data and Export:**
   ```bash
   scout research "car wash in Miami"
   ```
   - [ ] Wait for data to load
   - [ ] Press `E` to export

2. **Verify CSV File:**
   - [ ] Navigate to `outputs/` directory
   - [ ] File exists: `car_wash_miami_YYYY-MM-DD.csv`
   - [ ] Open in Excel/Numbers/Google Sheets

3. **Check CSV Contents:**
   - [ ] Headers present: name, address, phone, website, category
   - [ ] Row count matches business count in terminal
   - [ ] No blank rows (except for missing data → "N/A")
   - [ ] Special characters (accents, symbols) display correctly
   - [ ] Phone numbers formatted correctly
   - [ ] Websites are valid URLs

4. **Multiple Exports:**
   - [ ] Press `E` again (still in terminal)
   - [ ] File is overwritten (same filename)
   - [ ] New export has same data

**Expected Result:** CSV export is complete, accurate, and well-formatted.

---

## Test Scenario 5: Error Handling

**Objective:** Test graceful error handling

### Test 5A: Invalid API Key

1. **Setup:**
   - Temporarily rename `.env` to `.env.backup`
   - Create new `.env` with invalid key: `GOOGLE_MAPS_API_KEY=invalid_key`

2. **Run Scout:**
   ```bash
   scout research "HVAC in Boston"
   ```
   - [ ] Error message appears: "❌ Error: Google Maps authentication failed"
   - [ ] Helpful message: "Please check your GOOGLE_MAPS_API_KEY in .env file"
   - [ ] No stack trace shown to user
   - [ ] Clean exit (no crash)

3. **Cleanup:**
   - Restore original `.env`

### Test 5B: Network Disconnection

1. **Setup:**
   - Disconnect from internet (turn off WiFi)

2. **Run Scout:**
   ```bash
   scout research "HVAC in Seattle"
   ```
   - [ ] Error message: "❌ Error: Network connection failed"
   - [ ] Helpful message: "Please check your internet connection and try again"
   - [ ] No crash
   - [ ] Clean exit

3. **Reconnect:**
   - Turn WiFi back on
   - [ ] Run same command - works correctly

### Test 5C: Invalid Query

1. **Run with Empty Industry:**
   ```bash
   scout research "in Los Angeles"
   ```
   - [ ] Error: "❌ Error: Industry cannot be empty"
   - [ ] Clean exit

2. **Run with Empty Location:**
   ```bash
   scout research "HVAC in"
   ```
   - [ ] Error: "❌ Error: Location cannot be empty"
   - [ ] Clean exit

3. **Run with Minimal Query:**
   ```bash
   scout research "a in b"
   ```
   - [ ] Should work (minimal valid query)

**Expected Result:** All errors handled gracefully with helpful messages.

---

## Test Scenario 6: No-UI Mode

**Objective:** Test simple CLI output mode

### Steps:

1. **Run with --no-ui flag:**
   ```bash
   scout research "HVAC in Denver" --no-ui
   ```
   - [ ] No terminal UI launches
   - [ ] Simple text output to console
   - [ ] Shows "📊 Scout Market Research" header
   - [ ] Shows query details (industry, location)
   - [ ] Shows "🔍 Searching Google Maps..."
   - [ ] Shows "✅ Found X businesses"
   - [ ] Lists top 10 businesses with ratings
   - [ ] Shows cache message
   - [ ] Clean exit

2. **Compare with UI Mode:**
   ```bash
   scout research "HVAC in Denver"
   ```
   - [ ] Terminal UI launches normally
   - [ ] Both modes access same data/cache

**Expected Result:** No-UI mode works as simple alternative to full terminal UI.

---

## Test Scenario 7: Keyboard Shortcuts Reference

**Objective:** Verify all keyboard shortcuts work

### Steps:

1. **Launch Scout:**
   ```bash
   scout research "HVAC in Phoenix"
   ```

2. **Test Each Shortcut:**

   | Key | Expected Action | ✓ |
   |-----|----------------|---|
   | ↑ | Scroll up 1 row | [ ] |
   | ↓ | Scroll down 1 row | [ ] |
   | Page Up | Scroll up 20 rows | [ ] |
   | Page Down | Scroll down 20 rows | [ ] |
   | Home | Jump to top | [ ] |
   | End | Jump to bottom | [ ] |
   | E | Export to CSV | [ ] |
   | e | Export to CSV (lowercase works) | [ ] |
   | Q | Quit application | [ ] |
   | q | Quit application (lowercase works) | [ ] |
   | H | Toggle help panel | [ ] |
   | h | Toggle help panel (lowercase works) | [ ] |
   | R | Refresh data (bypass cache) | [ ] |
   | r | Refresh data (lowercase works) | [ ] |
   | Ctrl+C | Graceful exit | [ ] |

**Expected Result:** All keyboard shortcuts work as documented.

---

## Performance Benchmarks

Record timing for each scenario:

| Scenario | Target | Actual | Pass? |
|----------|--------|--------|-------|
| UI Launch Time | <2 seconds | _____ | [ ] |
| Cached Query Load | <1 second | _____ | [ ] |
| Fresh Query Load | 5-15 seconds | _____ | [ ] |
| CSV Export (500 rows) | <3 seconds | _____ | [ ] |
| Scroll Response | Instant | _____ | [ ] |
| Help Toggle | Instant | _____ | [ ] |

---

## Bug Report Template

If you encounter any issues, report them with this template:

```
**Bug Title:** [Short description]

**Scenario:** [Which test scenario]

**Steps to Reproduce:**
1.
2.
3.

**Expected Result:**

**Actual Result:**

**Screenshots/Logs:**

**Environment:**
- OS: [macOS/Linux/Windows]
- Python Version:
- Scout Version:
```

---

## Sign-Off Checklist

Before releasing Scout V0, all scenarios must pass:

- [ ] Scenario 1: Happy Path - Full Workflow
- [ ] Scenario 2: Cache Hit - Second Run
- [ ] Scenario 3: Scrolling Performance - 500 Businesses
- [ ] Scenario 4: Export Verification
- [ ] Scenario 5: Error Handling (A, B, C)
- [ ] Scenario 6: No-UI Mode
- [ ] Scenario 7: Keyboard Shortcuts Reference
- [ ] All Performance Benchmarks Met
- [ ] No critical bugs found
- [ ] Documentation reviewed

**Tested By:** _______________ **Date:** _______________

**Approved By:** _______________ **Date:** _______________
