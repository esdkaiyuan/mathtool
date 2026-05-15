import unittest

from formula_docx import SUPPORTED_FORMULA_FONTS
from formula_preview import validate_latex_preview
from formula_symbols import find_symbol, iter_symbols, preferred_cursor_offset


class FormulaSymbolTests(unittest.TestCase):
    def test_supported_formula_fonts_include_times_new_roman(self):
        self.assertIn("Times New Roman", SUPPORTED_FORMULA_FONTS)

    def test_symbol_catalog_contains_common_latex_snippets(self):
        snippets_by_label = {symbol.label: symbol.snippet for symbol in iter_symbols()}

        self.assertEqual(snippets_by_label["a⁄b"], r"\frac{a}{b}")
        self.assertEqual(snippets_by_label["√x"], r"\sqrt{x}")
        self.assertEqual(snippets_by_label["∫ₐᵇ"], r"\int_{a}^{b} f(x)\,dx")
        self.assertEqual(find_symbol("∫ₐᵇ").snippet, r"\int_{a}^{b} f(x)\,dx")

    def test_symbol_catalog_is_rich_and_buttons_show_only_symbols(self):
        symbols = list(iter_symbols())
        engineering_labels = {"pmat", "bmat", "cases", "sin", "cos", "tan", "ln", "log", "lim"}

        self.assertGreaterEqual(len(symbols), 80)
        self.assertTrue(all(symbol.label == symbol.display for symbol in symbols))
        self.assertTrue(all(symbol.snippet.strip() for symbol in symbols))
        self.assertFalse(any(chinese in symbol.label for symbol in symbols for chinese in "分式积分根号矩阵向量"))
        self.assertTrue(engineering_labels.isdisjoint({symbol.label for symbol in symbols}))

    def test_preferred_cursor_offset_moves_inside_first_empty_group(self):
        self.assertEqual(preferred_cursor_offset(r"\frac{}{}"), len(r"\frac{"))
        self.assertEqual(preferred_cursor_offset(r"\sqrt{}"), len(r"\sqrt{"))
        self.assertEqual(preferred_cursor_offset(r"\frac{a}{b}"), len(r"\frac{"))
        self.assertEqual(preferred_cursor_offset(r"\alpha "), len(r"\alpha "))

    def test_structure_symbols_are_preview_compatible(self):
        structure_symbols = [symbol for symbol in iter_symbols() if symbol.group == "结构"]

        self.assertGreater(len(structure_symbols), 0)
        failures = []
        for symbol in structure_symbols:
            ok, message = validate_latex_preview(symbol.snippet)
            if not ok:
                failures.append(f"{symbol.label}: {message}")

        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
