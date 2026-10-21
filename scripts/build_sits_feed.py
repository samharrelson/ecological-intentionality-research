#!/usr/bin/env python3
"""Build a *sits-only* RSS feed from the curated public Obsidian index.

The Obsidian Home.md "Recent sits" links are the feed allowlist.
Descriptions and full-text HTML come only from already-exported public field notes.
No private vault paths, unindexed notes, or page-edit timestamps are syndicated.
"""
from __future__ import annotations

import argparse
from html import escape
import posixpath
from urllib.parse import quote, unquote, urlsplit
from datetime import date, datetime, time, timezone
from email.utils import format_datetime
from pathlib import Path
import re
import xml.etree.ElementTree as ET

SITE = "https://ecologicalintentionality.org"
FEED = "https://samharrelson.github.io/ecological-intentionality-research/sits.xml"
ATOM = "http://www.w3.org/2005/Atom"
CONTENT = "http://purl.org/rss/1.0/modules/content/"
ET.register_namespace("atom", ATOM)
ET.register_namespace("content", CONTENT)
DATE_PATTERN = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")


def frontmatter(text: str) -> dict[str, str]:
    """Read only simple one-line public metadata; never the note body."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    result = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip().lower() in {"date", "description"}:
            result[key.strip().lower()] = value.strip().strip('"').strip("'")
    return result


def body_without_frontmatter(text: str) -> str:
    """Use the public note body, never its publication-routing YAML metadata."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end >= 0:
            return text[end + 5:].strip()
    return text.strip()


def public_link(url: str) -> str | None:
    """Keep external links and allowlisted public GitHub Markdown references."""
    parsed = urlsplit(url)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return url
    if parsed.scheme or parsed.netloc or url.startswith("/"):
        return None
    decoded = unquote(parsed.path)
    path = posixpath.normpath(posixpath.join("field-notes", decoded))
    if (
        path.startswith(("concepts/", "field-notes/", "project/", "method/"))
        and path.endswith(".md")
        and ".." not in path.split("/")
    ):
        return (
            "https://github.com/samharrelson/ecological-intentionality-research/blob/main/"
            + quote(path, safe="/._-")
            + (("#" + quote(parsed.fragment, safe="-_")) if parsed.fragment else "")
        )
    return None


def inline_html(text: str) -> str:
    """Render basic Markdown without trusting raw HTML or local links."""
    links = []

    def render_link(match):
        label, url = match.group(1), match.group(2)
        if match.group(0).startswith("!"):
            # No remote images or private media in RSS.
            return label
        href = public_link(url)
        if not href:
            return label
        links.append(f'<a href="{escape(href, quote=True)}">{escape(label)}</a>')
        return f"FEEDLINKPLACEHOLDER{len(links) - 1}END"

    text = re.sub(r"!?\[([^\]]+)\]\(([^)\s]+)\)", render_link, text)
    escaped = escape(text)
    escaped = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", escaped)
    for i, value in enumerate(links):
        escaped = escaped.replace(f"FEEDLINKPLACEHOLDER{i}END", value)
    return escaped


