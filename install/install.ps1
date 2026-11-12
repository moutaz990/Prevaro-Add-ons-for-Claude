#Requires -Version 5.1
<#
.SYNOPSIS
  Prevaro Add-ons for Claude: version-pinned Claude Code skills, agents, plugins and MCP servers (Windows 11).

.DESCRIPTION
  Installs the reviewed, version-pinned Claude Code environment described in manifest.json:
  skills, Playwright MCP, cad MCP, HyperFrames, Remotion plugin, auto-handoff plugin, 9 subagents,
  optional Firecrawl / Perplexity MCP and safe settings. Starts with a prerequisite check and changes nothing
  until the check passes. Backs up settings.json, CLAUDE.md and .claude.json first.

  Secrets are read with hidden input and stored ONLY as user environment variables.

.PARAMETER CheckOnly
  Only run the prerequisite check, then exit without changing anything.

.PARAMETER Site
  Website used for the desktop/mobile screenshot check (default https://example.com).

.PARAMETER NoVerify
  Skip the verification steps (screenshots, test video, provider tests).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\install\install.ps1
#>
[CmdletBinding()]
param(
    [switch]$CheckOnly,
    [string]$Site = 'https://example.com',
    [switch]$NoVerify
)

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

# ----------------------------------------------------------------------------- paths
$Repo      = Split-Path -Parent $PSScriptRoot
$Manifest  = Join-Path $Repo 'manifest.json'
$Helper    = Join-Path $PSScriptRoot 'lib\kit.mjs'
$ClaudeDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME '.claude' }
$SetupDir  = Join-Path $HOME 'prevaro-claude-setup'
$Ledger    = Join-Path $SetupDir 'installed.json'
$Stamp     = Get-Date -Format 'yyyyMMdd-HHmmss'
$Log       = Join-Path $SetupDir "install-log-$Stamp.md"
$VerifyDir = Join-Path $SetupDir 'verify'

$M = Get-Content $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
$Results = New-Object System.Collections.ArrayList

# ----------------------------------------------------------------------------- helpers
function Say([string]$Text, [string]$Color = 'Gray') { Write-Host $Text -ForegroundColor $Color }
function Section([string]$Title) { Write-Host ''; Write-Host "=== $Title ===" -ForegroundColor Cyan }

function Add-Result([string]$Phase, [string]$Item, [string]$Status, [string]$Note = '') {
    [void]$Results.Add([pscustomobject]@{ Phase = $Phase; Item = $Item; Status = $Status; Note = $Note })
    $color = switch ($Status) { 'OK' { 'Green' } 'SKIPPED' { 'Yellow' } 'MANUAL' { 'Yellow' } default { 'Red' } }
    Say ("  [{0}] {1} {2}" -f $Status, $Item, $Note) $color
}

function Invoke-Helper([string[]]$HelperArgs) {
    $out = & node $Helper @HelperArgs 2>&1
    return @{ Code = $LASTEXITCODE; Out = ($out | Out-String).Trim() }
}

function Add-Ledger([string]$Section, [string]$Value) { [void](Invoke-Helper @('ledger-add', $Ledger, $Section, $Value)) }

function Read-Secret([string]$Prompt) {
    $sec = Read-Host -Prompt $Prompt -AsSecureString
    $plain = [System.Net.NetworkCredential]::new('', $sec).Password
    if ([string]::IsNullOrWhiteSpace($plain)) { return $null }
    return $plain.Trim()
}

function Set-UserEnv([string]$Name, [string]$Value) {
    [Environment]::SetEnvironmentVariable($Name, $Value, 'User')
    Set-Item -Path "Env:$Name" -Value $Value
    Add-Ledger 'env' $Name
}

function Get-UserEnv([string]$Name) { return [Environment]::GetEnvironmentVariable($Name, 'User') }

function Ask-YesNo([string]$Prompt, [bool]$Default = $false) {
    $suffix = if ($Default) { '[Y/n]' } else { '[y/N]' }
    $a = Read-Host "$Prompt $suffix"
    if ([string]::IsNullOrWhiteSpace($a)) { return $Default }
    return $a.Trim().ToLower().StartsWith('y')
}

