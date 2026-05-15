from __future__ import annotations

import io
import sys
import tempfile
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_file, send_from_directory

from formula_docx import SUPPORTED_FORMULA_FONTS, build_docx, parse_equations
from formula_symbols import SYMBOL_GROUPS
from ui_branding import APP_TITLE, FEEDBACK_URL, HELP_TEXT, WATERMARK_TEXT


DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def resource_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def _symbol_groups_payload() -> list[dict[str, Any]]:
    return [
        {
            "name": group.name,
            "symbols": [
                {
                    "label": symbol.label,
                    "snippet": symbol.snippet,
                    "hint": symbol.hint,
                    "group": group.name,
                }
                for symbol in group.symbols
            ],
        }
        for group in SYMBOL_GROUPS
    ]


def _docx_stream(result: object) -> io.BytesIO:
    if isinstance(result, io.BytesIO):
        result.seek(0)
        return result

    path = Path(result)
    return io.BytesIO(path.read_bytes())


def create_app(base_dir: str | Path | None = None) -> Flask:
    root = Path(base_dir) if base_dir is not None else resource_root()
    app = Flask(__name__)

    @app.get("/")
    @app.get("/index.html")
    def index():
        return send_file(root / "index.html")

    @app.get("/assets/<path:filename>")
    def assets(filename: str):
        return send_from_directory(root / "assets", filename)

    @app.get("/api/config")
    def config():
        return jsonify(
            {
                "appTitle": APP_TITLE,
                "feedbackUrl": FEEDBACK_URL,
                "helpText": HELP_TEXT,
                "watermarkText": WATERMARK_TEXT,
                "formulaFonts": list(SUPPORTED_FORMULA_FONTS),
                "symbolGroups": _symbol_groups_payload(),
            }
        )

    @app.post("/api/docx")
    def docx():
        payload = request.get_json(silent=True) or {}
        formula_font = str(payload.get("formulaFont") or SUPPORTED_FORMULA_FONTS[0]).strip()
        if formula_font not in SUPPORTED_FORMULA_FONTS:
            return jsonify({"error": f"不支持的公式字体：{formula_font}"}), 400

        raw_equations = payload.get("equations") or []
        if isinstance(raw_equations, str):
            equations = parse_equations(raw_equations)
        else:
            equations = [str(item).strip() for item in raw_equations if str(item).strip()]

        title = str(payload.get("title") or "Word 原生矢量公式")
        intro = str(payload.get("intro") or "以下公式由 LaTeX 转换为 Word 原生公式对象。")

        try:
            with tempfile.TemporaryDirectory(prefix="mathtool-web-") as tmp_dir:
                output_path = Path(tmp_dir) / "generated-formulas.docx"
                result = build_docx(
                    output_path=output_path,
                    title=title,
                    intro=intro,
                    equations=equations,
                    formula_font=formula_font,
                )
                stream = _docx_stream(result)
        except Exception as exc:
            return jsonify({"error": str(exc)}), 422

        return send_file(
            stream,
            mimetype=DOCX_MIME,
            as_attachment=True,
            download_name="generated-formulas.docx",
        )

    return app


app = create_app()
