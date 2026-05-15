import unittest
from pathlib import Path


class WebFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = Path("index.html").read_text(encoding="utf-8")

    def test_web_app_has_python_backend_integration_points(self):
        self.assertIn("loadBackendConfig", self.html)
        self.assertIn("/api/config", self.html)
        self.assertIn("/api/docx", self.html)
        self.assertIn("generateWordDocx", self.html)

    def test_web_app_has_desktop_branding_and_controls(self):
        self.assertIn("干翻传统公式编辑，全给我用LaTex", self.html)
        self.assertIn("assets/esdkaiyuan.png", self.html)
        self.assertIn("formulaFontSelect", self.html)
        self.assertIn("symbolPalette", self.html)
        self.assertIn("helpDialog", self.html)
        self.assertIn("esdkaiyuan.online", self.html)


if __name__ == "__main__":
    unittest.main()
