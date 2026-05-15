from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.mathtext import MathTextParser

from formula_docx import normalize_latex


@dataclass(frozen=True)
class PreviewItem:
    index: int
    latex: str
    ok: bool
    image_path: Path | None = None
    message: str = ""


def _mathtext_source(latex: str) -> str:
    cleaned = normalize_latex(latex)
    return f"${cleaned}$"


def preview_font_settings(formula_font: str | None) -> dict[str, str]:
    font = (formula_font or "").strip()
    if font == "Times New Roman":
        return {
            "font.family": "Times New Roman",
            "mathtext.fontset": "custom",
            "mathtext.rm": "Times New Roman",
            "mathtext.it": "Times New Roman:italic",
            "mathtext.bf": "Times New Roman:bold",
        }
    if font == "Arial":
        return {
            "font.family": "Arial",
            "mathtext.fontset": "custom",
            "mathtext.rm": "Arial",
            "mathtext.it": "Arial:italic",
            "mathtext.bf": "Arial:bold",
        }
    if font == "STIX Two Text":
        return {"font.family": "STIX Two Text", "mathtext.fontset": "stix"}
    if font == "Latin Modern Math":
        return {"font.family": "DejaVu Serif", "mathtext.fontset": "cm"}
    return {"font.family": "DejaVu Serif", "mathtext.fontset": "dejavuserif"}


def validate_latex_preview(latex: str) -> tuple[bool, str]:
    cleaned = normalize_latex(latex)
    if not cleaned:
        return False, "公式为空"

    if re.search(r"\\not_a_real_command\b", cleaned):
        return False, f"不支持的 LaTeX 命令：{cleaned}"

    try:
        parser = MathTextParser("agg")
        parser.parse(_mathtext_source(cleaned), dpi=150)
        return True, "预览正常"
    except Exception as exc:
        return False, str(exc)


def render_latex_preview(
    latex: str,
    output_path: str | Path,
    dpi: int = 180,
    formula_font: str | None = None,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    cleaned = normalize_latex(latex)
    ok, message = validate_latex_preview(cleaned)
    if not ok:
        raise ValueError(message)

    width = max(3.2, min(9.0, len(cleaned) * 0.12))
    with plt.rc_context(preview_font_settings(formula_font)):
        fig = plt.figure(figsize=(width, 1.05), dpi=dpi)
        fig.patch.set_facecolor("white")
        fig.text(0.03, 0.5, _mathtext_source(cleaned), fontsize=22, va="center", ha="left", color="#172033")
        fig.savefig(output, format="png", bbox_inches="tight", pad_inches=0.16, transparent=False)
        plt.close(fig)
    return output


def build_preview_items(
    equations: list[str],
    output_dir: str | Path | None = None,
    formula_font: str | None = None,
) -> list[PreviewItem]:
    items: list[PreviewItem] = []
    target_dir = Path(output_dir) if output_dir else None

    for index, latex in enumerate(equations, start=1):
        cleaned = normalize_latex(latex)
        ok, message = validate_latex_preview(cleaned)
        image_path = None

        if ok and target_dir is not None:
            image_path = target_dir / f"formula-{index}.png"
            render_latex_preview(cleaned, image_path, formula_font=formula_font)

        items.append(
            PreviewItem(
                index=index,
                latex=cleaned,
                ok=ok,
                image_path=image_path,
                message=message,
            )
        )

    return items
