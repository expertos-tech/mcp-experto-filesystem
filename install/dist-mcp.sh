#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "${SCRIPT_DIR}")"
DIST_DIR="${SCRIPT_DIR}/dist"
PACKAGE_BASENAME="mcp-experto-filesystem"
INSTALLER_NAME="mcp-experto-filesystem-install.sh"

info() { echo "[info]  $*"; }
ok() { echo "[ok]    $*"; }
err() { echo "[error] $*" >&2; exit 1; }

command -v python3 >/dev/null 2>&1 || err "python3 not found."
command -v tar >/dev/null 2>&1 || err "tar not found."
command -v sha256sum >/dev/null 2>&1 || err "sha256sum not found."

PYPROJECT_PATH="${REPO_ROOT}/pyproject.toml"
INSTALLER_PATH="${SCRIPT_DIR}/${INSTALLER_NAME}"

[[ -f "${PYPROJECT_PATH}" ]] || err "pyproject.toml not found at ${PYPROJECT_PATH}."
[[ -f "${INSTALLER_PATH}" ]] || err "Installer not found at ${INSTALLER_PATH}."

RAW_VERSION="$(
python3 - "${PYPROJECT_PATH}" <<'PYEOF'
from pathlib import Path
import re
import sys

content = Path(sys.argv[1]).read_text(encoding="utf-8")
match = re.search(r'^version\s*=\s*"([^"]+)"', content, flags=re.MULTILINE)
if not match:
    raise SystemExit("Unable to locate project version in pyproject.toml")
print(match.group(1))
PYEOF
)"

FORMATTED_VERSION="$(
python3 - "${RAW_VERSION}" <<'PYEOF'
import re
import sys

raw_version = sys.argv[1].strip()
parts = raw_version.split(".")
if len(parts) != 3 or any(not re.fullmatch(r"\d+", part) for part in parts):
    raise SystemExit(f"Unsupported version format: {raw_version}")
print(f"v{raw_version}")
PYEOF
)"

ARCHIVE_NAME="${PACKAGE_BASENAME}.${FORMATTED_VERSION}.tar.gz"
ARCHIVE_PATH="${DIST_DIR}/${ARCHIVE_NAME}"
ARCHIVE_SHA_PATH="${ARCHIVE_PATH}.sha256"
INSTALLER_DIST_PATH="${DIST_DIR}/${INSTALLER_NAME}"
INSTALLER_SHA_PATH="${INSTALLER_DIST_PATH}.sha256"

STAGING_DIR="$(mktemp -d)"
cleanup() {
    rm -rf "${STAGING_DIR}"
}
trap cleanup EXIT

PACKAGE_ROOT="${STAGING_DIR}/${PACKAGE_BASENAME}"
mkdir -p "${PACKAGE_ROOT}/install"

info "Preparing distribution assets for version ${RAW_VERSION} (${FORMATTED_VERSION})."

cp -r "${REPO_ROOT}/src" "${PACKAGE_ROOT}/src"
cp "${REPO_ROOT}/pyproject.toml" "${PACKAGE_ROOT}/pyproject.toml"
cp "${REPO_ROOT}/README.md" "${PACKAGE_ROOT}/README.md"
cp "${INSTALLER_PATH}" "${PACKAGE_ROOT}/install/${INSTALLER_NAME}"

mkdir -p "${DIST_DIR}"
rm -f "${ARCHIVE_PATH}" "${ARCHIVE_SHA_PATH}" "${INSTALLER_DIST_PATH}" "${INSTALLER_SHA_PATH}"

info "Creating archive ${ARCHIVE_NAME}."
tar -C "${STAGING_DIR}" -czf "${ARCHIVE_PATH}" "${PACKAGE_BASENAME}"
cp "${INSTALLER_PATH}" "${INSTALLER_DIST_PATH}"

(
    cd "${DIST_DIR}"
    sha256sum "${ARCHIVE_NAME}" > "$(basename "${ARCHIVE_SHA_PATH}")"
    sha256sum "${INSTALLER_NAME}" > "$(basename "${INSTALLER_SHA_PATH}")"
)

ok "Distribution created in ${DIST_DIR}."
echo ""
echo "Artifacts:"
echo "  - ${ARCHIVE_PATH}"
echo "  - ${ARCHIVE_SHA_PATH}"
echo "  - ${INSTALLER_DIST_PATH}"
echo "  - ${INSTALLER_SHA_PATH}"
