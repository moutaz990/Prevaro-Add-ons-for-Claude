#Requires -Version 5.1
<#
.SYNOPSIS
  Removes everything install.ps1 added (from the ledger) and restores settings.json and CLAUDE.md
  from the first backup.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\install\uninstall.ps1
#>
[CmdletBinding()]
param([switch]$Yes)

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$Repo      = Split-Path -Parent $PSScriptRoot
$Helper    = Join-Path $PSScriptRoot 'lib\kit.mjs'
$ClaudeDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME '.claude' }
$SetupDir  = Join-Path $HOME 'prevaro-claude-setup'
$Ledger    = Join-Path $SetupDir 'installed.json'

if (-not (Test-Path $Ledger)) { Write-Host "لا يوجد سجل تثبيت: $Ledger — لا شيء لإزالته." -ForegroundColor Yellow; exit 0 }

$L = Get-Content $Ledger -Raw -Encoding UTF8 | ConvertFrom-Json
Write-Host 'سيُزال ما يلي (من سجل التثبيت):' -ForegroundColor Cyan
Write-Host "  skills:  $($L.skills -join ', ')"
Write-Host "  agents:  $($L.agents -join ', ')"
Write-Host "  plugins: $($L.plugins -join ', ')"
Write-Host "  MCP:     $($L.mcp -join ', ')"
Write-Host "  npm:     $($L.npm -join ', ')"
Write-Host "  env:     $($L.env -join ', ')"
Write-Host "  ثم استعادة settings.json و CLAUDE.md من: $($L.backup.dir)"
if (-not $Yes) {
    $a = Read-Host 'اكتب YES للمتابعة'
    if ($a -ne 'YES') { Write-Host 'أُلغي. لم يتغير شيء.' -ForegroundColor Yellow; exit 0 }
}

function Step([string]$Text, [scriptblock]$Do) {
    try {
        $global:LASTEXITCODE = 0
        & $Do
        if ($LASTEXITCODE -ne 0) { throw "exit code $LASTEXITCODE" }
        Write-Host "  [OK] $Text" -ForegroundColor Green
    } catch { Write-Host "  [FAILED] $Text : $($_.Exception.Message)" -ForegroundColor Red }
}

foreach ($p in @($L.plugins)) { if ($p) { Step "plugin uninstall $p" { & claude plugin uninstall $p 2>&1 | Out-Null } } }
foreach ($m in @($L.marketplaces)) { if ($m) { Step "marketplace remove $m" { & claude plugin marketplace remove $m 2>&1 | Out-Null } } }
foreach ($s in @($L.mcp)) { if ($s) { Step "mcp remove $s" { & claude mcp remove $s --scope user 2>&1 | Out-Null } } }
foreach ($n in @($L.npm)) { if ($n) { Step "npm uninstall -g $n" { & npm uninstall -g $n 2>&1 | Out-Null } } }

foreach ($d in @($L.dirs)) {
    if ($d -and (Test-Path $d) -and $d.StartsWith($SetupDir, [StringComparison]::OrdinalIgnoreCase)) { Step "delete $d" { Remove-Item $d -Recurse -Force } }
}
Step 'remove kit skills' { & node $Helper remove-skills $ClaudeDir $Ledger | Out-Null }
Step 'remove kit agents' { & node $Helper remove-agents $ClaudeDir $Ledger | Out-Null }
Step 'restore settings.json + CLAUDE.md from backup' { & node $Helper restore $ClaudeDir $Ledger | Out-Null }

foreach ($e in @($L.env)) { if ($e) { Step "remove user env $e" { [Environment]::SetEnvironmentVariable($e, $null, 'User') } } }

foreach ($f in @($L.files)) {
    if ($f -and (Test-Path $f) -and ((Get-Content $f -Raw) -match 'Prevaro Add-ons for Claude ignore list')) { Step "remove $f" { Remove-Item $f -Force } }
}

Step 'archive ledger' { Move-Item $Ledger (Join-Path $SetupDir ("installed-removed-{0}.json" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))) -Force }
Write-Host 'انتهت الإزالة. النسخ الاحتياطية باقية في ' -NoNewline; Write-Host (Join-Path $SetupDir 'backups') -ForegroundColor Cyan
Write-Host 'ملاحظة: ~/.claude.json لم يُستبدل (فيه بيانات أخرى)؛ أُزيلت خوادم MCP منه بالأمر claude mcp remove.' -ForegroundColor Gray
