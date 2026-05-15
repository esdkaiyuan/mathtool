import io
import unittest
from unittest.mock import patch

from formula_docx import SUPPORTED_FORMULA_FONTS


class WebBackendTests(unittest.TestCase):
    def test_config_api_returns_desktop_project_configuration(self):
        from web_formula_backend import create_app

        client = create_app().test_client()
        response = client.get("/api/config")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["appTitle"], "干翻传统公式编辑，全给我用LaTex")
        self.assertEqual(payload["feedbackUrl"], "https://www.esdkaiyuan.online/")
        self.assertEqual(payload["watermarkText"], "esdkaiyuan.online")
        self.assertEqual(payload["formulaFonts"], list(SUPPORTED_FORMULA_FONTS))
        self.assertIn("Times New Roman", payload["formulaFonts"])
        self.assertGreaterEqual(len(payload["symbolGroups"]), 8)
        self.assertEqual(payload["symbolGroups"][0]["name"], "基础")
        self.assertIn("symbols", payload["symbolGroups"][0])

    def test_index_html_route_serves_web_app_for_existing_browser_url(self):
        from web_formula_backend import create_app

        client = create_app().test_client()
        response = client.get("/index.html")

        try:
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/html", response.headers["Content-Type"])
            self.assertIn("干翻传统公式编辑，全给我用LaTex", response.get_data(as_text=True))
        finally:
            response.close()

    def test_docx_api_returns_word_document_attachment(self):
        from web_formula_backend import create_app

        fake_docx = io.BytesIO(b"fake-docx")
        fake_docx.name = "generated-formulas.docx"

        with patch("web_formula_backend.build_docx") as build_docx:
            build_docx.return_value = fake_docx
            client = create_app().test_client()
            response = client.post(
                "/api/docx",
                json={
                    "title": "测试文档",
                    "intro": "网页生成",
                    "equations": [r"E = mc^2"],
                    "formulaFont": "Times New Roman",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"fake-docx")
        self.assertEqual(
            response.headers["Content-Type"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        self.assertIn("attachment;", response.headers["Content-Disposition"])
        build_docx.assert_called_once()
        _, kwargs = build_docx.call_args
        self.assertEqual(kwargs["title"], "测试文档")
        self.assertEqual(kwargs["intro"], "网页生成")
        self.assertEqual(kwargs["equations"], [r"E = mc^2"])
        self.assertEqual(kwargs["formula_font"], "Times New Roman")


if __name__ == "__main__":
    unittest.main()
