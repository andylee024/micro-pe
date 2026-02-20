#!/usr/bin/env python
"""Demo script to test the terminal UI"""

from scout.ui.terminal import ScoutTerminal


def main():
    """Run the terminal UI demo"""
    terminal = ScoutTerminal(
        industry="HVAC",
        location="Los Angeles",
        use_cache=True,
        max_results=500
    )

    terminal.run()


if __name__ == "__main__":
    main()
