import unittest
from pathlib import Path

from PIL import Image

from ui_branding import APP_ICON_ICO, APP_ICON_PNG, APP_TITLE, FEEDBACK_URL, HELP_TEXT, WATERMARK_TEXT


class BrandingTests(unittest.TestCase):
    def test_branding_text_matches_requested_copy(self):
        self.assertEqual(APP_TITLE, "干翻传统公式编辑，全给我用LaTex")
        self.assertEqual(WATERMARK_TEXT, "esdkaiyuan.online")
        self.assertEqual(FEEDBACK_URL, "https://www.esdkaiyuan.online/")
        self.assertIn("有任何宝贵的意见，以及问题需要反馈", HELP_TEXT)
        self.assertIn(FEEDBACK_URL, HELP_TEXT)

    def test_icon_assets_exist_for_window_and_exe(self):
        self.assertEqual(APP_ICON_PNG.suffix.lower(), ".png")
        self.assertEqual(APP_ICON_ICO.suffix.lower(), ".ico")
        self.assertTrue(APP_ICON_PNG.exists())
        self.assertTrue(APP_ICON_ICO.exists())

    def test_icon_png_has_transparent_rounded_corners(self):
        image = Image.open(APP_ICON_PNG).convert("RGBA")
        width, height = image.size
        corners = [
            image.getpixel((0, 0)),
            image.getpixel((width - 1, 0)),
            image.getpixel((0, height - 1)),
            image.getpixel((width - 1, height - 1)),
        ]
        center = image.getpixel((width // 2, height // 2))

        self.assertTrue(all(pixel[3] == 0 for pixel in corners))
        self.assertGreater(center[3], 240)

    def test_build_script_uses_exe_icon(self):
        build_script = Path("build_exe.ps1").read_text(encoding="utf-8")

        self.assertIn("--icon", build_script)
        self.assertIn("assets\\esdkaiyuan.ico", build_script)


if __name__ == "__main__":
    unittest.main()
