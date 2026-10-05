#!/usr/bin/env python3
from __future__ import annotations
import argparse
import re
from pathlib import Path

ALLOWED_ROOT = Path("Public/Tracking")
BLOCKED_PATH_MARKERS = (
    "Daily Notes", "Field Journal", "CIIS", "Zotero",
    "People", "Media", "Private", ".obsidian",
)
EXACT_FILES = {
    Path("Public/Tracking/Where the Inquiry Stands.md"): Path("project/where-the-inquiry-stands.md"),
    Path("Public/Tracking/Sources & Reading.md"): Path("project/sources-and-reading.md"),
    Path("Public/Tracking/About the Practice.md"): Path("method/about-the-practice.md"),
    Path("Public/Tracking/Sit Template.md"): Path("method/sit-template.md"),
}
FOLDER_MAP = {
    Path("Public/Tracking/Sits"): Path("field-notes"),
    Path("Public/Tracking/Concepts"): Path("concepts"),
}

def assert_safe_source(rel: Path) -> None:
    rel_s = rel.as_posix()
    if not rel_s.startswith(ALLOWED_ROOT.as_posix() + "/"):
        raise RuntimeError(f"Refusing non-public source path: {rel}")
    for marker in BLOCKED_PATH_MARKERS:
        if marker.lower() in rel_s.lower():
            raise RuntimeError(f"Blocked source marker {marker!r} in {rel}")

def strip_publish_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    body = text[end + 5:]
    fm = text[4:end].splitlines()
    kept = []
    for line in fm:
        key = line.split(":", 1)[0].strip().lower() if ":" in line else ""
        if key in {"permalink", "publish", "published", "share", "cssclasses"}:
            continue
        kept.append(line)
    if not kept:
        return body.lstrip()
    return "---\n" + "\n".join(kept) + "\n---\n" + body.lstrip()

def convert_wikilinks(text: str) -> str:
    text = re.sub(
        r'!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]',
        lambda m: f"*{(m.group(2) or Path(m.group(1)).stem).strip()}*",
        text,
    )
    def repl(m):
        target = m.group(1).strip()
        alias = (m.group(2) or Path(target).stem).strip()
        return alias
    return re.sub(r'\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]', repl, text)

def normalize(text: str) -> str:
    return convert_wikilinks(strip_publish_frontmatter(text)).rstrip() + "\n"

def iter_sources(vault: Path):
    for rel, dest in EXACT_FILES.items():
        src = vault / rel
        if src.exists():
            assert_safe_source(rel)
            yield src, dest
    for source_rel, dest_dir in FOLDER_MAP.items():
        src_dir = vault / source_rel
        if not src_dir.exists():
            continue
        for src in sorted(src_dir.glob("*.md")):
            rel = src.relative_to(vault)
            assert_safe_source(rel)
            yield src, dest_dir / src.name

def write_if_changed(src: Path, dest: Path, apply: bool) -> bool:
    new_text = normalize(src.read_text(encoding="utf-8"))
    old_text = dest.read_text(encoding="utf-8") if dest.exists() else None
    if old_text == new_text:
        return False
    print(("UPDATE" if dest.exists() else "ADD").ljust(7), dest)
    if apply:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(new_text, encoding="utf-8")
    return True

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--vault", required=True)
    p.add_argument("--repo", default=".")
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    repo = Path(args.repo).expanduser().resolve()

    if not (vault / "Public" / "Tracking").exists():
        raise SystemExit(f"Public/Tracking not found under vault: {vault}")

    changed = 0
    for src, dest_rel in iter_sources(vault):
        if write_if_changed(src, repo / dest_rel, args.apply):
            changed += 1

    print()
    print(
        f"Applied {changed} changed file(s)." if args.apply
        else f"Dry run: {changed} file(s) would change. Re-run with --apply to write."
    )
    print("No files were deleted.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
