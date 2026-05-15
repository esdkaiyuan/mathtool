from __future__ import annotations

import os
import sys
from pathlib import Path

from formula_docx import build_docx


def configure_tk_runtime() -> None:
    candidates = [
        Path(sys.base_prefix) / "tcl",
        Path(sys.prefix) / "tcl",
        Path(r"C:\Users\28916\AppData\Local\Programs\Python\Python313\tcl"),
    ]

    for root in candidates:
        tcl = root / "tcl8.6"
        tk = root / "tk8.6"
        if tcl.exists() and tk.exists():
            os.environ.setdefault("TCL_LIBRARY", str(tcl))
            os.environ.setdefault("TK_LIBRARY", str(tk))
            return


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--smoke-output":
        build_docx(
            sys.argv[2],
            title="Word Formula Studio Smoke Test",
            intro="This document verifies native Word equation generation.",
            equations=[r"\frac{d}{dx}\left(\int_{0}^{x} f(t)\,dt\right)=f(x)", r"E=mc^2"],
            formula_font="Times New Roman",
        )
        return 0

    configure_tk_runtime()
    from word_formula_gui import main as gui_main

    return gui_main()


if __name__ == "__main__":
    raise SystemExit(main())
