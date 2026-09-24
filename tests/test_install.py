"""Exercise installation's public filesystem contract in disposable homes."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Installation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="plainpad install ")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "XDG_DATA_HOME": str(self.home / "custom data"),
            "XDG_CONFIG_HOME": str(self.home / "custom config"),
        }
        self.env.pop("HYPRLAND_INSTANCE_SIGNATURE", None)
        self.hypr = self.home / "custom config/hypr/hyprland.lua"
        self.hypr.parent.mkdir(parents=True)
        self.original = "-- Omarchy personal config\n-- Keep this comment.\n"
        self.hypr.write_text(self.original)
        self.launcher = self.home / ".local/bin/plainpad"

    def install(self, *args, success=True):
        result = subprocess.run(
            [str(ROOT / "install.sh"), *args],
            env=self.env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def test_install_update_uninstall_preserves_other_files_and_config(self):
        self.install("--omarchy")
        self.assertEqual(
            subprocess.check_output(
                [self.launcher, "--version"], env=self.env, text=True
            ),
            "Plainpad 0.1.0\n",
        )
        configured = self.hypr.read_text()
        self.assertIn(self.original, configured)
        self.assertIn("dofile(", configured)
        desktop = self.home / "custom data/applications/local.plainpad.Plainpad.desktop"
        subprocess.run(["desktop-file-validate", desktop], check=True)
        self.install("--omarchy")
        self.assertEqual(self.hypr.read_text(), configured)
        self.hypr.write_text(configured + "-- Later personal edit\n")
        unrelated = self.home / "custom data/plainpad/my-note.txt"
        unrelated.write_text("Keep me")
        self.install("--uninstall")
        self.assertEqual(
            self.hypr.read_text(), self.original + "-- Later personal edit\n"
        )
        self.assertFalse(self.launcher.exists())
        self.assertFalse(desktop.exists())
        self.assertEqual(unrelated.read_text(), "Keep me")
        self.install("--uninstall")

    def test_preserves_existing_and_modified_files(self):
        self.launcher.parent.mkdir(parents=True)
        self.launcher.write_text("existing executable")
        self.install(success=False)
        self.assertEqual(self.launcher.read_text(), "existing executable")
        self.assertEqual(self.hypr.read_text(), self.original)
        self.launcher.unlink()
        self.install()
        self.assertEqual(self.hypr.read_text(), self.original)
        self.launcher.write_text("local modification")
        self.install(success=False)
        self.install("--uninstall", success=False)
        self.assertEqual(self.launcher.read_text(), "local modification")

    def test_preserves_modified_managed_config(self):
        self.install("--omarchy")
        edited = self.hypr.read_text().replace("dofile(", "-- dofile(")
        self.hypr.write_text(edited)
        self.install("--uninstall", success=False)
        self.assertEqual(self.hypr.read_text(), edited)
        self.assertTrue(self.launcher.exists())


if __name__ == "__main__":
    unittest.main()
