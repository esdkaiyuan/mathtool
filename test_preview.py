import unittest
from pathlib import Path
from unittest.mock import patch

from formula_preview import build_preview_items, preview_font_settings, render_latex_preview


class PreviewTests(unittest.TestCase):
    def test_build_preview_items_marks_valid_and_invalid_formulas(self):
        items = build_preview_items([r"\frac{a}{b}", r"\not_a_real_command{"])

        self.assertEqual(items[0].ok, True)
        self.assertEqual(items[0].index, 1)
        self.assertEqual(items[1].ok, False)
        self.assertIn("not_a_real_command", items[1].message)

    def test_render_latex_preview_creates_png_file(self):
        output_dir = Path("preview-test-output")
        output_dir.mkdir(exist_ok=True)
        output = output_dir / "preview.png"
        if output.exists():
            output.unlink()

        render_latex_preview(r"\int_0^1 x^2 dx", output)

        self.assertEqual(output.exists(), True)
        self.assertGreater(output.stat().st_size, 1000)
        output.unlink()
        output_dir.rmdir()

    def test_preview_font_settings_maps_times_new_roman(self):
        settings = preview_font_settings("Times New Roman")

        self.assertEqual(settings["mathtext.fontset"], "custom")
        self.assertEqual(settings["mathtext.rm"], "Times New Roman")
        self.assertEqual(settings["font.family"], "Times New Roman")

    def test_build_preview_items_passes_formula_font_to_renderer(self):
        output_dir = Path("preview-font-pass-through")
        output_dir.mkdir(exist_ok=True)
        try:
            with patch("formula_preview.render_latex_preview") as render:
                items = build_preview_items([r"E=mc^2"], output_dir, formula_font="Times New Roman")

            self.assertEqual(items[0].ok, True)
            render.assert_called_once_with("E=mc^2", output_dir / "formula-1.png", formula_font="Times New Roman")
        finally:
            output_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
