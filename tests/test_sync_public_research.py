"""Regression tests for the guarded Obsidian-to-GitHub exporter."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "sync_public_research", ROOT / "scripts" / "sync_public_research.py"
)
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)

PAIRS = [
    (Path("unused"), Path("Public/Tracking/Where the Inquiry Stands.md"), Path("project/where-the-inquiry-stands.md")),
    (Path("unused"), Path("Public/Tracking/How the Inquiry Developed.md"), Path("project/how-the-inquiry-developed.md")),
]


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.full, self.titles = exporter.build_public_index(PAIRS)
        self.target = Path("project/where-the-inquiry-stands.md")

    def render(self, source):
        return exporter.normalize(source, self.target, self.full, self.titles)[0]

    def test_archive_is_explicitly_allowlisted(self):
        self.assertEqual(
            exporter.EXACT_FILES[Path("Public/Tracking/How the Inquiry Developed.md")],
            Path("project/how-the-inquiry-developed.md"),
        )

    def test_same_page_navigation_and_cross_page_links(self):
        result = self.render(
            "[[#The two questions|Two questions]] and "
            "[[How the Inquiry Developed|research history]]"
        )
        self.assertIn("[Two questions](#the-two-questions)", result)
        self.assertIn("[research history](how-the-inquiry-developed.md)", result)

    def test_audio_link_and_public_transcript_without_asset_path(self):
        result = self.render(
            "![[" + "walnut-audio-sample.mp4" + "]]\n\n"
            "> [!note]- Read the transcript (lightly edited)\n"
            "> Good morning.\n>\n> There are two questions.\n\n"
        )
        self.assertIn("https://ecologicalintentionality.org/inquiry#hear-the-practice", result)
        self.assertIn("<details>", result)
        self.assertIn("<summary>Read the transcript (lightly edited)</summary>", result)
        self.assertIn("There are two questions.", result)
        self.assertNotIn("walnut-audio-sample.mp4", result)
        self.assertNotIn("[!note]", result)

    def test_image_and_private_link_remain_safe(self):
        result = self.render(
            "![[Media/walnut-photo.jpg|480]]\n"
            "[[CIIS/Fall 2026 (Comps 2)/Secret Working Note|private reference]]\n"
        )
        self.assertIn("Photograph available on the", result)
        self.assertNotIn("Media/walnut-photo.jpg", result)
        self.assertIn("private reference", result)
        self.assertNotIn("Secret Working Note", result)
        self.assertNotIn("CIIS/", result)


if __name__ == "__main__":
    unittest.main()
