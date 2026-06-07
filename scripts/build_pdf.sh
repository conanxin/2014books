#!/bin/bash
set -euo pipefail

# Resolve repo root from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

# Dependency checks
MISSING=()
if ! command -v pandoc &>/dev/null; then
    MISSING+=("pandoc")
fi
if ! command -v xelatex &>/dev/null; then
    MISSING+=("xelatex (texlive-xetex)")
fi

if [ ${#MISSING[@]} -ne 0 ]; then
    echo "ERROR: Missing required tools:" >&2
    for m in "${MISSING[@]}"; do
        echo "  - ${m}" >&2
    done
    echo "Install with (Ubuntu/Debian):" >&2
    echo "  sudo apt-get install pandoc texlive-xetex texlive-latex-recommended texlive-latex-extra" >&2
    exit 1
fi

# Build via legacy mmd2bok (it handles latex/ subdir and sorting)
bash ./mmd2bok

echo "PDF build complete."
