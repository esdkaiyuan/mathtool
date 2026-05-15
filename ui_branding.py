from __future__ import annotations

import sys
from pathlib import Path


APP_TITLE = "干翻传统公式编辑，全给我用LaTex"
WATERMARK_TEXT = "esdkaiyuan.online"
WATERMARK_COLOR = "#e9c7cf"
WATERMARK_FONT_SIZE = 14
WATERMARK_STEP_X = 420
WATERMARK_STEP_Y = 240
BOTTOM_WATERMARK_COLOR = "#dbe6f0"
BOTTOM_WATERMARK_FONT_SIZE = 8
BOTTOM_WATERMARK_STEP_X = 230
BOTTOM_WATERMARK_STEP_Y = 18
APP_BACKGROUND = "#f7fafc"
FROSTED_PANEL_BACKGROUND = "#f8fbff"
TRANSLUCENT_EDITOR_BACKGROUND = "#f3f7fb"
FEEDBACK_URL = "https://www.esdkaiyuan.online/"

HELP_TEXT = (
    f"有任何宝贵的意见，以及问题需要反馈，请前往{FEEDBACK_URL}\n\n"
    "基本使用说明：\n"
    "1. 在左侧 LaTeX 编辑区输入公式，每行一个公式，右侧会自动刷新预览。\n"
    "2. 点击符号库里的数学符号，可把对应 LaTeX 示例插入到光标位置，再按需要修改参数。\n"
    "3. 通过顶部字体下拉框选择 Word 公式字体，预览和生成文档会同步使用当前选择。\n"
    "4. 点击“生成 Word”会输出包含 Word 原生矢量公式对象的 DOCX，可在 Word 里继续编辑和复制。\n"
    "5. Ctrl+Enter 生成 Word，Ctrl+R 刷新预览，Ctrl+Shift+C 复制左侧 LaTeX。"
)


def resource_path(relative_path: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative_path


APP_ICON_PNG = resource_path("assets/esdkaiyuan.png")
APP_ICON_ICO = resource_path("assets/esdkaiyuan.ico")
