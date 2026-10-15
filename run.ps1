param (
    [string]$Goal = "",
    [switch]$Headless,
    [string]$Provider = "",
    [int]$MaxSteps = 20
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if (-not (Test-Path "$ScriptDir\.venv\Scripts\python.exe")) {
    Write-Host "[INFO] Setting up virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    & "$ScriptDir\.venv\Scripts\pip.exe" install -r requirements.txt
    & "$ScriptDir\.venv\Scripts\playwright.exe" install chromium
}

$argsList = @("-m", "src.main")
if ($Goal) { $argsList += @("--goal", $Goal) }
if ($Headless) { $argsList += "--headless" }
if ($Provider) { $argsList += @("--provider", $Provider) }
if ($MaxSteps) { $argsList += @("--max-steps", $MaxSteps) }

& "$ScriptDir\.venv\Scripts\python.exe" $argsList