function Test-Cmd([string]$Name) { return [bool](Get-Command $Name -ErrorAction SilentlyContinue) }

# ----------------------------------------------------------------------------- 0. prerequisites
Section '0. فحص المتطلبات / Prerequisites'
$missingRequired = @()
$missingOptional = @()

function Get-SemVer([string]$Text) { if ($Text -match '(\d+)\.(\d+)\.(\d+)') { return [version]"$($Matches[1]).$($Matches[2]).$($Matches[3])" } return $null }
if (Test-Cmd 'claude') {
    $ccv = Get-SemVer ((& claude --version 2>$null) -join ' ')
    if ($ccv -and $ccv -lt [version]'2.1.275') { $missingRequired += "Claude Code 2.1.275+ (found $ccv) -> claude update"; Add-Result '0' 'Claude Code' 'TOO OLD' "$ccv" }
    else { Add-Result '0' 'Claude Code' 'OK' "$ccv" }
}
else { $missingRequired += 'Claude Code  -> install: irm https://claude.ai/install.ps1 | iex   (docs: https://code.claude.com/docs)'; Add-Result '0' 'Claude Code' 'MISSING' }

if (Test-Cmd 'node') {
    $nv = (& node --version).TrimStart('v'); $major = [int]($nv.Split('.')[0])
    if ($major -ge 22) { Add-Result '0' 'Node.js' 'OK' "v$nv" }
    else { $missingRequired += "Node.js 22+ (found v$nv) -> winget install OpenJS.NodeJS.LTS"; Add-Result '0' 'Node.js' 'TOO OLD' "v$nv" }
} else { $missingRequired += 'Node.js 22+ -> winget install OpenJS.NodeJS.LTS'; Add-Result '0' 'Node.js' 'MISSING' }

if (Test-Cmd 'git') {
    $gv = Get-SemVer ((& git --version) -join ' ')
    if ($gv -and $gv -lt [version]'2.25.0') { $missingRequired += "git 2.25+ (found $gv) -> winget upgrade Git.Git"; Add-Result '0' 'git' 'TOO OLD' "$gv" }
    else { Add-Result '0' 'git' 'OK' "$gv" }
}
else { $missingRequired += 'git -> winget install Git.Git'; Add-Result '0' 'git' 'MISSING' }

$gitBash = @("$env:ProgramFiles\Git\bin\bash.exe", "${env:ProgramFiles(x86)}\Git\bin\bash.exe", $env:CLAUDE_CODE_GIT_BASH_PATH) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if ($gitBash) { Add-Result '0' 'Git Bash (hooks)' 'OK' $gitBash }
else { $missingOptional += 'Git Bash (comes with Git for Windows) - needed by plugin hooks'; Add-Result '0' 'Git Bash (hooks)' 'MISSING' 'hooks of taste-skill/auto-handoff will not run' }

if (Test-Cmd 'ffmpeg') { Add-Result '0' 'ffmpeg' 'OK' (((& ffmpeg -version 2>$null) | Select-Object -First 1) -replace 'Copyright.*', '') }
else { $missingOptional += 'ffmpeg (video phase) -> winget install Gyan.FFmpeg'; Add-Result '0' 'ffmpeg' 'MISSING' 'video phase will be skipped' }

if ($missingRequired.Count -gt 0) {
    Say ''
    Say 'ينقص الجهاز ما يلي (مطلوب) — لم يتغير شيء على الجهاز:' 'Red'
    $missingRequired | ForEach-Object { Say "  - $_" 'Red' }
    if ($missingOptional.Count) { Say 'اختياري:' 'Yellow'; $missingOptional | ForEach-Object { Say "  - $_" 'Yellow' } }
    Say 'ثبّت الناقص ثم افتح نافذة PowerShell جديدة وأعد تشغيل السكربت.' 'Yellow'
    exit 1
}
if ($missingOptional.Count) { Say 'اختياري ناقص:' 'Yellow'; $missingOptional | ForEach-Object { Say "  - $_" 'Yellow' } }
if ($CheckOnly) { Say 'CheckOnly: انتهى الفحص، لم يتغير شيء.' 'Green'; exit 0 }

