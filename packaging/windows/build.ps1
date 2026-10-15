# SPDX-License-Identifier: GPL-3.0-or-later
# Compila Quadrafall para Windows.
#   dist\Quadrafall\Quadrafall.exe                  (carpeta del programa)
#   dist\Quadrafall-<versión>-Windows-Setup.exe     (instalador, si está Inno Setup 6)
#   dist\Quadrafall-<versión>-Windows-Portable.zip  (sin instalar)
# Uso (desde cualquier carpeta):  powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
# Variable opcional: $env:APP_URL = dirección del repositorio, para el instalador.
$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

function Invoke-Checked {
    # Los programas externos no detienen el script al fallar: se comprueba a mano.
    & $args[0] $args[1..($args.Count - 1)]
    if ($LASTEXITCODE -ne 0) { throw "Falló: $($args -join ' ')" }
}

$python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
Invoke-Checked $python -m pip install --quiet -e ".[dev]"
Invoke-Checked $python -m pytest -q
Invoke-Checked $python -m PyInstaller --noconfirm --clean packaging\quadrafall.spec

$version = (& $python -c "import sys; sys.path.insert(0, 'src'); import quadrafall; print(quadrafall.__version__)").Trim()
Copy-Item LICENSE dist\Quadrafall\LICENSE.txt
Copy-Item README.md dist\Quadrafall\README.md

$zip = "dist\Quadrafall-$version-Windows-Portable.zip"
if (Test-Path $zip) { Remove-Item $zip }
Compress-Archive -Path dist\Quadrafall -DestinationPath $zip
Write-Host "Listo: $zip"

$iscc = @(
    (Get-Command ISCC.exe -ErrorAction SilentlyContinue).Source,
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if ($iscc) {
    $url = if ($env:APP_URL) { $env:APP_URL } else { "https://github.com" }
    Invoke-Checked $iscc /Q "/DAppVersion=$version" "/DAppURL=$url" packaging\windows\installer.iss
    Write-Host "Listo: dist\Quadrafall-$version-Windows-Setup.exe"
} else {
    Write-Warning "No se encontró Inno Setup 6: se omite el instalador (https://jrsoftware.org/isdl.php)."
}
