$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$pythonRoot = "C:\Users\28916\AppData\Local\Programs\Python\Python313"
$officeXsl = "C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"

if (!(Test-Path ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install python-docx lxml latex2mathml matplotlib pillow pyinstaller

$env:TCL_LIBRARY = Join-Path $pythonRoot "tcl\tcl8.6"
$env:TK_LIBRARY = Join-Path $pythonRoot "tcl\tk8.6"

.\.venv\Scripts\pyinstaller.exe `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name WordFormulaStudio `
    --icon ".\assets\esdkaiyuan.ico" `
    --hidden-import tkinter `
    --collect-data matplotlib `
    --collect-submodules matplotlib.backends.backend_agg `
    --add-binary "$pythonRoot\DLLs\_tkinter.pyd;." `
    --add-binary "$pythonRoot\DLLs\tcl86t.dll;." `
    --add-binary "$pythonRoot\DLLs\tk86t.dll;." `
    --add-data "$pythonRoot\tcl\tcl8.6;tcl\tcl8.6" `
    --add-data "$pythonRoot\tcl\tk8.6;tcl\tk8.6" `
    --add-data ".\assets\esdkaiyuan.png;assets" `
    --add-data ".\assets\esdkaiyuan.ico;assets" `
    --add-data ".\.venv\Lib\site-packages\latex2mathml\unimathsymbols.txt;latex2mathml" `
    --add-data "$officeXsl;." `
    word_formula_studio.py

Write-Host "Built dist\WordFormulaStudio.exe"
