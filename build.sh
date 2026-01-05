#!/bin/bash
uv run pyinstaller --onefile --name sn-review --paths src build_entry.py
echo "Build complete. Binary is at dist/sn-review"
