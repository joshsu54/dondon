# One-step Blender MCP setup for Claude Code on Windows (same steps as install_claude_code.sh).
#   1. Python venv in Tools\BlenderMCP\.venv with the pinned mcp-for-blender (requirements.lock.txt)
#   2. Install + enable the bundled Blender add-on (existing add-on file and userpref.blend are backed up first)
#   3. Register the "blender" MCP server with Claude Code (local scope: this project, this computer only)
# Usage (PowerShell, from the repo root):
#   powershell -ExecutionPolicy Bypass -File Tools\BlenderMCP\install_claude_code.ps1
#   powershell -ExecutionPolicy Bypass -File Tools\BlenderMCP\install_claude_code.ps1 -Blender "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe"
#   add -NoClaude to skip step 3
param([string]$Blender = $env:BLENDER, [switch]$NoClaude)
# 'Continue': Windows PowerShell 5.1 turns any stderr line of a native program into an error under 'Stop';
# every step below checks its own result instead.
$ErrorActionPreference = 'Continue'
$ToolDir = $PSScriptRoot
$Repo = (Resolve-Path (Join-Path $ToolDir '..\..')).Path
$Venv = Join-Path $ToolDir '.venv'
$VenvPy = Join-Path $Venv 'Scripts\python.exe'
$Server = Join-Path $Venv 'Scripts\mcp-for-blender.exe'
function Say($m) { Write-Host "`n== $m" -ForegroundColor Cyan }

# ---- 1. Python environment
Say 'Python environment'
if (-not (Test-Path $Server)) {
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        uv venv --python '>=3.10' $Venv
        uv pip install --python $VenvPy -r (Join-Path $ToolDir 'requirements.lock.txt')
        if ($LASTEXITCODE -ne 0) { throw 'uv could not install requirements.lock.txt' }
    } else {
        $py = if (Get-Command py -ErrorAction SilentlyContinue) { @('py', '-3') } elseif (Get-Command python -ErrorAction SilentlyContinue) { @('python') } else { throw 'Python 3.10+ not found. Install it from python.org (tick "Add to PATH") or install uv, then rerun.' }
        & $py[0] $py[1..9] -c 'import sys; assert sys.version_info >= (3, 10), "Python 3.10+ required"'
        & $py[0] $py[1..9] -m venv $Venv
        & $VenvPy -m pip install --quiet --upgrade pip
        & $VenvPy -m pip install --quiet -r (Join-Path $ToolDir 'requirements.lock.txt')
        if ($LASTEXITCODE -ne 0) { throw 'pip could not install requirements.lock.txt' }
    }
}
& $VenvPy -c 'import blender_mcp, mcp; print("mcp-for-blender ready")'
if ($LASTEXITCODE -ne 0) { throw 'mcp-for-blender did not install' }

# ---- 2. Blender add-on
Say 'Blender add-on'
if (-not $Blender) {
    $cands = @(Get-ChildItem 'C:\Program Files\Blender Foundation\Blender*\blender.exe' -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | ForEach-Object FullName)
    $cands += @(Get-ChildItem "$env:ProgramFiles\Steam\steamapps\common\Blender\blender.exe" -ErrorAction SilentlyContinue | ForEach-Object FullName)
    $cmd = Get-Command blender -ErrorAction SilentlyContinue; if ($cmd) { $cands += $cmd.Source }
    $Blender = $cands | Select-Object -First 1
}
if (-not $Blender -or -not (Test-Path $Blender)) { throw 'Blender not found. Pass it: -Blender "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe"' }
& $Blender --version | Select-Object -First 1
$out = & $Blender --background --factory-startup --python (Join-Path $ToolDir 'install_blender_addon.py') 2>&1 | Out-String
$out -split "`n" | Where-Object { $_ -match 'BLENDER_MCP_INSTALLED|Error|Traceback' }
if ($out -notmatch 'BLENDER_MCP_INSTALLED') { throw 'Add-on install failed (full Blender output above was filtered; rerun the Blender command by hand to see it).' }

# ---- 3. Claude Code registration
Say 'Claude Code'
if ($NoClaude) {
    Write-Host 'Skipped (-NoClaude).'
} elseif (Get-Command claude -ErrorAction SilentlyContinue) {
    Push-Location $Repo
    try {
        claude mcp remove blender --scope local *> $null      # fine if it was not registered yet
        # start-mcp is a POSIX script; on Windows call the server directly with the same environment.
        # Prefer uvx with the pinned version (verified on a Windows desktop, 2026-10-22); fall back to the venv executable.
        if (Get-Command uvx -ErrorAction SilentlyContinue) {
            claude mcp add blender --scope local -e DISABLE_TELEMETRY=true -e BLENDER_HOST=127.0.0.1 -e BLENDER_PORT=9876 -- uvx mcp-for-blender==2.1.9
        } else {
            claude mcp add blender --scope local -e DISABLE_TELEMETRY=true -e BLENDER_HOST=127.0.0.1 -e BLENDER_PORT=9876 -- $Server
        }
        if ($LASTEXITCODE -ne 0) { throw 'claude mcp add failed' }
        claude mcp list 2>$null | Select-String -Pattern blender
    } finally { Pop-Location }
} else {
    Write-Host "claude CLI not found. Install Claude Code, then run in ${Repo}:"
    Write-Host "  claude mcp add blender --scope local -e DISABLE_TELEMETRY=true -e BLENDER_HOST=127.0.0.1 -e BLENDER_PORT=9876 -- uvx mcp-for-blender==2.1.9"
}

Say 'Done'
Write-Host 'Next: open Blender (the add-on starts its server on 127.0.0.1:9876; if not, press N in the 3D view > MCP tab > Start),'
Write-Host "then run 'claude' in $Repo and type /mcp to check that 'blender' is connected. Keep only one Blender instance open."
