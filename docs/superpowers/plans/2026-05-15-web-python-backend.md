# Web Python Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Python-backed web mode that reuses the desktop formula engine while improving the existing web UI.

**Architecture:** Flask serves `index.html`, static assets, JSON configuration, and generated DOCX downloads. The single-file front end uses MathJax for live SVG preview and calls Flask for Word-native formula output.

**Tech Stack:** Python unittest, Flask, python-docx, latex2mathml, MathJax 3, FontAwesome 6, single-file HTML/CSS/JS.

---

### Task 1: Web Backend Tests

**Files:**
- Create: `test_web_backend.py`
- Create: `test_web_frontend.py`

- [ ] **Step 1: Write failing backend tests**

```python
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
```

- [ ] **Step 2: Write failing frontend static tests**

```python
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
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m unittest test_web_backend.py test_web_frontend.py`

Expected: import failure for `web_formula_backend` and missing strings in `index.html`.

### Task 2: Flask Backend

**Files:**
- Create: `web_formula_backend.py`
- Create: `web_formula_studio.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Implement backend app**

Create `create_app()` with `/`, `/assets/<path>`, `/api/config`, and `/api/docx`.

- [ ] **Step 2: Implement launcher**

Create a launcher that finds an available localhost port, starts Flask in a background thread, opens the browser, and keeps the process alive until interrupted.

- [ ] **Step 3: Add Flask to requirements**

Append `flask`.

- [ ] **Step 4: Run backend tests**

Run: `python -m unittest test_web_backend.py`

Expected: PASS.

### Task 3: Frontend Enhancement

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Update branding and layout controls**

Add favicon/logo, app title, formula font select, help button, symbol palette container, generate Word button, bottom watermark strip, and DOCX title/intro controls.

- [ ] **Step 2: Add backend loading JavaScript**

Add `loadBackendConfig()`, `renderFormulaFonts()`, `renderSymbolPalette()`, `insertLatexSnippet()`, `generateWordDocx()`, and help dialog logic.

- [ ] **Step 3: Preserve offline fallback**

Keep local fallback config so opening `index.html` directly still works for preview and SVG copy, while DOCX generation shows a clear local-backend-required message.

- [ ] **Step 4: Run frontend static tests**

Run: `python -m unittest test_web_frontend.py`

Expected: PASS.

### Task 4: Packaging and Docs

**Files:**
- Modify: `build_exe.ps1`
- Modify: `.gitignore`
- Modify: `README.md`

- [ ] **Step 1: Update build script**

Include `flask`, `index.html`, and `web_formula_studio.py` in PyInstaller build inputs.

- [ ] **Step 2: Track web app**

Remove the `index.html` ignore rule.

- [ ] **Step 3: Document web mode**

Add commands for local web launch and Windows packaging.

- [ ] **Step 4: Run full tests**

Run: `python -m unittest test_branding.py test_gui_branding_behavior.py test_formula_symbols.py test_word_equation.py test_preview.py test_mac_packaging.py test_web_backend.py test_web_frontend.py`

Expected: PASS.
