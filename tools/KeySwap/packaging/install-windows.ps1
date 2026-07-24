# KeySwap one-shot Windows install helper (AHK v2 + optional Startup)
# Usage (from sanskrit-util repo root or any cwd):
#   powershell -ExecutionPolicy Bypass -File tools\KeySwap\packaging\install-windows.ps1
#   powershell ... install-windows.ps1 -NoStartup

param(
    [switch]$NoStartup,
    [switch]$NoStart
)

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$KeySwap = Split-Path -Parent $Here
$Ahk = Join-Path $KeySwap "windows\KeySwap.ahk"
$Allow = Join-Path $KeySwap "windows\allowlist.txt"
$AllowEx = Join-Path $KeySwap "windows\allowlist.example.txt"

if (-not (Test-Path $Ahk)) {
    Write-Error "Missing $Ahk - run from a full sanskrit-util checkout."
}

if (-not (Test-Path $Allow) -and (Test-Path $AllowEx)) {
    Copy-Item $AllowEx $Allow
    Write-Host "Created allowlist.txt from example (edit to limit apps)."
}

$ahkExe = $null
foreach ($c in @(
    "${env:ProgramFiles}\AutoHotkey\v2\AutoHotkey64.exe",
    "${env:ProgramFiles}\AutoHotkey\v2\AutoHotkey.exe",
    "${env:LocalAppData}\Programs\AutoHotkey\v2\AutoHotkey64.exe",
    "${env:LocalAppData}\Programs\AutoHotkey\AutoHotkey64.exe",
    "${env:LocalAppData}\Programs\AutoHotkey\AutoHotkey32.exe",
    "${env:LocalAppData}\Programs\AutoHotkey\v2\AutoHotkey32.exe"
)) {
    if (Test-Path $c) { $ahkExe = $c; break }
}

if (-not $ahkExe) {
    Write-Host "AutoHotkey v2 not found in Program Files."
    Write-Host "Install from https://www.autohotkey.com/ then re-run, or double-click:"
    Write-Host "  $Ahk"
} else {
    Write-Host "Found AutoHotkey: $ahkExe"
}

if (-not $NoStartup -and $ahkExe) {
    $startup = [Environment]::GetFolderPath("Startup")
    $lnkPath = Join-Path $startup "KeySwap.lnk"
    $w = New-Object -ComObject WScript.Shell
    $sc = $w.CreateShortcut($lnkPath)
    $sc.TargetPath = $ahkExe
    $sc.Arguments = "`"$Ahk`""
    $sc.WorkingDirectory = Split-Path $Ahk
    $sc.Description = "KeySwap IAST typing (sanskrit-util)"
    $sc.Save()
    Write-Host "Startup shortcut: $lnkPath"
}

if (-not $NoStart) {
    if ($ahkExe) {
        Start-Process -FilePath $ahkExe -ArgumentList "`"$Ahk`""
        Write-Host "Started KeySwap (tray icon). Script mode: Ctrl+Alt+D. Gloss: Ctrl+Alt+G"
    } else {
        Start-Process $Ahk
        Write-Host "Launched via file association: $Ahk"
    }
}

Write-Host "Done. Docs: tools\KeySwap\packaging\INSTALL.md"
