$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$officeXsl = "C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"

if (!(Test-Path ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install python-docx lxml latex2mathml matplotlib pillow flask pyinstaller

.\.venv\Scripts\pyinstaller.exe `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name WordFormulaStudio `
    --icon ".\assets\esdkaiyuan.ico" `
    --hidden-import flask `
    --hidden-import werkzeug.serving `
    --add-data ".\index.html;." `
    --add-data ".\assets\esdkaiyuan.png;assets" `
    --add-data ".\assets\esdkaiyuan.ico;assets" `
    --add-data ".\.venv\Lib\site-packages\latex2mathml\unimathsymbols.txt;latex2mathml" `
    --add-data "$officeXsl;." `
    web_formula_studio.py

Write-Host "Built dist\WordFormulaStudio.exe"
