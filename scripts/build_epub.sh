#!/usr/bin/env bash
set -euo pipefail

# build_epub.sh — Build EPUB from markdown sources using pandoc
# Usage: bash scripts/build_epub.sh [repo_root]

REPO_DIR="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
CONTENTS_DIR="$REPO_DIR/contents"
DIST_DIR="$REPO_DIR/dist"

cd "$REPO_DIR"

# Dependency check
if ! command -v pandoc &> /dev/null; then
    echo "ERROR: pandoc not found. Install with: sudo apt-get install pandoc" >&2
    exit 1
fi

mkdir -p "$DIST_DIR"

# Collect source files in natural order
mapfile -t PREFACE_FILES < <(ls -1 "$CONTENTS_DIR"/0-preface*.markdown 2>/dev/null | sort -V)
mapfile -t CHAPTER_FILES < <(ls -1 "$CONTENTS_DIR"/1-chapter*.markdown 2>/dev/null | sort -V)
mapfile -t APPENDIX_FILES < <(ls -1 "$CONTENTS_DIR"/2-appendix*.markdown 2>/dev/null | sort -V)

SOURCE_FILES=("${PREFACE_FILES[@]}" "${CHAPTER_FILES[@]}" "${APPENDIX_FILES[@]}")

if [ ${#SOURCE_FILES[@]} -eq 0 ]; then
    echo "ERROR: No markdown source files found in $CONTENTS_DIR" >&2
    exit 1
fi

echo "Building EPUB from ${#SOURCE_FILES[@]} source files..."

# Build EPUB with pandoc
pandoc \
    --from markdown \
    --to epub \
    --output "$DIST_DIR/2014books.epub" \
    --metadata title="2014年值得你阅读的100本书" \
    --metadata author="Conan Xin" \
    --metadata lang="zh-CN" \
    --toc \
    --toc-depth=2 \
    "${SOURCE_FILES[@]}"

echo "EPUB built at $DIST_DIR/2014books.epub"
ls -lh "$DIST_DIR/2014books.epub"