$hasFfmpeg = Test-Cmd 'ffmpeg'
$HfBrowser = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe", "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe", "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe") | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
New-Item -ItemType Directory -Force -Path $SetupDir, $VerifyDir, $ClaudeDir | Out-Null

# ----------------------------------------------------------------------------- backup
Section 'نسخة احتياطية / Backup'
$bk = Invoke-Helper @('backup', $ClaudeDir, (Join-Path $SetupDir "backups\$Stamp"), $Ledger)
if ($bk.Code -ne 0) { Say "Backup failed, stopping: $($bk.Out)" 'Red'; exit 1 }
Add-Result 'backup' "settings.json, CLAUDE.md, .claude.json" 'OK' (Join-Path $SetupDir "backups\$Stamp")

function Install-SkillsPhase([string]$Phase) {
    $r = Invoke-Helper @('install-skills', $Manifest, $ClaudeDir, $Ledger, $Phase)
    if ($r.Code -ne 0) { Add-Result $Phase 'skills' 'FAILED' $r.Out; return }
    try {
        foreach ($x in ($r.Out | ConvertFrom-Json)) {
            $note = if ($x.commit) { "@ $($x.commit.Substring(0,7))" } else { $x.reason }
            Add-Result $Phase "skill $($x.name)" $x.status $note
        }
    } catch { Add-Result $Phase 'skills' 'FAILED' $r.Out }
}

function Add-McpServer([string]$Phase, [string]$Name, [string]$Package, [string]$Version) {
    $ours = $false
    if (Test-Path $Ledger) { try { $ours = @((Get-Content $Ledger -Raw -Encoding UTF8 | ConvertFrom-Json).mcp) -contains $Name } catch { } }
    & claude mcp get $Name *> $null
    if ($LASTEXITCODE -eq 0) {
        if (-not $ours) { Add-Result $Phase "MCP $Name" 'SKIPPED' 'already configured by someone else (left unchanged)'; return }
        & claude mcp remove $Name --scope user *> $null   # ours: re-add at the pinned version
    }
    & claude mcp add $Name --scope user -- cmd /c npx -y "$Package@$Version" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Add-Ledger 'mcp' $Name; Add-Result $Phase "MCP $Name" 'OK' "$Package@$Version" }
    else { Add-Result $Phase "MCP $Name" 'FAILED' 'claude mcp add returned an error' }
}

function Get-PluginVersion([string]$Id) {
    try {
        $j = (& claude plugin list --json 2>$null | Out-String) | ConvertFrom-Json
        $items = if ($j.installed) { $j.installed } else { $j }
        $p = $items | Where-Object { $_.pluginId -eq $Id -or $_.id -eq $Id } | Select-Object -First 1
        return $p.version
    } catch { return $null }
}

# ----------------------------------------------------------------------------- phase 1
Section 'المرحلة 1 — تصميم المواقع'
Install-SkillsPhase '1'
$pw = $M.mcp | Where-Object { $_.name -eq 'playwright' }
Add-McpServer '1' 'playwright' $pw.package $pw.version

# ----------------------------------------------------------------------------- phase 2
Section 'المرحلة 2 — الفيديو والموشن'
Install-SkillsPhase '2'
$hf = $M.npm | Where-Object { $_.name -eq 'hyperframes' }
& npm ls -g --depth=0 hyperframes *> $null; $preHf = ($LASTEXITCODE -eq 0)
& npm install -g "hyperframes@$($hf.version)" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { if (-not $preHf) { Add-Ledger 'npm' 'hyperframes' }; Add-Result '2' 'hyperframes CLI' 'OK' $hf.version } else { Add-Result '2' 'hyperframes CLI' 'FAILED' 'npm install failed' }
Set-UserEnv 'HYPERFRAMES_NO_TELEMETRY' '1'
Set-UserEnv 'HYPERFRAMES_SKIP_SKILLS' '1'
if ($HfBrowser) { Set-UserEnv 'HYPERFRAMES_BROWSER_PATH' $HfBrowser; Add-Result '2' 'HyperFrames browser' 'OK' $HfBrowser }
else { Add-Result '2' 'HyperFrames browser' 'SKIPPED' 'no Chrome/Edge found; HyperFrames will download its own on first render' }

