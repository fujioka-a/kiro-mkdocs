#!/usr/bin/env python3
"""
Simple polling-based watcher for documentation changes.

This script avoids external dependencies by repeatedly scanning the
`docs` directory for changes.  When it detects that a file has been
created, removed, or its modification time has changed, it runs the
validation script.

Usage:
    python tools/watch_docs.py

Press Ctrl+C to stop.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_PATH = PROJECT_ROOT / "docs"
VALIDATE_SCRIPT = PROJECT_ROOT / "tools" / "validate_docs.py"


def build_snapshot(root: Path) -> dict[str, float]:
    """Return a dictionary mapping file paths to last modification times."""
    snapshot: dict[str, float] = {}
    for p in root.rglob("*.md"):
        try:
            snapshot[str(p)] = p.stat().st_mtime
        except FileNotFoundError:
            continue
    return snapshot


def run_validation() -> None:
    """Run the validation script and print the result."""
    result = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip()
    timestamp = time.strftime("%H:%M:%S")
    if result.returncode == 0:
        print(f"[{timestamp}] Validation OK: {output}")
    else:
        print(f"[{timestamp}] Validation errors detected:\n{output}")


def main() -> None:
    if not DOCS_PATH.exists():
        print(f"Docs folder not found: {DOCS_PATH}")
        sys.exit(1)
    print(f"Watching {DOCS_PATH} for changes (polling). Press Ctrl+C to stop.")
    last_snapshot = build_snapshot(DOCS_PATH)
    # Run validation initially
    run_validation()
    try:
        while True:
            time.sleep(1.0)
            current_snapshot = build_snapshot(DOCS_PATH)
            if current_snapshot != last_snapshot:
                run_validation()
                last_snapshot = current_snapshot
    except KeyboardInterrupt:
        print("Stopping watcher...")


if __name__ == "__main__":
    main()