def markdown_to_html(text: str) -> str:
    """Render already-public Markdown as reader-friendly, sanitized HTML."""
    lines = body_without_frontmatter(text).splitlines()
    fragments = []
    paragraph = []
    bullets = []
    quoted = []

    def flush_para():
        if paragraph:
            fragments.append("<p>" + inline_html(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    def flush_bullets():
        if bullets:
            fragments.append("<ul>" + "".join("<li>" + inline_html(x) + "</li>" for x in bullets) + "</ul>")
            bullets.clear()

    def flush_quote():
        if quoted:
            fragments.append("<blockquote><p>" + inline_html(" ".join(quoted)) + "</p></blockquote>")
            quoted.clear()

    for raw in lines:
        line = raw.strip()
        if not line:
            flush_para()
            flush_bullets()
            flush_quote()
            continue
        heading = re.match(r"^(#{1,5})\s+(.+)$", line)
        bullet = re.match(r"^[-*]\s+(.+)$", line)
        quote_line = re.match(r"^>\s?(.*)$", line)
        if heading:
            flush_para(); flush_bullets(); flush_quote()
            level = min(len(heading.group(1)) + 1, 6)
            fragments.append(f"<h{level}>" + inline_html(heading.group(2)) + f"</h{level}>")
        elif quote_line:
            flush_para(); flush_bullets()
            quoted.append(quote_line.group(1))
        elif bullet:
            flush_para(); flush_quote()
            bullets.append(bullet.group(1))
        else:
            flush_bullets(); flush_quote()
            paragraph.append(line)

    flush_para(); flush_bullets(); flush_quote()
    return "\n".join(fragments)


def curated_sits(home_text: str) -> list[tuple[str, str]]:
    """Find explicitly linked dated sits in Home's public 'Recent sits' section."""
    section = re.search(r"(?ms)^## Recent sits\s*\n(.*?)(?=^## |\Z)", home_text)
    if not section:
        raise ValueError("No 'Recent sits' section in the public Home index.")
    results = []
    seen = set()
    for line in section.group(1).splitlines():
        if not line.lstrip().startswith("- "):
            continue
        wiki = re.search(r"\[\[([^\]|]+)\|([^\]]+)\]\]", line)
        web = re.search(r"\[([^\]]+)\]\((https://ecologicalintentionality\.org/sits/20\d{2}-\d{2}-\d{2})\)", line)
        if wiki:
            target, label = wiki.groups()
            if not (target.startswith("Public/Tracking/Sits/") or re.match(r"20\d{2}-\d{2}-\d{2} - ", target)):
                continue
            match = DATE_PATTERN.search(target)
        elif web:
            label, target = web.groups()
            match = DATE_PATTERN.search(target)
        else:
            continue
        if not match:
            continue
        day = match.group(1)
        date.fromisoformat(day)
        if day in seen:
            continue
        seen.add(day)
        title = label.split(": ", 1)[1] if ": " in label else label
        results.append((day, title.strip()))
    if not results:
        raise ValueError("No dated public sit links were found in Home.")
    return results


def public_metadata(notes_dir: Path) -> dict[str, dict[str, str]]:
    """Use only exported public notes, never arbitrary vault or note body text."""
    result = {}
    for path in sorted(notes_dir.glob("20??-??-?? - *.md")):
        day_match = DATE_PATTERN.match(path.name)
        if not day_match:
            continue
        day = day_match.group(1)
        metadata = frontmatter(path.read_text(encoding="utf-8"))
        if metadata.get("date") != day or not metadata.get("description"):
            continue
        # Duplicate exported filenames for one date are common while renaming.
        # Their date-specific public permalink is the stable article identity.
        result.setdefault(day, {"date": day, "description": metadata["description"], "body": path.read_text(encoding="utf-8")})
    return result


def build_xml(home_text: str, notes_dir: Path) -> bytes:
    curated = curated_sits(home_text)
    metadata = public_metadata(notes_dir)
    missing = sorted(day for day, _ in curated if day not in metadata)
    if missing:
        raise ValueError("Public Home lists dates without matching exported sit metadata: " + ", ".join(missing))
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "Black Walnut Field Notes | Ecological Intentionality"
    ET.SubElement(channel, "link").text = SITE
    ET.SubElement(channel, "description").text = (
        "Newly curated field sits with a black walnut and related places. "
        "Excludes research-page edits, thinker pages, and private notes."
    )
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, f"{{{ATOM}}}link", href=FEED, rel="self", type="application/rss+xml")
    for day, title in sorted(curated, reverse=True):
        permalink = f"{SITE}/sits/{day}"
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = permalink
        ET.SubElement(item, "guid", isPermaLink="true").text = permalink
        ET.SubElement(item, "description").text = metadata[day]["description"]
        ET.SubElement(item, f"{{{CONTENT}}}encoded").text = markdown_to_html(metadata[day]["body"])
        # Source records a field-sit day, not an exact website publication time.
        # A constant UTC day boundary keeps the item stable during edits.
        stamp = datetime.combine(date.fromisoformat(day), time.min, tzinfo=timezone.utc)
        ET.SubElement(item, "pubDate").text = format_datetime(stamp, usegmt=True)
    ET.indent(root, space="  ")
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="utf-8") + b"\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", required=True, help="Obsidian vault root")
    parser.add_argument("--repo", default=".", help="Public research repo root")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    vault = Path(args.vault).expanduser().resolve()
    repo = Path(args.repo).expanduser().resolve()
    home = vault / "Public/Tracking/Home.md"
    if not home.is_file():
        raise SystemExit("Cannot locate public Home index, refusing to build feed.")
    xml = build_xml(home.read_text(encoding="utf-8"), repo / "field-notes")
    dest = repo / "docs/sits.xml"
    old = dest.read_bytes() if dest.is_file() else None
    if old == xml:
        print("Sit-only RSS unchanged (no new sit or metadata change).")
        return 0
    if args.apply:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(xml)
    print(f"{'Wrote' if args.apply else 'Would write'} {dest} ({len(xml)} bytes, {xml.count(b'<item>')} sits).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
