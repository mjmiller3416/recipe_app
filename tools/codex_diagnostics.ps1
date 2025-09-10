param(
  [switch]$NoWrite
)

$ErrorActionPreference = 'Continue'

Write-Host "=== Codex Diagnostics (PowerShell) ==="

Write-Host "PowerShell edition: $($PSVersionTable.PSEdition)"
Write-Host "PowerShell version: $($PSVersionTable.PSVersion)"

Write-Host "`nEnvironment:"
Write-Host "  OS: $env:OS"
Write-Host "  ARCH: $env:PROCESSOR_ARCHITECTURE"
Write-Host "  USERPROFILE: $env:USERPROFILE"
Write-Host "  PATH entries (first 15):"
($env:Path -split ';' | Select-Object -First 15) | ForEach-Object { Write-Host "    $_" }

Write-Host "`nWorking directory:"
Write-Host "  $(Get-Location)"

Write-Host "`nRepo root listing (first 50):"
try {
  Get-ChildItem -Force | Select-Object -First 50 | ForEach-Object {
    $type = if ($_.PSIsContainer) { 'DIR ' } else { 'FILE' }
    "{0} {1,-12} {2,10} {3}" -f $type, $_.Mode, ($_.Length), $_.Name
  } | ForEach-Object { Write-Host "  $_" }
} catch {
  Write-Host "  (failed to list directory: $($_.Exception.Message))"
}

function Test-Tool {
  param(
    [string]$Name,
    [string]$VersionArgs = ''
  )
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if ($cmd) {
    Write-Host "FOUND $Name: $($cmd.Path)"
    if ($VersionArgs -ne '') {
      try {
        $out = & $Name $VersionArgs 2>$null | Select-Object -First 1
        if ($out) { Write-Host "    $out" }
      } catch {
        Write-Host "    version check failed: $($_.Exception.Message)"
      }
    }
  } else {
    Write-Host "MISSING $Name"
  }
}

Write-Host "`nShell/tool availability:"
Test-Tool -Name 'pwsh' -VersionArgs '-v'
Test-Tool -Name 'bash' -VersionArgs '--version'
Test-Tool -Name 'git' -VersionArgs '--version'
Test-Tool -Name 'python' -VersionArgs '--version'
Test-Tool -Name 'python3' -VersionArgs '--version'

$cmdPath = (Get-Command cmd -ErrorAction SilentlyContinue).Path
if ($cmdPath) {
  Write-Host "FOUND cmd: $cmdPath"
  try {
    $ver = & cmd /c ver 2>$null
    if ($ver) { Write-Host "    $ver" }
  } catch {
    Write-Host "    failed to run cmd: $($_.Exception.Message)"
  }
} else {
  Write-Host "MISSING cmd"
}

if (-not $NoWrite) {
  Write-Host "`nWrite test:"
  $targetDir = $PSScriptRoot
  if (-not (Test-Path $targetDir)) {
    try { New-Item -ItemType Directory -Force -Path $targetDir | Out-Null } catch {}
  }
  $tmpPath = Join-Path -Path $targetDir -ChildPath '_tmp_diagnostic_write_test_ps.txt'
  try {
    'ok' | Out-File -FilePath $tmpPath -Encoding utf8 -Force
    $ok = Test-Path $tmpPath
    Write-Host "  Write to $tmpPath: " -NoNewline
    Write-Host ($(if ($ok) {'OK'} else {'FAILED'}))
  } catch {
    Write-Host "  Write test failed: $($_.Exception.Message)"
  } finally {
    try { Remove-Item -Force $tmpPath -ErrorAction SilentlyContinue } catch {}
  }
} else {
  Write-Host "`nWrite test: skipped (NoWrite switch set)"
}

Write-Host "`nTips:"
Write-Host "  - If shells are MISSING above, install one and add it to PATH."
Write-Host "  - Configure your CLI to use an available shell (e.g., pwsh or bash)."
Write-Host "  - On Windows, you can run with: powershell -ExecutionPolicy Bypass -File tools\\codex_diagnostics.ps1"

