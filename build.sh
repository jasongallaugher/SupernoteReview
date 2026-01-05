#!/bin/bash
uv run pyinstaller --onefile --name manta-review --paths src build_entry.py
echo "Build complete. Binary is at dist/manta-review"
