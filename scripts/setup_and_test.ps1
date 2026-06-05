<#
Automates setup and test for NSE Analyser on Windows.

Usage:
  Open PowerShell as your user and run:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .\scripts\setup_and_test.ps1

This will:
- create a virtual environment at .venv (unless already present)
- install dependencies from requirements.txt
- run pytest and save logs to .\logs\
- create a desktop shortcut named 'nse analyser' that runs run_local.bat

No Finnhub API key is required to run the tests; the client gracefully handles missing keys.
#>

param(
    [switch]$NoVenv
)

function Write-Log($msg) { Write-Host "[setup] $msg" }

# Determine repository root (parent of the scripts directory)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
Set-Location $root

if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" | Out-Null }

if (-not $NoVenv) {
    if (-not (Test-Path ".venv")) {
        Write-Log "Creating virtual environment .venv"
        python -m venv .venv
    } else {
        Write-Log ".venv already exists, skipping creation"
    }
    $activate = Join-Path $root ".venv\Scripts\Activate.ps1"
    if (Test-Path $activate) {
        Write-Log "Activating virtual environment"
        & $activate
    } else {
        Write-Log "Activation script not found; proceeding without activation"
    }
}

Write-Log "Upgrading pip"
python -m pip install --upgrade pip | Tee-Object -FilePath "logs\pip_upgrade.log"

Write-Log "Installing requirements"
python -m pip install --prefer-binary -r requirements.txt 2>&1 | Tee-Object -FilePath "logs\pip_install.log"

Write-Log "Running unit tests (pytest)"
python -m pytest -q 2>&1 | Tee-Object -FilePath "logs\pytest.log"

Write-Log "Creating desktop shortcut 'nse analyser'"
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $ShortcutPath = "$env:USERPROFILE\Desktop\nse analyser.lnk"
    $TargetPath = Join-Path $root "run_local.bat"
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $TargetPath
    $Shortcut.WorkingDirectory = $root
    $Shortcut.WindowStyle = 1
    $Shortcut.Description = "Run NSE Analyser (backend)"
    $Shortcut.Save()
    Write-Log "Shortcut created at $ShortcutPath"
} catch {
    Write-Log "Failed to create shortcut: $_"
}

Write-Log "Setup and test complete. Logs are in 'logs' folder."