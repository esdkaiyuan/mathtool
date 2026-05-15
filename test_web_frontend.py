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

    def test_web_app_replicates_compiled_exe_layout(self):
        expected_markers = [
            "tk-shell",
            "tk-header",
            "tk-main",
            "tk-paned",
            "tk-input-panel",
            "tk-preview-panel",
            "tk-output-bar",
            "tk-status-bar",
            "tk-bottom-watermark",
            "previewCount",
            "outputPathInput",
            "openAfterGenerate",
            "Ctrl+Enter 生成 Word  ·  Ctrl+R 刷新预览  ·  Ctrl+Shift+C 复制 LaTeX",
        ]

        for marker in expected_markers:
            with self.subTest(marker=marker):
                self.assertIn(marker, self.html)

    def test_web_app_uses_exe_visual_constants(self):
        for color in ("#f7fafc", "#f8fbff", "#f3f7fb", "#dbe6f0"):
            with self.subTest(color=color):
                self.assertIn(color, self.html)


if __name__ == "__main__":
    unittest.main()
