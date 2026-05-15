# 干翻传统公式编辑，全给我用LaTex

Python desktop/web tool for converting LaTeX formulas into DOCX files with native Word equation objects.

## Features

- Real-time LaTeX preview
- Native Word OMML equation generation
- Formula font selection, including Times New Roman
- Symbol palette with LaTeX insertion templates
- Windows PyInstaller build script
- macOS PyInstaller build script and `.icns` icon
- Python-backed web editor with MathJax SVG preview and DOCX download

## Local Web Mode

```powershell
.\.venv\Scripts\python.exe web_formula_studio.py
```

The launcher starts a local Flask service and opens the browser at an available `127.0.0.1` port, starting from `5173`.

## Windows Build

```powershell
.\build_exe.ps1
```

Output:

```text
dist\WordFormulaStudio.exe
```

The Windows executable opens the Python-backed web editor.

## macOS Build

macOS apps must be built on macOS:

```bash
chmod +x build_mac.sh
./build_mac.sh
```

Output:

```text
dist/WordFormulaStudio.app
```

See [MAC_BUILD.md](MAC_BUILD.md) for details.

## Tests

```bash
python -m unittest test_branding.py test_gui_branding_behavior.py test_formula_symbols.py test_word_equation.py test_preview.py test_mac_packaging.py test_web_backend.py test_web_frontend.py
```
