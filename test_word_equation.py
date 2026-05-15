import unittest
import zipfile
from pathlib import Path
from lxml import etree

from formula_docx import build_docx, latex_to_omml


class WordEquationTests(unittest.TestCase):
    def test_latex_to_omml_returns_word_equation(self):
        omml = latex_to_omml(r"\frac{a}{b} = c")

        self.assertEqual(omml.tag.endswith("}oMath"), True)

    def test_integral_with_limits_does_not_leave_empty_word_placeholder(self):
        omml = latex_to_omml(r"\frac{d}{dx}\left(\int_{0}^{x} f(t)\,dt\right)=f(x)")
        xml = etree.tostring(omml, encoding="unicode")

        self.assertNotIn("<m:e/>", xml)
        self.assertIn("f(t)", xml)
        self.assertIn("dt", xml)

    def test_latex_to_omml_applies_formula_font(self):
        omml = latex_to_omml(r"E = mc^2", formula_font="Times New Roman")
        namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        fonts = omml.xpath(".//w:rFonts", namespaces=namespaces)

        self.assertGreater(len(fonts), 0)
        self.assertEqual(fonts[0].get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii"), "Times New Roman")
        self.assertEqual(fonts[0].get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi"), "Times New Roman")

    def test_build_docx_contains_native_word_equations(self):
        output = Path("test-output.docx")
        if output.exists():
            output.unlink()

        build_docx(
            output,
            title="公式测试",
            intro="下面是 Word 原生公式：",
            equations=[r"\frac{a}{b} = c", r"E = mc^2"],
            formula_font="Times New Roman",
        )

        self.assertEqual(output.exists(), True)
        with zipfile.ZipFile(output) as archive:
            document_xml = archive.read("word/document.xml").decode("utf-8")

        self.assertIn("<m:oMath", document_xml)
        self.assertIn("<m:f", document_xml)
        self.assertIn('w:ascii="Times New Roman"', document_xml)
        self.assertIn("公式测试", document_xml)

        output.unlink()


if __name__ == "__main__":
    unittest.main()
