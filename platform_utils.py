from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def open_path(path: str | Path) -> None:
    if sys.platform == "darwin":
        target = path.as_posix() if isinstance(path, Path) else str(path)
        subprocess.Popen(["open", target])
    elif os.name == "nt":
        target = str(Path(path))
        os.startfile(target)  # type: ignore[attr-defined]
    else:
        target = str(Path(path))
        subprocess.Popen(["xdg-open", target])
