#!/usr/bin/env python3
"""
Chinese Subtitle to Anki - Launcher
====================================
Launches the GUI application for converting Chinese subtitles to Anki cards.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run GUI
from gui import main

if __name__ == "__main__":
    print("Starting Chinese Subtitle to Anki GUI...")
    main()
