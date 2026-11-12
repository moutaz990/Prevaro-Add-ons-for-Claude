#!/usr/bin/env bash
# Prevaro Add-ons for Claude — Linux / macOS installer (Windows uses install.ps1).
# Same pinned sources as install.ps1 (manifest.json).
# Usage: bash install/install.sh [--check-only] [--no-verify] [--non-interactive] [--site URL]
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
HELPER="$REPO/install/lib/kit.mjs"
MANIFEST="$REPO/manifest.json"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SETUP_DIR="$HOME/prevaro-claude-setup"
LEDGER="$SETUP_DIR/installed.json"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="$SETUP_DIR/install-log-$STAMP.md"
VERIFY_DIR="$SETUP_DIR/verify"
CHECK_ONLY=0; NO_VERIFY=0; NONINTERACTIVE=0; SITE="https://example.com"
while [ $# -gt 0 ]; do case "$1" in --check-only) CHECK_ONLY=1;; --no-verify) NO_VERIFY=1;; --non-interactive) NONINTERACTIVE=1;; --site) shift; SITE="${1:-$SITE}";; esac; shift; done

RESULTS=()
res() { RESULTS+=("| $1 | $2 | $3 | ${4:-} |"); printf '  [%s] %s %s\n' "$3" "$2" "${4:-}"; }
have() { command -v "$1" >/dev/null 2>&1; }
helper() { node "$HELPER" "$@"; }
mfield() { node -e "const m=require('$MANIFEST');const x=$1;process.stdout.write(String(x))"; }
read_secret() { local v=""; if [ "$NONINTERACTIVE" = 0 ]; then read -r -s -p "$1: " v; echo >&2; fi; printf '%s' "$v"; }

echo "=== 0. Prerequisites ==="
MISSING=()
vge() { node -e 'const [a,b]=process.argv.slice(1).map(v=>(v.match(/\d+\.\d+\.\d+/)||["0.0.0"])[0].split(".").map(Number));for(let i=0;i<3;i++){if(a[i]>b[i])process.exit(0);if(a[i]<b[i])process.exit(1)}process.exit(0)' "$1" "$2"; }
if have claude; then CCV="$(claude --version 2>/dev/null)"; if vge "$CCV" 2.1.275; then res 0 "Claude Code" OK "$CCV"; else MISSING+=("Claude Code 2.1.275+ (found $CCV): claude update"); res 0 "Claude Code" "TOO OLD" "$CCV"; fi; else MISSING+=("Claude Code (https://code.claude.com/docs)"); res 0 "Claude Code" MISSING; fi
if have node; then NV="$(node --version)"; if [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 22 ]; then MISSING+=("Node.js 22+ (found $NV)"); res 0 Node "TOO OLD" "$NV"; else res 0 Node OK "$NV"; fi; else MISSING+=("Node.js 22+"); res 0 Node MISSING; fi
if have git; then GV="$(git --version)"; if vge "$GV" 2.25.0; then res 0 git OK "$GV"; else MISSING+=("git 2.25+ (found $GV)"); res 0 git "TOO OLD" "$GV"; fi; else MISSING+=("git"); res 0 git MISSING; fi
if have ffmpeg; then res 0 ffmpeg OK; else res 0 ffmpeg MISSING "video phase skipped"; fi
if [ ${#MISSING[@]} -gt 0 ]; then printf 'Missing (required), nothing changed:\n'; printf '  - %s\n' "${MISSING[@]}"; exit 1; fi
[ "$CHECK_ONLY" = 1 ] && { echo "check-only: nothing changed"; exit 0; }
mkdir -p "$SETUP_DIR" "$VERIFY_DIR" "$CLAUDE_DIR"

echo "=== Backup ==="
helper backup "$CLAUDE_DIR" "$SETUP_DIR/backups/$STAMP" "$LEDGER" >/dev/null || { echo "backup failed"; exit 1; }
res backup "settings.json, CLAUDE.md, .claude.json" OK "$SETUP_DIR/backups/$STAMP"

skills_phase() {
  local out; out="$(helper install-skills "$MANIFEST" "$CLAUDE_DIR" "$LEDGER" "$1")" || { res "$1" skills FAILED; return; }
  while IFS=$'\t' read -r n s note; do res "$1" "skill $n" "$s" "$note"; done < <(node -e 'for (const x of JSON.parse(process.argv[1])) console.log([x.name,x.status,x.commit?"@ "+x.commit.slice(0,7):x.reason].join("\t"))' "$out")
}
mcp_add() { # phase name package version
  if claude mcp get "$2" >/dev/null 2>&1; then
    if node "$HELPER" ledger-get "$LEDGER" mcp | grep -q "\"$2\""; then claude mcp remove "$2" --scope user >/dev/null 2>&1
    else res "$1" "MCP $2" SKIPPED "already configured by someone else"; return; fi
  fi
  if claude mcp add "$2" --scope user -- npx -y "$3@$4" >/dev/null 2>&1; then helper ledger-add "$LEDGER" mcp "$2"; res "$1" "MCP $2" OK "$3@$4"; else res "$1" "MCP $2" FAILED; fi
}

echo "=== Phase 1 ==="
skills_phase 1
mcp_add 1 playwright "$(mfield 'm.mcp.find(x=>x.name==="playwright").package')" "$(mfield 'm.mcp.find(x=>x.name==="playwright").version')"

echo "=== Phase 2 ==="
skills_phase 2
HFV="$(mfield 'm.npm.find(x=>x.name==="hyperframes").version')"
NPM_G=(); NPMG_DIR="$(npm prefix -g 2>/dev/null)"
if [ -n "$NPMG_DIR" ] && [ ! -w "$NPMG_DIR/lib" ] && [ ! -w "$NPMG_DIR" ]; then
  NPM_G=(--prefix "$HOME/.npm-global"); mkdir -p "$HOME/.npm-global/bin"; export PATH="$HOME/.npm-global/bin:$PATH"
  echo "  npm global folder is not writable; installing CLI tools to ~/.npm-global (add ~/.npm-global/bin to PATH in ~/.zshrc)"
fi
if npm install -g "${NPM_G[@]+"${NPM_G[@]}"}" "hyperframes@$HFV" >/dev/null 2>&1; then helper ledger-add "$LEDGER" npm hyperframes; res 2 "hyperframes CLI" OK "$HFV"; else res 2 "hyperframes CLI" FAILED "npm install -g failed"; fi
HF_BROWSER=""
for b in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" "$(command -v google-chrome 2>/dev/null)" "$(command -v chromium 2>/dev/null)"; do
  [ -n "$b" ] && [ -x "$b" ] && { HF_BROWSER="$b"; break; }
done
[ -n "$HF_BROWSER" ] && res 2 "HyperFrames browser" OK "$HF_BROWSER" || res 2 "HyperFrames browser" SKIPPED "no Chrome/Edge found; HyperFrames downloads its own on first render"
if claude plugin install remotion@anthropic-plugin-directory >/dev/null 2>&1; then helper ledger-add "$LEDGER" plugins remotion@anthropic-plugin-directory; res 2 "Remotion plugin" OK; else res 2 "Remotion plugin" FAILED; fi
echo "  Remotion license: free for individuals and for-profit orgs up to 3 employees; otherwise a Company License (remotion.pro/license)."

echo "=== Phase 3 ==="
claude plugin marketplace add "$REPO" >/dev/null 2>&1 && helper ledger-add "$LEDGER" marketplaces prevaro-addons
if claude plugin install auto-handoff@prevaro-addons >/dev/null 2>&1; then
  helper ledger-add "$LEDGER" plugins auto-handoff@prevaro-addons
  echo '{"viewer":"off"}' | claude plugin configure auto-handoff@prevaro-addons --values-stdin >/dev/null 2>&1
  res 3 "auto-handoff plugin" OK "viewer=off"
else res 3 "auto-handoff plugin" FAILED; fi

echo "=== Phase 4 ==="
while IFS=$'\t' read -r n s note; do res 4 "agent $n" "$s" "$note"; done < <(node -e 'for (const x of JSON.parse(process.argv[1])) console.log([x.name,x.status,x.reason||""].join("\t"))' "$(helper copy-agents "$REPO/claude-home/agents" "$CLAUDE_DIR" "$LEDGER")")

echo "=== Phase 6 ==="
for pair in "firecrawl FIRECRAWL_API_KEY" "perplexity PERPLEXITY_API_KEY"; do
  set -- $pair
  if [ -z "${!2:-}" ]; then v="$(read_secret "$2 (empty = skip)")"; if [ -n "$v" ]; then export "$2=$v"; echo "  Add to your shell profile yourself: export $2=..." ; fi; fi
  if [ -z "${!2:-}" ]; then res 6 "MCP $1" SKIPPED "no API key"; continue; fi
  mcp_add 6 "$1" "$(mfield "m.mcp.find(x=>x.name===\"$1\").package")" "$(mfield "m.mcp.find(x=>x.name===\"$1\").version")"
done

echo "=== Phase 7 ==="
helper merge-settings "$CLAUDE_DIR/settings.json" "$REPO/claude-home/settings.fragment.json" "$LEDGER" >/dev/null && res 7 settings.json OK || res 7 settings.json FAILED
if [ -n "${HF_BROWSER:-}" ]; then
  HF_FRAG="$SETUP_DIR/hf-browser.fragment.json"; node -e 'require("fs").writeFileSync(process.argv[1], JSON.stringify({env:{HYPERFRAMES_BROWSER_PATH:process.argv[2]}}))' "$HF_FRAG" "$HF_BROWSER"
  helper merge-settings "$CLAUDE_DIR/settings.json" "$HF_FRAG" "$LEDGER" >/dev/null && res 7 "settings.json HYPERFRAMES_BROWSER_PATH" OK
fi
if [ ! -e "$HOME/.claudeignore" ]; then cp "$REPO/templates/.claudeignore" "$HOME/.claudeignore"; helper ledger-add "$LEDGER" files "$HOME/.claudeignore"; res 7 .claudeignore OK "documentation; enforced via permissions.deny"; else res 7 .claudeignore SKIPPED exists; fi

echo "=== CAD MCP (cad-mcp-server: open DWG/DXF, query, measure, export DXF) ==="
CAD_DIR="$SETUP_DIR/mcp/cad-mcp-server"
mkdir -p "$CAD_DIR" && for f in package.json package-lock.json selftest.mjs selftest-input.dxf; do cp "$REPO/mcp/cad-mcp-server/$f" "$CAD_DIR/"; done
if (cd "$CAD_DIR" && npm ci --ignore-scripts --no-audit --no-fund >/dev/null 2>&1); then
  helper ledger-add "$LEDGER" dirs "$CAD_DIR"
  CHANNEL=""
  if [ -d "/Applications/Google Chrome.app" ]; then CHANNEL=chrome; elif [ -d "/Applications/Microsoft Edge.app" ]; then CHANNEL=msedge; fi
  if [ -z "$CHANNEL" ]; then
    (cd "$CAD_DIR" && node node_modules/playwright/cli.js install chromium >/dev/null 2>&1) && res 10 "Chromium for cad MCP" OK "playwright 1.64.1 bundled browser" || res 10 "Chromium for cad MCP" FAILED "browser download failed"
  fi
  if claude mcp get cad >/dev/null 2>&1; then
    if node "$HELPER" ledger-get "$LEDGER" mcp | grep -q '"cad"'; then claude mcp remove cad --scope user >/dev/null 2>&1; else res 10 "MCP cad" SKIPPED "already configured by someone else"; CAD_SKIP=1; fi
  fi
  if [ -z "${CAD_SKIP:-}" ]; then
    ENVARG=(); [ -n "$CHANNEL" ] && ENVARG=(-e "PLAYWRIGHT_BROWSER_CHANNEL=$CHANNEL")
    if claude mcp add cad --scope user "${ENVARG[@]+"${ENVARG[@]}"}" -- node "$CAD_DIR/node_modules/@mlightcad/cad-mcp-server/dist/cli.js" >/dev/null 2>&1; then
      helper ledger-add "$LEDGER" mcp cad; res 10 "MCP cad" OK "@mlightcad/cad-mcp-server@1.7.8 (lockfile), browser: ${CHANNEL:-bundled chromium}"
    else res 10 "MCP cad" FAILED "claude mcp add failed"; fi
  fi
else res 10 "cad-mcp-server" FAILED "npm ci failed"; fi

if [ "$NO_VERIFY" = 0 ]; then
  echo "=== Verify ==="
  if [ -f "$CAD_DIR/selftest.mjs" ] && [ -d "$CAD_DIR/node_modules" ]; then
    if PLAYWRIGHT_BROWSER_CHANNEL="${CHANNEL:-}" node "$CAD_DIR/selftest.mjs" "$CAD_DIR/selftest-input.dxf" "$VERIFY_DIR/cad-selftest-export.dxf" > "$VERIFY_DIR/cad-selftest.txt" 2>&1; then
      res verify "cad MCP self-test (open + export DXF)" OK; else res verify "cad MCP self-test" FAILED "see $VERIFY_DIR/cad-selftest.txt"; fi
  fi
  claude mcp list > "$VERIFY_DIR/mcp-list.txt" 2>&1; claude plugin list > "$VERIFY_DIR/plugin-list.txt" 2>&1
  res verify "mcp/plugin list" OK "$VERIFY_DIR"
  for shot in "desktop --viewport-size=1440,900" "mobile --device=Pixel 7"; do
    name="${shot%% *}"; arg="${shot#* }"
    SHOT_CH=(); if [ -n "${CHANNEL:-}" ]; then SHOT_CH=(--channel "$CHANNEL"); else npx -y playwright@1.64.1 install chromium >/dev/null 2>&1; fi
    if npx -y playwright@1.64.1 screenshot "${SHOT_CH[@]+"${SHOT_CH[@]}"}" "$arg" --wait-for-timeout 3000 "$SITE" "$VERIFY_DIR/site-$name.png" >/dev/null 2>&1; then res verify "screenshot $name" OK; else res verify "screenshot $name" FAILED "network or browser (npx playwright@1.64.1 install chromium)"; fi
  done
  if have ffmpeg && have hyperframes; then
    rm -rf "$VERIFY_DIR/video-test"; cp -R "$REPO/verify/video-test" "$VERIFY_DIR/video-test"
    ( cd "$VERIFY_DIR/video-test" && npm install --no-save --silent gsap@3.15.0 >/dev/null 2>&1 && HYPERFRAMES_NO_TELEMETRY=1 HYPERFRAMES_BROWSER_PATH="${HF_BROWSER:-${HYPERFRAMES_BROWSER_PATH:-}}" hyperframes render --quality standard -o "$VERIFY_DIR/placeholder-5s.mp4" >/dev/null 2>&1 )
    if [ -f "$VERIFY_DIR/placeholder-5s.mp4" ]; then res verify "test video" OK "$(ffprobe -v error -show_entries stream=width,height:format=duration -of csv=p=0 "$VERIFY_DIR/placeholder-5s.mp4" | tr '\n' ' ')"; else res verify "test video" FAILED; fi
  fi
fi

{ echo "# Install log $STAMP"; echo; echo "| Phase | Item | Status | Note |"; echo "|---|---|---|---|"; printf '%s\n' "${RESULTS[@]}"; } > "$LOG"
echo "Log: $LOG"
