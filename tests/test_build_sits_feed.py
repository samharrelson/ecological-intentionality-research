"""Tests for the public-sits-only RSS feed."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_sits_feed", ROOT / "scripts/build_sits_feed.py")
feed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feed)


class SitFeedTests(unittest.TestCase):
    def make_sit(self, directory, date, name, description):
        p = directory / f"{date} - {name}.md"
        p.write_text(
            f"---\ndate: {date}\ndescription: {description}\nstatus: draft\n---\n"
            "## Field Notes\nA public observation that belongs in the full text.\n\n"
            "## Reflection\nA thoughtful distinction.\n",
            encoding="utf-8"
        )

    def test_only_curated_index_sits_become_entries(self):
        home = (
            "## Recent sits\n"
            "- [[Public/Tracking/Sits/2026-10-21 - A Shared Morning|October 21, 2026: A Shared Morning]]\n"
            "- [October 16, 2026: No Line on the Horizon](https://ecologicalintentionality.org/sits/2026-10-16)\n"
            "## Threads\n"
            "- [[2026-10-17 - Excluded|Not a sit index entry]]\n"
        )
        with TemporaryDirectory() as temp:
            d = Path(temp)
            self.make_sit(d, "2026-10-21", "A Shared Morning", "A short day beside the walnut.")
            self.make_sit(d, "2026-10-16", "No Line on the Horizon", "A coastal sit.")
            self.make_sit(d, "2026-10-16", "No Line on the Horizon copy", "A coastal sit.")
            self.make_sit(d, "2026-10-17", "Unindexed Note", "Not published.")
            xml = feed.build_xml(home, d).decode()
        root = ET.fromstring(xml)
        items = root.findall("./channel/item")
        self.assertEqual(len(items), 2)
        self.assertEqual([x.findtext("title") for x in items], ["A Shared Morning", "No Line on the Horizon"])
        self.assertEqual(items[0].findtext("guid"), "https://ecologicalintentionality.org/sits/2026-10-21")
        self.assertEqual(items[0].findtext("description"), "A short day beside the walnut.")
        encoded = items[0].findtext(f"{{{feed.CONTENT}}}encoded")
        self.assertIn("<h3>Field Notes</h3>", encoded)
        self.assertIn("A public observation that belongs in the full text.", encoded)
        self.assertIn("<h3>Reflection</h3>", encoded)
        self.assertNotIn("status: draft", xml)
        self.assertNotIn("2026-10-17", xml)
        self.assertNotIn("Public/Tracking", xml)

    def test_existing_sit_edits_do_not_create_new_feed_items(self):
        home = "## Recent sits\n- [[2026-10-21 - A Shared Morning|October 21, 2026: A Shared Morning]]\n"
        with TemporaryDirectory() as temp:
            d = Path(temp)
            self.make_sit(d, "2026-10-21", "A Shared Morning", "Brief description.")
            first = ET.fromstring(feed.build_xml(home, d)).find("./channel/item")
            self.make_sit(d, "2026-10-21", "A Shared Morning", "Revised description.")
            second = ET.fromstring(feed.build_xml(home, d)).find("./channel/item")
            self.assertEqual(first.findtext("guid"), second.findtext("guid"))
            self.assertEqual(first.findtext("pubDate"), second.findtext("pubDate"))
            self.assertEqual(second.findtext("description"), "Revised description.")

    def test_html_escapes_raw_markup_and_restricts_links(self):
        markdown = (
            "---\ndate: 2026-10-21\ndescription: Shown only in preview.\n---\n"
            "## Research Connection\n"
            "A **strong** idea, and *a tentative* claim. "
            "[Husserl](../concepts/Husserl.md) "
            "[website](https://ecologicalintentionality.org/) "
            "[private](../private/something.md) "
            "<script>alert('bad')</script>\n\n"
            "> What do I actually know?\n\n"
            "- Observation\n- Inference\n\n"
            "![secret](file:///Users/test/private.png)\n"
        )
        rendered = feed.markdown_to_html(markdown)
        self.assertIn("<h3>Research Connection</h3>", rendered)
        self.assertIn("<strong>strong</strong>", rendered)
        self.assertIn("<em>a tentative</em>", rendered)
        self.assertIn("<blockquote>", rendered)
        self.assertIn("<ul>", rendered)
        self.assertIn("github.com/samharrelson/ecological-intentionality-research/blob/main/concepts/Husserl.md", rendered)
        self.assertIn('href="https://ecologicalintentionality.org/"', rendered)
        self.assertNotIn("../private", rendered)
        self.assertNotIn("file://", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("status: draft", rendered)

    def test_index_requires_matching_exported_public_sit(self):
        home = "## Recent sits\n- [[2026-10-22 - Missing|October 22, 2026: Missing]]\n"
        with TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "2026-10-22"):
                feed.build_xml(home, Path(temp))

    def test_archive_preferred_over_short_home_preserves_complete_feed(self):
        november = [
            f"- [[Public/Tracking/Sits/2026-11-{day} - A Sit|November {day}, 2026: A Sit]]\n"
            for day in (24, 23, 22)
        ]
        october = "- [October 16, 2026: A Coastal Sit](https://ecologicalintentionality.org/sits/2026-10-16)\n"
        old_home = "## Recent sits\n" + "".join(november) + october
        archive = "## All sits\n\n### November 2026\n" + "".join(november) + "\n### October 2026\n" + october
        with TemporaryDirectory() as temp:
            vault = Path(temp) / "vault"
            public = vault / "Public/Tracking"
            public.mkdir(parents=True)
            (public / "Home.md").write_text("## Recent sits\n" + "".join(november), encoding="utf-8")
            (public / "Field Notes.md").write_text(archive, encoding="utf-8")
            notes = Path(temp) / "field-notes"
            notes.mkdir()
            for day in (24, 23, 22):
                self.make_sit(notes, f"2026-11-{day}", "A Sit", "A public sit.")
            self.make_sit(notes, "2026-10-16", "A Coastal Sit", "A coastal sit.")
            actual = feed.build_xml(feed.read_public_index(vault), notes)
            self.assertEqual(len(ET.fromstring(actual).findall("./channel/item")), 4)
            self.assertEqual(actual, feed.build_xml(old_home, notes))

    def test_home_fallback_when_archive_is_absent(self):
        home = "## Recent sits\n- [[2026-10-21 - A Shared Morning|October 21, 2026: A Shared Morning]]\n"
        with TemporaryDirectory() as temp:
            vault = Path(temp)
            public = vault / "Public/Tracking"
            public.mkdir(parents=True)
            (public / "Home.md").write_text(home, encoding="utf-8")
            self.assertEqual(feed.curated_sits(feed.read_public_index(vault)), [("2026-10-21", "A Shared Morning")])

    def test_existing_invalid_archive_never_falls_back_to_home(self):
        home = "## Recent sits\n- [[2026-10-21 - A Shared Morning|October 21, 2026: A Shared Morning]]\n"
        invalid_archives = (
            "",
            "## Unrelated section\n- [[2026-10-21 - A Shared Morning|October 21, 2026: A Shared Morning]]\n",
            "## All sits\nNo published sits listed.\n",
            "## All sits\n- [[Private/2026-10-21 - A Private Sit|October 21, 2026: Private]]\n",
        )
        with TemporaryDirectory() as temp:
            vault = Path(temp)
            public = vault / "Public/Tracking"
            public.mkdir(parents=True)
            (public / "Home.md").write_text(home, encoding="utf-8")
            for archive in invalid_archives:
                with self.subTest(archive=archive):
                    (public / "Field Notes.md").write_text(archive, encoding="utf-8")
                    with self.assertRaises(ValueError):
                        feed.curated_sits(feed.read_public_index(vault))

    def test_partial_migration_cannot_overwrite_existing_feed_history(self):
        links = [
            f"- [[2026-11-{day} - A Sit|November {day}, 2026: A Sit]]\n"
            for day in (24, 23, 22, 21)
        ]
        with TemporaryDirectory() as temp:
            vault = Path(temp) / "vault"
            public = vault / "Public/Tracking"
            public.mkdir(parents=True)
            # Home has already been shortened, but the archive has not arrived.
            (public / "Home.md").write_text("## Recent sits\n" + "".join(links[:3]), encoding="utf-8")
            repo = Path(temp) / "repo"
            notes = repo / "field-notes"
            notes.mkdir(parents=True)
            for day in (24, 23, 22, 21):
                self.make_sit(notes, f"2026-11-{day}", "A Sit", "A public sit.")
            dest = repo / "docs/sits.xml"
            dest.parent.mkdir()
            old = feed.build_xml("## Recent sits\n" + "".join(links), notes)
            dest.write_bytes(old)
            with patch("sys.argv", ["build_sits_feed.py", "--vault", str(vault), "--repo", str(repo), "--apply"]):
                with self.assertRaisesRegex(ValueError, "Feed would remove existing sits"):
                    feed.main()
            self.assertEqual(dest.read_bytes(), old)


if __name__ == "__main__":
    unittest.main()
