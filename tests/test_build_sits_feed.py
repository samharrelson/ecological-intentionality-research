"""Tests for the public-sits-only RSS feed."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
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


if __name__ == "__main__":
    unittest.main()
