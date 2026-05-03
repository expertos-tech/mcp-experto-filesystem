#!/usr/bin/env bash
# mcp-experto-filesystem-install.sh
#
# Installs a packaged mcp-experto-filesystem release into ~/.mcp_experto_filesystem
# and registers it in ~/.claude/.mcp.json (merges, never overwrites).
#
# Usage:
#   bash install/mcp-experto-filesystem-install.sh

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────

SERVER_KEY="mcp-experto-filesystem"
INSTALL_DIR="${HOME}/.mcp_experto_filesystem"
CLAUDE_DIR="${HOME}/.claude"
MCP_CONFIG="${CLAUDE_DIR}/.mcp.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(basename "${SCRIPT_DIR}")" == "dist" ]]; then
    DIST_DIR="${SCRIPT_DIR}"
else
    DIST_DIR="${SCRIPT_DIR}/dist"
fi
INSTALLER_BASENAME="$(basename "${BASH_SOURCE[0]}")"
INSTALLER_PATH="${SCRIPT_DIR}/${INSTALLER_BASENAME}"
INSTALLER_SHA_PATH="${DIST_DIR}/${INSTALLER_BASENAME}.sha256"

# ── Helpers ───────────────────────────────────────────────────────────────

info()  { echo "[info]  $*"; }
ok()    { echo "[ok]    $*"; }
err()   { echo "[error] $*" >&2; exit 1; }

verify_sha256() {
    local checksum_file="$1"
    local base_dir
    base_dir="$(dirname "${checksum_file}")"
    (
        cd "${base_dir}"
        sha256sum -c "$(basename "${checksum_file}")"
    )
}

# ── Pre-flight checks ─────────────────────────────────────────────────────

command -v uv &>/dev/null      || err "uv not found. Install it: https://docs.astral.sh/uv/getting-started/installation/"
command -v python3 &>/dev/null || err "python3 not found."
command -v tar &>/dev/null     || err "tar not found."
command -v sha256sum &>/dev/null || err "sha256sum not found."

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
echo "  Dist   : ${DIST_DIR}"
echo "  Target : ${INSTALL_DIR}"
echo "  Config : ${MCP_CONFIG}"
echo ""

# ── Step 1: Resolve packaged release ──────────────────────────────────────

[[ -d "${DIST_DIR}" ]] || err "Distribution directory not found at ${DIST_DIR}."
[[ -f "${INSTALLER_SHA_PATH}" ]] || err "Installer checksum not found at ${INSTALLER_SHA_PATH}."
[[ -f "${INSTALLER_PATH}" ]] || err "Installer not found at ${INSTALLER_PATH}."

PACKAGE_CANDIDATES=("${DIST_DIR}"/mcp-experto-filesystem.v*.tar.gz)
if [[ ! -e "${PACKAGE_CANDIDATES[0]}" ]]; then
    err "No packaged release found in ${DIST_DIR}."
fi

if [[ "${#PACKAGE_CANDIDATES[@]}" -ne 1 ]]; then
    err "Expected exactly one packaged release in ${DIST_DIR}, found ${#PACKAGE_CANDIDATES[@]}."
fi

ARCHIVE_PATH="${PACKAGE_CANDIDATES[0]}"
ARCHIVE_SHA_PATH="${ARCHIVE_PATH}.sha256"
ARCHIVE_BASENAME="$(basename "${ARCHIVE_PATH}")"
ARCHIVE_ROOT="mcp-experto-filesystem"
STAGING_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "${STAGING_DIR}"
}
trap cleanup EXIT

[[ -f "${ARCHIVE_SHA_PATH}" ]] || err "Archive checksum not found at ${ARCHIVE_SHA_PATH}."

info "Validating installer checksum..."
verify_sha256 "${INSTALLER_SHA_PATH}" >/dev/null
ok "Installer checksum verified."

info "Validating archive checksum for ${ARCHIVE_BASENAME}..."
verify_sha256 "${ARCHIVE_SHA_PATH}" >/dev/null
ok "Archive checksum verified."

# ── Step 2: Extract packaged release ──────────────────────────────────────

info "Extracting packaged release..."
mkdir -p "${INSTALL_DIR}"
tar -C "${STAGING_DIR}" -xzf "${ARCHIVE_PATH}"

[[ -d "${STAGING_DIR}/${ARCHIVE_ROOT}" ]] || err "Archive contents are invalid, expected ${ARCHIVE_ROOT}/ at the root."

rm -rf "${INSTALL_DIR}/src" "${INSTALL_DIR}/install"
cp -r "${STAGING_DIR}/${ARCHIVE_ROOT}/src" "${INSTALL_DIR}/src"
cp -r "${STAGING_DIR}/${ARCHIVE_ROOT}/install" "${INSTALL_DIR}/install"
cp "${STAGING_DIR}/${ARCHIVE_ROOT}/pyproject.toml" "${INSTALL_DIR}/pyproject.toml"
cp "${STAGING_DIR}/${ARCHIVE_ROOT}/README.md" "${INSTALL_DIR}/README.md"

ok "Packaged release extracted."

# ── Step 3: Install Python dependencies ───────────────────────────────────

info "Installing Python dependencies (with retrieval extras, no dev dependencies)..."
uv --directory "${INSTALL_DIR}" sync --extra retrieval --no-dev
ok "Dependencies installed."

# ── Step 4: Register in ~/.claude/.mcp.json ───────────────────────────────

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
