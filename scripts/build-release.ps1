param([switch]$SkipDependencies)
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $ProjectRoot

$BuildPython = Join-Path $ProjectRoot '.build-venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $BuildPython)) {
    python -m venv (Join-Path $ProjectRoot '.build-venv')
}
if (-not $SkipDependencies) {
    & $BuildPython -m pip install -r requirements-desktop.txt
}
& $BuildPython scripts\build-formal-v1.py
& $BuildPython scripts\build-icon.py
& $BuildPython -m PyInstaller --noconfirm --clean MortalQuotaCard.spec

$Candidates = @(
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
)
$Compiler = $Candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $Compiler) { throw 'Inno Setup 6 is required to build the installer.' }
& $Compiler installer\mortal-quota-card.iss
