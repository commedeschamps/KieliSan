#!/usr/bin/env python3
"""
Script for auto-reloading the bot when files change.
Just for development purposes, you can run this script instead of main.py to automatically restart the bot on code changes.
Run: python3 scripts/dev.py
"""

import subprocess
import sys
from watchfiles import run_process


def run_bot():
    subprocess.run([sys.executable, "main.py"])


if __name__ == "__main__":
    print("Starting bot in development mode (auto-reload)")
    print("Watching for changes in .py files...")
    print("-" * 50)
    run_process(
        ".",
        target=run_bot,
        watch_filter=lambda change, path: path.endswith(".py"),
    )