$rem = $M.plugins | Where-Object { $_.id -like 'remotion@*' }
$preRem = Get-PluginVersion $rem.id
if ($preRem) { Add-Result '2' 'Remotion plugin' 'SKIPPED' "already installed (v$preRem), left unchanged" }
else { & claude plugin install $rem.id 2>&1 | Out-Null }
if ($preRem) { }
elseif ($LASTEXITCODE -eq 0) {
    Add-Ledger 'plugins' $rem.id
    $v = Get-PluginVersion $rem.id
    if ($v -and $v -notlike "$($rem.expectedVersion)*") { Add-Result '2' 'Remotion plugin' 'OK' "installed $v (reviewed: $($rem.expectedVersion)) - review the difference" }
    else { Add-Result '2' 'Remotion plugin' 'OK' "v$($rem.expectedVersion)" }
} else { Add-Result '2' 'Remotion plugin' 'FAILED' 'claude plugin install failed' }
Say '  تنبيه رخصة Remotion (LICENSE.md في remotion-dev/remotion): مجاني للأفراد وللشركات الربحية حتى 3 موظفين.' 'Yellow'
Say '  أكثر من 3 موظفين = Company License مدفوعة (remotion.pro/license). قرّر قبل أول استخدام تجاري.' 'Yellow'

# ----------------------------------------------------------------------------- phase 3
Section 'المرحلة 3 — حماية السياق'
& claude plugin marketplace add $Repo 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Add-Ledger 'marketplaces' 'prevaro-addons' }
$ah = $M.plugins | Where-Object { $_.id -like 'auto-handoff@*' }
& claude plugin install $ah.id 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Add-Ledger 'plugins' $ah.id
    '{"viewer":"off"}' | & claude plugin configure $ah.id --values-stdin 2>&1 | Out-Null
    Add-Result '3' 'auto-handoff plugin' 'OK' "v$($ah.expectedVersion) @ $($ah.sourceSha.Substring(0,7)), viewer=off"
} else { Add-Result '3' 'auto-handoff plugin' 'FAILED' 'claude plugin install failed' }
Add-Result '3' 'Built-in: /context /compact /rewind /resume /export, autoCompactEnabled' 'OK' 'verified in Claude Code 2.1.322'

# ----------------------------------------------------------------------------- phase 4
Section 'المرحلة 4 — الوكلاء الفرعيون'
$ag = Invoke-Helper @('copy-agents', (Join-Path $Repo 'claude-home\agents'), $ClaudeDir, $Ledger)
if ($ag.Code -eq 0) { foreach ($x in ($ag.Out | ConvertFrom-Json)) { Add-Result '4' "agent $($x.name)" $x.status $x.reason } }
else { Add-Result '4' 'agents' 'FAILED' $ag.Out }

# ----------------------------------------------------------------------------- phase 6
Section 'المرحلة 6 — بحث وسحب بيانات (اختياري، يحتاج مفتاحاً)'
foreach ($s in @(@{ Name = 'firecrawl'; Env = 'FIRECRAWL_API_KEY' }, @{ Name = 'perplexity'; Env = 'PERPLEXITY_API_KEY' })) {
    $have = [bool](Get-UserEnv $s.Env)
    $v = Read-Secret ("  {0}{1} (فارغ = تخطٍ)" -f $s.Env, $(if ($have) { ' [محفوظ — Enter للإبقاء]' } else { '' }))
    if ($v) { Set-UserEnv $s.Env $v; $have = $true }
    if (-not $have) { Add-Result '6' "MCP $($s.Name)" 'SKIPPED' 'no API key'; continue }
    if (-not (Get-Item -Path "Env:$($s.Env)" -ErrorAction SilentlyContinue)) { Set-Item -Path "Env:$($s.Env)" -Value (Get-UserEnv $s.Env) }
    $cfg = $M.mcp | Where-Object { $_.name -eq $s.Name }
    Add-McpServer '6' $s.Name $cfg.package $cfg.version
}

