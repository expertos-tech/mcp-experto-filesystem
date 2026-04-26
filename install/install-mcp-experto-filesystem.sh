#!/usr/bin/env bash
# install-mcp-experto-filesystem.sh
#
# Installs mcp-experto-filesystem to ~/.local/mcp-experto-filesystem
# and registers it in ~/.claude/.mcp.json (merges, never overwrites).
#
# Usage:
#   bash install/install-mcp-experto-filesystem.sh

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────

SERVER_KEY="mcp-experto-filesystem"
INSTALL_DIR="${HOME}/.local/${SERVER_KEY}"
CLAUDE_DIR="${HOME}/.claude"
MCP_CONFIG="${CLAUDE_DIR}/.mcp.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "${SCRIPT_DIR}")"

# ── Helpers ───────────────────────────────────────────────────────────────

info()  { echo "[info]  $*"; }
ok()    { echo "[ok]    $*"; }
err()   { echo "[error] $*" >&2; exit 1; }

# ── Pre-flight checks ─────────────────────────────────────────────────────

command -v uv &>/dev/null      || err "uv not found. Install it: https://docs.astral.sh/uv/getting-started/installation/"
command -v python3 &>/dev/null || err "python3 not found."

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_MINOR=11

if python3 -c "import sys; exit(0 if sys.version_info >= (3, ${REQUIRED_MINOR}) else 1)" 2>/dev/null; then
    ok "Python ${PYTHON_VERSION} detected."
else
    err "Python 3.${REQUIRED_MINOR}+ is required. Found: ${PYTHON_VERSION}."
fi

# ── Summary ───────────────────────────────────────────────────────────────

echo ""
echo "  mcp-experto-filesystem installer"
echo "  ─────────────────────────────────────────────"
echo "  Source : ${REPO_ROOT}"
echo "  Target : ${INSTALL_DIR}"
echo "  Config : ${MCP_CONFIG}"
echo ""

# ── Step 1: Copy server files ─────────────────────────────────────────────

info "Copying server files..."
mkdir -p "${INSTALL_DIR}"

# Replace src/ cleanly to avoid stale files from previous installs
rm -rf "${INSTALL_DIR}/src"
cp -r "${REPO_ROOT}/src" "${INSTALL_DIR}/src"
cp "${REPO_ROOT}/pyproject.toml" "${INSTALL_DIR}/pyproject.toml"
cp "${REPO_ROOT}/README.md" "${INSTALL_DIR}/README.md"

ok "Server files copied."

# ── Step 2: Install Python dependencies ───────────────────────────────────

info "Installing Python dependencies (no dev extras)..."
uv --directory "${INSTALL_DIR}" sync --no-dev
ok "Dependencies installed."

# ── Step 3: Register in ~/.claude/.mcp.json ───────────────────────────────

info "Updating MCP config at ${MCP_CONFIG}..."
mkdir -p "${CLAUDE_DIR}"

python3 - <<PYEOF
import json, os, sys

config_path = "${MCP_CONFIG}"
install_dir = "${INSTALL_DIR}"
server_key  = "${SERVER_KEY}"

new_entry = {
    "command": "uv",
    "args": [
        "--directory", install_dir,
        "run", "python", "-m", "server"
    ]
}

config = {}
if os.path.isfile(config_path):
    try:
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"[error] {config_path} contains invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)

config.setdefault("mcpServers", {})[server_key] = new_entry

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
    f.write("\n")
PYEOF

ok "MCP config updated."

# ── Done ──────────────────────────────────────────────────────────────────

echo ""
echo "  Installation complete."
echo ""
echo "  To test the server manually:"
echo "    uv --directory '${INSTALL_DIR}' run python -m server"
echo ""
echo "  Restart Claude for the '${SERVER_KEY}' MCP server to appear in the tool list."
echo ""
