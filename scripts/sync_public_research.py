#!/usr/bin/env python3
"""
Conservative one-way exporter from an Obsidian public layer to this repository.

Default behavior is DRY RUN. Pass --apply to write files.

Privacy rule:
- The script only reads an explicit allowlist under Public/Tracking.
- Wikilinks become clickable only when the target is also in that allowlist.
- Unresolved or non-public wikilinks degrade to plain text, so private vault
  structure is not exposed through generated GitHub links.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from urllib.parse import quote

ALLOWED_ROOT = Path("Public/Tracking")

BLOCKED_PATH_MARKERS = (
    "Daily Notes",
    "Field Journal",
    "CIIS",
    "Zotero",
    "People",
    "Media",
    "Private",
    ".obsidian",
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
    """Keep descriptive YAML while dropping website-routing/publish-only keys."""
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


def iter_source_pairs(vault: Path):
    """Yield (source_path, source_relative_path, repo_destination_relative_path)."""
    for rel, dest in EXACT_FILES.items():
        src = vault / rel
        if src.exists():
            assert_safe_source(rel)
            yield src, rel, dest

    for source_rel, dest_dir in FOLDER_MAP.items():
        src_dir = vault / source_rel
        if not src_dir.exists():
            continue
        for src in sorted(src_dir.glob("*.md")):
            rel = src.relative_to(vault)
            assert_safe_source(rel)
            yield src, rel, dest_dir / src.name


def normalize_wiki_target(target: str) -> tuple[str, str | None]:
    """
    Return (note_target, heading).
    Block references are intentionally not reproduced on GitHub.
    """
    target = target.strip()
    heading = None

    if "#" in target:
        target, heading = target.split("#", 1)

    if "^" in target:
        target = target.split("^", 1)[0]

    target = target.strip()
    if target.lower().endswith(".md"):
        target = target[:-3]

    return target, heading.strip() if heading else None


def github_anchor(heading: str) -> str:
    """
    Approximate GitHub's heading slug for ordinary Markdown headings.
    Good for normal prose headings; unusual punctuation may still fall back
    to linking the note rather than relying on the fragment.
    """
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE)
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s.strip("-")


def build_public_index(pairs):
    """
    Build only from exportable public sources.

    Returns:
      by_full_target: normalized vault-relative target -> repo destination
      by_title: unique lowercase filename stem -> repo destination
    """
    by_full_target = {}
    title_candidates = {}

    for _src, source_rel, dest_rel in pairs:
        source_no_ext = source_rel.with_suffix("").as_posix()
        by_full_target[source_no_ext.lower()] = dest_rel

        title = source_rel.stem.strip().lower()
        title_candidates.setdefault(title, []).append(dest_rel)

    by_title = {
        title: dests[0]
        for title, dests in title_candidates.items()
        if len(dests) == 1
    }
    return by_full_target, by_title


def resolve_public_target(target: str, by_full_target, by_title):
    note_target, heading = normalize_wiki_target(target)

    # Explicit vault path.
    explicit = note_target.replace("\\", "/").strip("/")
    if explicit.lower() in by_full_target:
        return by_full_target[explicit.lower()], heading

    # Some public notes use Public/Tracking/... paths without extension.
    prefixed = f"Public/Tracking/{explicit}".lower()
    if prefixed in by_full_target:
        return by_full_target[prefixed], heading

    # Short Obsidian link by note title.
    title = Path(note_target).name.strip().lower()
    if title in by_title:
        return by_title[title], heading

    return None, heading


def relative_markdown_link(current_dest: Path, target_dest: Path, heading: str | None) -> str:
    rel = os.path.relpath(target_dest, start=current_dest.parent).replace(os.sep, "/")
    href = quote(rel, safe="/._-()")
    if heading:
        anchor = github_anchor(heading)
        if anchor:
            href += "#" + quote(anchor, safe="-_")
    return href


def convert_wikilinks(text: str, current_dest: Path, by_full_target, by_title):
    """
    Convert only known public wikilinks to GitHub-relative Markdown links.
    Anything else becomes readable plain text, not a link to private structure.
    """
    converted = 0
    flattened = 0

    # Embedded Obsidian assets are not mirrored into this repo.
    # Preserve readable alt/caption text without exposing a private path.
    def embed_repl(match):
        nonlocal flattened
        target = match.group(1).strip()
        alias = (match.group(2) or Path(target).stem).strip()
        flattened += 1
        return f"*{alias}*"

    text = re.sub(r'!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', embed_repl, text)

    def link_repl(match):
        nonlocal converted, flattened
        raw_target = match.group(1).strip()
        alias = match.group(2)

        note_target, _heading = normalize_wiki_target(raw_target)
        label = (alias or Path(note_target).name).strip()

        resolved, heading = resolve_public_target(raw_target, by_full_target, by_title)
        if resolved is None:
            flattened += 1
            return label

        converted += 1
        href = relative_markdown_link(current_dest, resolved, heading)
        return f"[{label}]({href})"

    text = re.sub(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', link_repl, text)
    return text, converted, flattened


def normalize(text: str, current_dest: Path, by_full_target, by_title):
    text = strip_publish_frontmatter(text)
    text, converted, flattened = convert_wikilinks(
        text, current_dest, by_full_target, by_title
    )
    return text.rstrip() + "\n", converted, flattened


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--vault", required=True, help="Path to the Obsidian vault root")
    p.add_argument("--repo", default=".", help="Path to repository root")
    p.add_argument("--apply", action="store_true", help="Actually write changes")
    args = p.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    repo = Path(args.repo).expanduser().resolve()

    if not (vault / "Public" / "Tracking").exists():
        raise SystemExit(f"Public/Tracking not found under vault: {vault}")

    pairs = list(iter_source_pairs(vault))
    by_full_target, by_title = build_public_index(pairs)

    changed = 0
    total_converted = 0
    total_flattened = 0

    for src, _source_rel, dest_rel in pairs:
        dest = repo / dest_rel
        new_text, converted, flattened = normalize(
            src.read_text(encoding="utf-8"),
            dest_rel,
            by_full_target,
            by_title,
        )
        old_text = dest.read_text(encoding="utf-8") if dest.exists() else None

        total_converted += converted
        total_flattened += flattened

        if old_text == new_text:
            continue

        action = "UPDATE" if dest.exists() else "ADD"
        print(f"{action:6} {dest}")

        if args.apply:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(new_text, encoding="utf-8")

        changed += 1

    print()
    if args.apply:
        print(f"Applied {changed} changed file(s).")
    else:
        print(f"Dry run: {changed} file(s) would change. Re-run with --apply to write.")

    print(f"Converted {total_converted} known public wikilink(s) to GitHub links.")
    print(f"Flattened {total_flattened} embedded/unresolved/non-public wikilink(s) to plain text.")
    print("No files were deleted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
