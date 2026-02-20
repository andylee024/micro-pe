#!/usr/bin/env python3
"""Test the exact example usage from the task requirements"""

from rich.console import Console
from scout.ui.components import *

console = Console()

# Example usage from task requirements
businesses = [
    {"name": "Cool Air", "phone": "555-0100", "website": "cool.com", "address": "123 Main St"},
    {"name": "Premier Climate", "phone": "555-0200", "website": "premier.com", "address": "456 Oak Ave"},
    {"name": "SoCal Heating", "phone": "555-0300", "website": "socal.com", "address": "789 Elm St"},
]

console.print("\n[bold cyan]Testing Example Usage from Task Requirements[/bold cyan]\n")

# Create components as specified in the task
header = create_header("HVAC in Los Angeles", "HVAC", "Los Angeles")
table = create_business_table(businesses, offset=0, limit=20)
status = create_status_bar(len(businesses), cached=True)

# Create layout and display
layout = create_layout(header, table, status)
console.print(layout)

console.print("\n[bold green]✓ Example usage works perfectly![/bold green]\n")
