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
            "## Body\nPrivate-looking text should never be used in the summary.\n",
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
        self.assertNotIn("Private-looking text", xml)
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

    def test_index_requires_matching_exported_public_sit(self):
        home = "## Recent sits\n- [[2026-10-22 - Missing|October 22, 2026: Missing]]\n"
        with TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "2026-10-22"):
                feed.build_xml(home, Path(temp))


if __name__ == "__main__":
    unittest.main()
