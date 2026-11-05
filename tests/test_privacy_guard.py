"""Regression tests for distinguishing public URLs from local private paths."""
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "privacy_guard.py"


class PrivacyGuardTests(unittest.TestCase):
    def scan(self, content):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            essays = root / "essays"
            essays.mkdir(parents=True)
            (essays / "sample.md").write_text(content, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(GUARD), str(root)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_public_github_projects_url_is_not_a_local_mac_path(self):
        result = self.scan(
            "[Research board](https://github.com/users/example/projects/1)\n"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Privacy guard passed.", result.stdout)

    def test_real_absolute_mac_user_path_is_still_blocked(self):
        result = self.scan("Private local path: /Users/example/Documents/journal.md\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("absolute macOS user path", result.stdout)

    def test_local_file_url_is_still_blocked(self):
        result = self.scan("file:///Users/example/Documents/journal.md\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("local file URL", result.stdout)


if __name__ == "__main__":
    unittest.main()
