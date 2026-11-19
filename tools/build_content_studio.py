#!/usr/bin/env python3
"""Package the Content Studio plugin and its connector add-ons.

Kept for the documents that name it. The work is done by tools/build_plugins.py, which packages every suite.
Usage: python3 tools/build_content_studio.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_plugins import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(["content-studio"]))
