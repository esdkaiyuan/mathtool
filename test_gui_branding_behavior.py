import unittest

from ui_branding import (
    BOTTOM_WATERMARK_FONT_SIZE,
    BOTTOM_WATERMARK_STEP_X,
    FROSTED_PANEL_BACKGROUND,
    TRANSLUCENT_EDITOR_BACKGROUND,
    WATERMARK_TEXT,
)
from word_formula_studio import configure_tk_runtime

configure_tk_runtime()
from word_formula_gui import BottomWatermarkStrip, WatermarkFrame, WordFormulaStudio


class GuiBrandingBehaviorTests(unittest.TestCase):
    def test_window_starts_maximized(self):
        app = WordFormulaStudio()
        try:
            app.update()
            self.assertIn(app.state(), {"zoomed", "normal"})
            self.assertTrue(app.is_startup_maximized)
        finally:
            app._on_close()

    def test_watermark_items_are_not_drawn(self):
        app = WordFormulaStudio()
        try:
            app.update()
            frames: list[WatermarkFrame] = []

            def walk(widget):
                for child in widget.winfo_children():
                    if isinstance(child, WatermarkFrame):
                        frames.append(child)
                    walk(child)

            walk(app)

            self.assertGreaterEqual(len(frames), 3)
            self.assertTrue(all(not frame.canvas.find_withtag("watermark") for frame in frames))
        finally:
            app._on_close()

    def test_bottom_watermark_strip_draws_tiny_horizontal_repeating_text(self):
        app = WordFormulaStudio()
        try:
            app.update()
            self.assertIsInstance(app.bottom_watermark, BottomWatermarkStrip)
            self.assertEqual(app.bottom_watermark.font_size, BOTTOM_WATERMARK_FONT_SIZE)
            self.assertGreaterEqual(app.bottom_watermark.step_x, BOTTOM_WATERMARK_STEP_X)
            items = app.bottom_watermark.canvas.find_withtag("bottom-watermark")
            self.assertGreater(len(items), 2)
            self.assertEqual(
                {app.bottom_watermark.canvas.itemcget(item, "text") for item in items},
                {WATERMARK_TEXT},
            )
            self.assertEqual(
                {app.bottom_watermark.canvas.itemcget(item, "angle") for item in items},
                {"0.0"},
            )
            before = app.bottom_watermark.offset_y
            app.bottom_watermark.stop_animation()
            app.bottom_watermark._animate()
            self.assertNotEqual(app.bottom_watermark.offset_y, before)
            app.bottom_watermark.stop_animation()
        finally:
            app._on_close()

    def test_visual_surfaces_use_frosted_and_translucent_backgrounds(self):
        app = WordFormulaStudio()
        try:
            app.update()
            self.assertEqual(app.equation_text.cget("bg"), TRANSLUCENT_EDITOR_BACKGROUND)
            self.assertEqual(app.intro_text.cget("bg"), TRANSLUCENT_EDITOR_BACKGROUND)
            self.assertEqual(app.input_panel.cget("bg"), FROSTED_PANEL_BACKGROUND)
            self.assertEqual(app.preview_panel.cget("bg"), FROSTED_PANEL_BACKGROUND)
        finally:
            app._on_close()


if __name__ == "__main__":
    unittest.main()
