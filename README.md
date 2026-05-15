# 干翻传统公式编辑，全给我用LaTex

Python/Tkinter desktop tool for converting LaTeX formulas into DOCX files with native Word equation objects.

## Features

- Real-time LaTeX preview
- Native Word OMML equation generation
- Formula font selection, including Times New Roman
- Symbol palette with LaTeX insertion templates
- Windows PyInstaller build script
- macOS PyInstaller build script and `.icns` icon

## Windows Build

```powershell
.\build_exe.ps1
```

Output:

```text
dist\WordFormulaStudio.exe
```

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
python -m unittest test_branding.py test_gui_branding_behavior.py test_formula_symbols.py test_word_equation.py test_preview.py test_mac_packaging.py
```
