"""Release packaging contract for the current-user Windows installer."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleaseConfigTest(unittest.TestCase):
    def test_pyinstaller_is_onedir_and_bundles_only_required_card_assets(self):
        spec = (ROOT / "MortalQuotaCard.spec").read_text(encoding="utf-8")
        self.assertIn("COLLECT(", spec)
        self.assertNotIn("onefile=True", spec)
        self.assertIn("quota-card-app.html", spec)
        self.assertIn("mortal-quota-card.ico", spec)

    def test_inno_setup_is_current_user_and_creates_expected_shortcuts(self):
        script = (ROOT / "installer" / "mortal-quota-card.iss").read_text(encoding="utf-8-sig")
        self.assertIn("PrivilegesRequired=lowest", script)
        self.assertIn("凡人额度卡-Setup-1.0.0", script)
        self.assertIn("{userdesktop}", script)
        self.assertIn("{userprograms}", script)
        self.assertIn("UninstallDisplayIcon", script)
        self.assertIn("{%LOCALAPPDATA}\\Programs\\MortalQuotaCard", script)
        self.assertIn("unins000.exe", script)


if __name__ == "__main__":
    unittest.main()
