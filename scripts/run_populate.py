#!/usr/bin/env python3
"""
Simple runner for the population scripts
"""

import sys
import os

# Add the parent directory to the path to import from project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.populate_deaf_insurance import run as run_insurance

if __name__ == "__main__":
    print("Populating insurance data...")
    run_insurance()
    print("Done!")