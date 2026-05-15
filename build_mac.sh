#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "macOS app bundles must be built on macOS." >&2
  exit 1
fi

python3 -m venv .venv-mac
source .venv-mac/bin/activate

python -m pip install --upgrade pip
python -m pip install python-docx lxml latex2mathml matplotlib pillow pyinstaller

OFFICE_XSL="${MML2OMML_XSL:-/Applications/Microsoft Word.app/Contents/Resources/MML2OMML.XSL}"
if [[ ! -f "$OFFICE_XSL" ]]; then
  echo "Cannot find MML2OMML.XSL. Install Microsoft Word or set MML2OMML_XSL=/path/to/MML2OMML.XSL" >&2
  exit 1
fi

pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name WordFormulaStudio \
  --icon "assets/esdkaiyuan.icns" \
  --collect-data matplotlib \
  --collect-submodules matplotlib.backends.backend_agg \
  --add-data "assets/esdkaiyuan.png:assets" \
  --add-data "assets/esdkaiyuan.icns:assets" \
  --add-data "$OFFICE_XSL:." \
  word_formula_studio.py

echo "Built dist/WordFormulaStudio.app"

if command -v create-dmg >/dev/null 2>&1; then
  rm -f "dist/WordFormulaStudio-mac.dmg"
  create-dmg \
    --volname "WordFormulaStudio" \
    --window-pos 200 120 \
    --window-size 640 420 \
    --icon-size 96 \
    --app-drop-link 500 190 \
    "dist/WordFormulaStudio-mac.dmg" \
    "dist/WordFormulaStudio.app"
  echo "Built dist/WordFormulaStudio-mac.dmg"
else
  echo "create-dmg not found; skipped DMG. Install with: brew install create-dmg"
fi