# ----------------------------------------------------------------------------- phase 7
Section 'المرحلة 7 — الإعدادات'
$st = Invoke-Helper @('merge-settings', (Join-Path $ClaudeDir 'settings.json'), (Join-Path $Repo 'claude-home\settings.fragment.json'), $Ledger)
Add-Result '7' 'settings.json' $(if ($st.Code -eq 0) { 'OK' } else { 'FAILED' }) 'env + permissions.deny (ignore list) + autoCompactEnabled'
$ci = Join-Path $HOME '.claudeignore'
if (-not (Test-Path $ci)) { Copy-Item (Join-Path $Repo 'templates\.claudeignore') $ci; Add-Ledger 'files' $ci; Add-Result '7' '.claudeignore' 'OK' 'documentation only; enforced via permissions.deny' }
else { Add-Result '7' '.claudeignore' 'SKIPPED' 'already exists' }

# ----------------------------------------------------------------------------- cad MCP (phase 10)
Section 'خادم CAD (فتح DWG/DXF، استعلام، قياس، تصدير DXF)'
$CadDir = Join-Path $SetupDir 'mcp\cad-mcp-server'
New-Item -ItemType Directory -Force -Path $CadDir | Out-Null
foreach ($f in 'package.json', 'package-lock.json', 'selftest.mjs', 'selftest-input.dxf') { Copy-Item (Join-Path $Repo "mcp\cad-mcp-server\$f") $CadDir -Force }
Push-Location $CadDir
& npm ci --ignore-scripts --no-audit --no-fund 2>&1 | Out-Null
$ciOk = ($LASTEXITCODE -eq 0)
Pop-Location
if (-not $ciOk) { Add-Result '10' 'cad-mcp-server' 'FAILED' 'npm ci failed' }
else {
    Add-Ledger 'dirs' $CadDir
    $cadOurs = $false
    if (Test-Path $Ledger) { try { $cadOurs = @((Get-Content $Ledger -Raw -Encoding UTF8 | ConvertFrom-Json).mcp) -contains 'cad' } catch { } }
    & claude mcp get cad *> $null
    $cadExists = ($LASTEXITCODE -eq 0)
    if ($cadExists -and -not $cadOurs) { Add-Result '10' 'MCP cad' 'SKIPPED' 'already configured by someone else (left unchanged)' }
    else {
        if ($cadExists) { & claude mcp remove cad --scope user *> $null }
        # Microsoft Edge ships with Windows 11: Playwright drives it, no Chromium download.
        & claude mcp add cad --scope user -e PLAYWRIGHT_BROWSER_CHANNEL=msedge -- node (Join-Path $CadDir 'node_modules\@mlightcad\cad-mcp-server\dist\cli.js') 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { Add-Ledger 'mcp' 'cad'; Add-Result '10' 'MCP cad' 'OK' '@mlightcad/cad-mcp-server@1.7.8 (lockfile), headless Edge' }
        else { Add-Result '10' 'MCP cad' 'FAILED' 'claude mcp add failed' }
    }
    if (-not $NoVerify) {
        $fx = Join-Path $CadDir 'selftest-input.dxf'; $fxOut = Join-Path $VerifyDir 'cad-selftest-export.dxf'
        $env:PLAYWRIGHT_BROWSER_CHANNEL = 'msedge'
        $st = & node (Join-Path $CadDir 'selftest.mjs') $fx $fxOut 2>&1 | Out-String
        Remove-Item Env:PLAYWRIGHT_BROWSER_CHANNEL -ErrorAction SilentlyContinue
        if ($LASTEXITCODE -eq 0) { Add-Result 'verify' 'cad MCP self-test (open + export DXF)' 'OK' $fxOut }
        else { Add-Result 'verify' 'cad MCP self-test' 'FAILED' (($st -split "`n" | Select-Object -Last 2) -join ' ') }
    }
}

