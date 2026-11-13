"""Regression tests for the guarded Obsidian-to-GitHub exporter."""
import importlib.util
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

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

    def test_essays_are_explicitly_allowlisted_not_a_whole_folder(self):
        self.assertNotIn(Path("Public/Tracking/Essays"), exporter.FOLDER_MAP)
        self.assertEqual(
            exporter.EXACT_FILES[Path("Public/Tracking/Essays/Essays.md")],
            Path("essays/README.md"),
        )
        self.assertEqual(
            exporter.EXACT_FILES[Path("Public/Tracking/Essays/Whose Good?.md")],
            Path("essays/whose-good.md"),
        )

    def test_essay_links_preserved_when_filename_shortens(self):
        cases = (
            "Public/Tracking/Essays/Whose Good - Ecological Intentionality and the Formation of Practical Purpose.md",
            "Public/Tracking/Essays/Whose Good.md",
            "Public/Tracking/Essays/Whose Good?.md",
        )
        for relative in cases:
            with TemporaryDirectory() as tmp:
                vault = Path(tmp)
                (vault / relative).parent.mkdir(parents=True, exist_ok=True)
                (vault / relative).write_text("A published draft", encoding="utf-8")
                pairs = list(exporter.iter_source_pairs(vault))
                self.assertEqual(len(pairs), 1)
                self.assertEqual(pairs[0][2], Path("essays/whose-good.md"))
                full, titles = exporter.build_public_index(pairs)
                normalized = exporter.normalize(
                    "[[Public/Tracking/Essays/" + Path(relative).stem + "|Read essay]]",
                    Path("project/where-the-inquiry-stands.md"), full, titles,
                )[0]
                self.assertIn("[Read essay](../essays/whose-good.md)", normalized)

    def test_current_and_legacy_essay_index_sources_and_links(self):
        for filename in ("Overview.md", "Essays.md"):
            with self.subTest(filename=filename), TemporaryDirectory() as tmp:
                vault = Path(tmp)
                relative = Path("Public/Tracking/Essays") / filename
                (vault / relative).parent.mkdir(parents=True)
                (vault / relative).write_text("A published index", encoding="utf-8")
                (vault / relative.parent / "Unpublished draft.md").write_text(
                    "Not approved for export", encoding="utf-8"
                )
                pairs = list(exporter.iter_source_pairs(vault))
                self.assertEqual(len(pairs), 1)
                self.assertEqual(pairs[0][2], Path("essays/README.md"))
                full, titles = exporter.build_public_index(pairs)
                normalized = exporter.normalize(
                    "[[" + relative.with_suffix("").as_posix() + "|Essays]]",
                    Path("project/where-the-inquiry-stands.md"), full, titles,
                )[0]
                self.assertEqual(normalized, "[Essays](../essays/README.md)\n")

    def test_duplicate_essay_index_sources_fail_closed(self):
        with TemporaryDirectory() as tmp:
            vault = Path(tmp)
            parent = vault / "Public" / "Tracking" / "Essays"
            parent.mkdir(parents=True)
            (parent / "Overview.md").write_text("current", encoding="utf-8")
            (parent / "Essays.md").write_text("legacy", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                list(exporter.iter_source_pairs(vault))

    def test_renamed_essay_duplicate_fails_closed(self):
        with TemporaryDirectory() as tmp:
            vault = Path(tmp)
            parent = vault / "Public" / "Tracking" / "Essays"
            parent.mkdir(parents=True)
            (parent / "Whose Good.md").write_text("one", encoding="utf-8")
            (parent / "Whose Good?.md").write_text("two", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                list(exporter.iter_source_pairs(vault))

    def test_undesignated_essay_is_not_exported(self):
        with TemporaryDirectory() as tmp:
            vault = Path(tmp)
            parent = vault / "Public" / "Tracking" / "Essays"
            parent.mkdir(parents=True)
            (parent / "Future private draft.md").write_text("private", encoding="utf-8")
            self.assertEqual(list(exporter.iter_source_pairs(vault)), [])

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

    def test_status_is_workflow_metadata_not_public_provenance(self):
        result = self.render(
            "---\ndate: 2026-10-23\npermalink: /sits/2026-10-23\n"
            "description: Public sit\nstatus: draft\ntags: [ruyer]\n---\nBody\n"
        )
        self.assertNotIn("status: draft", result)
        self.assertNotIn("permalink:", result)
        self.assertIn("date: 2026-10-23", result)
        self.assertIn("description: Public sit", result)

    def test_sit_image_placeholders_link_to_the_specific_public_day(self):
        note = Path("field-notes/2026-10-23 - What Living Changes.md")
        rendered = exporter.normalize(
            "![[" + "CIIS/Fall 2026 (Comps 2)/Field Journal/Media/photo.jpg|480" + "]]",
            note, self.full, self.titles,
        )[0]
        self.assertIn(
            "https://ecologicalintentionality.org/sits/2026-10-23",
            rendered,
        )
        self.assertNotIn("CIIS/", rendered)
        self.assertNotIn("photo.jpg", rendered)

    def test_non_sit_embed_falls_back_to_home(self):
        self.assertIn(
            "https://ecologicalintentionality.org/",
            self.render("![[Media/other-photo.jpg|480]]"),
        )

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
