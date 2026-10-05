#!/usr/bin/env python3
"""Fail closed on path/config leaks without blocking ordinary public prose."""

from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SCAN_DIRS = ["field-notes", "concepts", "project", "method"]

# Structural/path-like leak indicators, not ordinary methodological prose.
BLOCKED_PATTERNS = {
    "absolute macOS user path": re.compile(r"/Users/[^/\s]+/", re.I),
    "Daily Notes path": re.compile(r"(?:^|[\s(\[`\"'])Daily Notes/", re.I),
    "private Field Journal path": re.compile(r"(?:^|[\s(\[`\"'])Field Journal/", re.I),
    "CIIS semester path": re.compile(r"(?:^|[\s(\[`\"'])CIIS/(?:Fall|Spring|Summer)\b", re.I),
    "Zotero storage path": re.compile(r"Zotero/storage", re.I),
    "Obsidian config path": re.compile(r"\.obsidian/", re.I),
    "local file URL": re.compile(r"\bfile://", re.I),
    "plugin URL": re.compile(r"\bplugin://", re.I),
}

ALLOWED_EXTS = {".md", ".txt", ".csv", ".json", ".yml", ".yaml"}
failures = []

for dirname in SCAN_DIRS:
    d = ROOT / dirname
    if not d.exists():
        continue

    for p in d.rglob("*"):
        if not p.is_file() or p.name == ".gitkeep":
            continue

        if p.suffix.lower() not in ALLOWED_EXTS:
            failures.append(f"{p.relative_to(ROOT)}: disallowed extension")
            continue

        if p.stat().st_size > 2_000_000:
            failures.append(f"{p.relative_to(ROOT)}: file larger than 2 MB")
            continue

        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"{p.relative_to(ROOT)}: non-UTF-8 content")
            continue

        for label, pattern in BLOCKED_PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{p.relative_to(ROOT)}: {label}")

if failures:
    print("PUBLICATION BLOCKED")
    for item in failures:
        print(" -", item)
    raise SystemExit(1)

print("Privacy guard passed.")