# ----------------------------------------------------------------------------- verification
if (-not $NoVerify) {
    Section 'التحقق على جهاز المالك / Verification'
    & claude mcp list 2>&1 | Out-File -Encoding utf8 (Join-Path $VerifyDir 'mcp-list.txt')
    & claude plugin list 2>&1 | Out-File -Encoding utf8 (Join-Path $VerifyDir 'plugin-list.txt')
    Add-Result 'verify' 'claude mcp list / plugin list' 'OK' 'see verify\mcp-list.txt, verify\plugin-list.txt'

    # Website screenshots with Microsoft Edge (preinstalled on Windows 11): no browser download.
    $pwv = '1.64.1'
    foreach ($shot in @(@{ Name = 'desktop'; Args = @('--viewport-size=1440,900') }, @{ Name = 'mobile'; Args = @('--device=Pixel 7') })) {
        $out = Join-Path $VerifyDir "site-$($shot.Name).png"
        & npx -y "playwright@$pwv" screenshot --channel msedge @($shot.Args) --wait-for-timeout 3000 $Site $out 2>&1 | Out-Null
        if (Test-Path $out) { Add-Result 'verify' "screenshot $($shot.Name)" 'OK' $out } else { Add-Result 'verify' "screenshot $($shot.Name)" 'FAILED' 'playwright screenshot failed' }
    }

    # 5-second 1080p test video with a placeholder logo.
    if ($hasFfmpeg -and (Test-Cmd 'hyperframes')) {
        $vt = Join-Path $VerifyDir 'video-test'
        Remove-Item $vt -Recurse -Force -ErrorAction SilentlyContinue
        Copy-Item (Join-Path $Repo 'verify\video-test') $vt -Recurse
        Push-Location $vt
        & npm install --no-save --silent gsap@3.15.0 2>&1 | Out-Null
        $mp4 = Join-Path $VerifyDir 'placeholder-5s.mp4'
        & hyperframes render --quality standard -o $mp4 2>&1 | Out-Null
        Pop-Location
        if (Test-Path $mp4) {
            $probe = (& ffprobe -v error -select_streams v:0 -show_entries stream=width,height:format=duration -of csv=p=0 $mp4) -join ' '
            Add-Result 'verify' 'test video 5s 1080p' 'OK' "$probe -> $mp4"
        } else { Add-Result 'verify' 'test video 5s 1080p' 'FAILED' 'render failed' }
    } else { Add-Result 'verify' 'test video 5s 1080p' 'SKIPPED' 'ffmpeg or hyperframes missing' }
}

# ----------------------------------------------------------------------------- summary
Section 'الملخص / Summary'
$lines = @("# Install log $Stamp", '', "Repo: $Repo", "Claude dir: $ClaudeDir", '', '| Phase | Item | Status | Note |', '|---|---|---|---|')
foreach ($r in $Results) { $lines += "| $($r.Phase) | $($r.Item) | $($r.Status) | $($r.Note -replace '\|','/') |" }
$lines | Out-File -Encoding utf8 $Log
$Results | Format-Table -AutoSize Phase, Item, Status
$failed = @($Results | Where-Object { $_.Status -notin @('OK', 'SKIPPED', 'MANUAL') })
Say "السجل الكامل: $Log" 'Cyan'
if ($failed.Count) { Say "بنود فشلت: $($failed.Count) — راجع السجل. باقي البنود ثُبّتت." 'Yellow' } else { Say 'اكتمل التثبيت.' 'Green' }
Say 'افتح نافذة PowerShell جديدة ثم شغّل: claude' 'Green'
Say 'للإزالة: powershell -ExecutionPolicy Bypass -File install\uninstall.ps1' 'Gray'
