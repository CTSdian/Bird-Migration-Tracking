# Start both backend and frontend servers

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$frontendPath = Join-Path $projectRoot "frontend"

if (-not (Test-Path $pythonExe)) {
    Write-Error "Python environment not found at $pythonExe"
    exit 1
}

function Stop-ListenersOnPort {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $connections) {
        return
    }

    $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pidValue in $pids) {
        if (-not (Get-Process -Id $pidValue -ErrorAction SilentlyContinue)) {
            continue
        }

        try {
            Stop-Process -Id $pidValue -Force -ErrorAction Stop
            Write-Host "Stopped process $pidValue on port $Port"
        }
        catch {
            if (Get-Process -Id $pidValue -ErrorAction SilentlyContinue) {
                Write-Warning "Unable to stop process $pidValue on port ${Port}: $($_.Exception.Message)"
            }
        }
    }
}

# Clear any stale background jobs from previous runs.
Get-Job -Name "bird-migration-backend" -ErrorAction SilentlyContinue | Remove-Job -Force -ErrorAction SilentlyContinue

# Free backend port in case an orphan uvicorn process is still bound.
Stop-ListenersOnPort -Port 8001

# Start backend from the project root so backend.main imports resolve correctly.
Start-Job -Name "bird-migration-backend" -ScriptBlock {
    param($root, $python)

    Set-Location $root
    & $python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
} -ArgumentList $projectRoot, $pythonExe | Out-Null

# Start frontend from the frontend workspace.
Set-Location $frontendPath
npm run dev