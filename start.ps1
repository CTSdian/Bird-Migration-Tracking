# Start both backend and frontend servers

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$frontendPath = Join-Path $projectRoot "frontend"

if (-not (Test-Path $pythonExe)) {
    Write-Error "Python environment not found at $pythonExe"
    exit 1
}

# Start backend from the project root so backend.main imports resolve correctly.
Start-Job -Name "bird-migration-backend" -ScriptBlock {
    param($root, $python)

    Set-Location $root
    & $python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
} -ArgumentList $projectRoot, $pythonExe | Out-Null

# Start frontend from the frontend workspace.
Set-Location $frontendPath
npm run dev