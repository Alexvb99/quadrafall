# SPDX-License-Identifier: GPL-3.0-or-later
# Compila Quadrafall para Windows.
#   Resultado: dist\Quadrafall\Quadrafall.exe  y  dist\Quadrafall-<versión>-windows.zip
# Uso (desde cualquier carpeta):  powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

$python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
& $python -m pip install --quiet -e ".[dev]"
& $python -m pytest -q
& $python -m PyInstaller --noconfirm --clean packaging\quadrafall.spec

$version = (& $python -c "import sys; sys.path.insert(0, 'src'); import quadrafall; print(quadrafall.__version__)").Trim()
Copy-Item LICENSE dist\Quadrafall\LICENSE.txt
Copy-Item README.md dist\Quadrafall\README.md
$zip = "dist\Quadrafall-$version-windows.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path dist\Quadrafall -DestinationPath $zip
Write-Host "Listo: $zip"
