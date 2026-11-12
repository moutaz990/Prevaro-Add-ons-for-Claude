# Prevaro Add-ons for Claude - one-command setup for Windows 10/11.
#
# Run in PowerShell:
#   irm https://raw.githubusercontent.com/moutaz990/Prevaro-Add-ons-for-Claude/main/install/bootstrap.ps1 | iex
#
# What it does, in order (nothing else):
#   1. Installs what is missing with winget: Git, Node.js LTS, ffmpeg. Windows may ask for permission (UAC): click Yes.
#   2. Installs Claude Code if missing (official installer from claude.ai).
#   3. Downloads (or updates) this repository into %USERPROFILE%\prevaro-addons.
#   4. Runs install\install.ps1, which checks everything again, backs up your settings and asks for optional API keys
#      (leave any key empty to skip it).
# Re-running it is safe: it updates instead of reinstalling.

& {
    $ErrorActionPreference = 'Continue'
    try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }
    $repoUrl = 'https://github.com/moutaz990/Prevaro-Add-ons-for-Claude.git'
    $dir = Join-Path $HOME 'prevaro-addons'

    function Refresh-Path {
        $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
        $local = Join-Path $HOME '.local\bin'
        if ((Test-Path $local) -and ($env:Path -notlike "*$local*")) { $env:Path += ";$local" }
    }
    function Has([string]$Name) { return [bool](Get-Command $Name -ErrorAction SilentlyContinue) }
    function WingetInstall([string]$Id, [string]$Label) {
        Write-Host "  - تثبيت $Label ..." -ForegroundColor Cyan
        & winget install --id $Id -e --source winget --accept-package-agreements --accept-source-agreements --silent
        Refresh-Path
    }

    Write-Host ''
    Write-Host '=== Prevaro Add-ons for Claude: تجهيز الجهاز ===' -ForegroundColor Cyan
    Refresh-Path

    if (-not (Has 'winget')) {
        Write-Host 'winget غير موجود. ثبّت "App Installer" من Microsoft Store ثم أعد تشغيل الأمر.' -ForegroundColor Red
        return
    }

    if (-not (Has 'git')) { WingetInstall 'Git.Git' 'Git' }
    $needNode = -not (Has 'node')
    if (-not $needNode) {
        $major = 0
        try { $major = [int](((& node --version) -replace '^v', '').Split('.')[0]) } catch { }
        if ($major -lt 22) { $needNode = $true }
    }
    if ($needNode) { WingetInstall 'OpenJS.NodeJS.LTS' 'Node.js LTS' }
    if (-not (Has 'ffmpeg')) { WingetInstall 'Gyan.FFmpeg' 'ffmpeg (للفيديو)' }

    if (-not (Has 'claude')) {
        Write-Host '  - تثبيت Claude Code ...' -ForegroundColor Cyan
        Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression
        Refresh-Path
    }

    $missing = @('git', 'node', 'claude') | Where-Object { -not (Has $_) }
    if ($missing.Count -gt 0) {
        Write-Host ("لم يكتمل تثبيت: {0}. أغلق PowerShell وافتحه من جديد ثم أعد تشغيل نفس الأمر." -f ($missing -join ', ')) -ForegroundColor Yellow
        return
    }

    if (Test-Path (Join-Path $dir '.git')) {
        Write-Host '  - تحديث الحزمة ...' -ForegroundColor Cyan
        & git -C $dir pull --ff-only
    } else {
        Write-Host '  - تنزيل الحزمة ...' -ForegroundColor Cyan
        & git clone $repoUrl $dir
    }
    if (-not (Test-Path (Join-Path $dir 'install\install.ps1'))) {
        Write-Host 'تعذّر تنزيل الحزمة. تأكد من الإنترنت ثم أعد المحاولة.' -ForegroundColor Red
        return
    }

    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $dir 'install\install.ps1')

    Write-Host ''
    Write-Host 'انتهى. افتح نافذة PowerShell جديدة واكتب: claude' -ForegroundColor Green
    Write-Host 'أول مرة سيطلب تسجيل الدخول بحساب Claude.' -ForegroundColor Green
}
