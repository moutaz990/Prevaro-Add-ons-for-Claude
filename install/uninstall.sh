#!/usr/bin/env bash
# Removes what install.sh added (from the ledger) and restores settings.json / CLAUDE.md from the first backup.
# Usage: bash install/uninstall.sh [--yes]
set -u
REPO="$(cd "$(dirname "$0")/.." && pwd)"
HELPER="$REPO/install/lib/kit.mjs"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SETUP_DIR="$HOME/prevaro-claude-setup"
LEDGER="$SETUP_DIR/installed.json"
[ -f "$LEDGER" ] || { echo "No ledger at $LEDGER: nothing to remove."; exit 0; }
get() { node "$HELPER" ledger-get "$LEDGER" "$1" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{for(const x of JSON.parse(s)||[])console.log(x)})'; }
if [ "${1:-}" != "--yes" ]; then read -r -p "Type YES to remove Prevaro Add-ons for Claude components: " a; [ "$a" = "YES" ] || { echo "Cancelled."; exit 0; }; fi
step() { if "$@" >/dev/null 2>&1; then echo "  [OK] $*"; else echo "  [FAILED] $*"; fi; }
while read -r p; do [ -n "$p" ] && step claude plugin uninstall "$p"; done < <(get plugins)
while read -r m; do [ -n "$m" ] && step claude plugin marketplace remove "$m"; done < <(get marketplaces)
while read -r s; do [ -n "$s" ] && step claude mcp remove "$s" --scope user; done < <(get mcp)
while read -r n; do [ -n "$n" ] && step npm uninstall -g "$n"; done < <(get npm)
while read -r d; do case "$d" in "$SETUP_DIR"/*) [ -d "$d" ] && step rm -rf "$d";; esac; done < <(get dirs)
step node "$HELPER" remove-skills "$CLAUDE_DIR" "$LEDGER"
step node "$HELPER" remove-agents "$CLAUDE_DIR" "$LEDGER"
step node "$HELPER" restore "$CLAUDE_DIR" "$LEDGER"
while read -r f; do [ -n "$f" ] && grep -q "Prevaro Add-ons for Claude ignore list" "$f" 2>/dev/null && step rm -f "$f"; done < <(get files)
mv "$LEDGER" "$SETUP_DIR/installed-removed-$(date +%Y%m%d-%H%M%S).json"
echo "Done. Backups kept in $SETUP_DIR/backups"
