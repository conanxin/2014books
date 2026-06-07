#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_DIR}"

echo "=== 2014books Release Package ==="

# Ensure outputs exist
echo "Building web..."
make web

echo "Building epub..."
make epub

echo "Building pdf..."
make pdf || echo "WARNING: PDF build failed, continuing without PDF"

# Create release directory
RELEASE_DIR="${REPO_DIR}/dist/release"
mkdir -p "${RELEASE_DIR}"

# Collect files into staging
STAGE="${RELEASE_DIR}/stage"
rm -rf "${STAGE}"
mkdir -p "${STAGE}"

cp "${REPO_DIR}/README.md" "${STAGE}/"
cp "${REPO_DIR}/docs/GITHUB_PAGES_DEPLOYMENT.md" "${STAGE}/"
cp "${REPO_DIR}/docs/reports/PHASE_2014BOOKS_MODERNIZATION_A_REPORT.md" "${STAGE}/" 2>/dev/null || true
cp "${REPO_DIR}/docs/reports/PHASE_2014BOOKS_MODERNIZATION_B_REPORT.md" "${STAGE}/" 2>/dev/null || true
cp "${REPO_DIR}/docs/reports/PHASE_2014BOOKS_MODERNIZATION_C_REPORT.md" "${STAGE}/" 2>/dev/null || true
cp "${REPO_DIR}/docs/reports/PHASE_C_BOOK_GAP_AUDIT.md" "${STAGE}/" 2>/dev/null || true

if [ -f "${REPO_DIR}/dist/2014books.pdf" ]; then
    cp "${REPO_DIR}/dist/2014books.pdf" "${STAGE}/"
fi

if [ -f "${REPO_DIR}/dist/2014books.epub" ]; then
    cp "${REPO_DIR}/dist/2014books.epub" "${STAGE}/"
fi

# Copy web directory
cp -r "${REPO_DIR}/web" "${STAGE}/"

# Create zip
ZIP_FILE="${RELEASE_DIR}/2014books-phase-d-release.zip"

if command -v zip >/dev/null 2>&1; then
    rm -f "${ZIP_FILE}"
    cd "${STAGE}"
    zip -r "${ZIP_FILE}" . >/dev/null
    echo "Created: ${ZIP_FILE}"
else
    echo "WARNING: zip command not found. Install with: sudo apt-get install zip"
    echo "Release files staged at: ${STAGE}"
    exit 1
fi

# Report
echo ""
echo "=== Release Package Contents ==="
ls -lh "${ZIP_FILE}"
echo ""
echo "Done."
