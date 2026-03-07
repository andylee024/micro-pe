# Hex UI Exploration Artifacts

This folder stores visual captures of the currently runnable Scout product surface (CLI).

## Screenshots

- `screenshots/scout-cli-help.png`  
  Command: `scout --help`  
  Purpose: command surface and available subcommands.

- `screenshots/scout-cli-run-hvac.png`  
  Command: `scout run "HVAC businesses in Los Angeles"`  
  Purpose: end-to-end run output with per-source coverage/status rows.

- `screenshots/scout-cli-run-carwash.png`  
  Command: `scout run "Car wash businesses in Houston"`  
  Purpose: second market run showing consistent output shape across inputs.

## Notes

- These captures are product-state evidence for PR review.
- The runs in this environment show source failures because required external credentials/runtime deps are not configured (`GOOGLE_MAPS_API_KEY`, Selenium/BizBuySell runtime deps).
