# PHASE_2014BOOKS_MODERNIZATION_B_REPORT.md

## STATUS

PASS (with known content gap: 97/100 books)

## HOST_SCOPE

WSL2 Ubuntu local environment

## REPO_DIR

/home/conanxin/projects/2014books

## BRANCH

phase/2014books-modernization-b

## BASE_COMMIT

56cec4671503a30c25e8af4a093b987ca89b9d06 Phase A: modernize 2014books build and web output

## FINAL_COMMIT

8da877ae7511113116ee9e73487de4384abc5fe2 Phase B: harden PDF build and audit book extraction

## FILES_CHANGED

- `docs/reports/PHASE_2014BOOKS_MODERNIZATION_A_REPORT.md` — modified: FINAL_COMMIT placeholder fixed
- `template/template.tex` — modified: font fallback chain (Noto Serif CJK SC → AR PL SungtiL GB → WenQuanYi Zen Hei), cover fallback with \IfFileExists
- `template/template-win.tex` — modified: same font fallback + cover fallback for Windows template
- `scripts/generate_web.py` — modified: added parse_appendix(), books.json now sourced from appendix, structured output with id/title/author/raw/source/confidence
- `web/index.html` — regenerated: displays "当前已结构化整理 97 本"
- `web/data/books.json` — regenerated: 97 structured book entries from appendix
- `web/assets/style.css` — unchanged
- `dist/2014books.pdf` — regenerated: 97 pages, 1.7MB
- `2014books.pdf` — regenerated: root copy

## DEPENDENCY_STATUS

| Tool | Status | Version/Path |
|------|--------|-------------|
| pandoc | PASS | /usr/bin/pandoc 3.1.3 |
| xelatex | PASS | /usr/bin/xelatex (texlive 2023) |
| Noto Serif CJK SC | PASS | /usr/share/fonts/opentype/noto/ |
| Noto Sans CJK SC | PASS | /usr/share/fonts/opentype/noto/ |
| WenQuanYi Micro Hei | PASS | /usr/share/fonts/truetype/wqy/ |
| WenQuanYi Zen Hei | PASS | /usr/share/fonts/truetype/wqy/ |
| AR PL SungtiL GB | NOT_FOUND | Only AR PL UMing available |

Installation: `sudo apt-get install pandoc texlive-xetex texlive-latex-recommended texlive-latex-extra texlive-lang-chinese fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei` — completed after dpkg recovery.

## PDF_BUILD_STATUS

PASS

- `make pdf` completed successfully
- `dist/2014books.pdf` exists (1,728,933 bytes)
- `2014books.pdf` root copy exists
- pdfinfo: 97 pages, A4, PDF 1.5, xdvipdfmx producer
- Overfull hbox warning at lines 241-242 (cover page, non-critical)

## FONT_FALLBACK_STATUS

PASS

- template.tex: \IfFontExistsTF chain — Noto Serif CJK SC → AR PL SungtiL GB → WenQuanYi Zen Hei
- template.tex: \IfFontExistsTF for monospace — Noto Sans CJK SC → WenQuanYi Zen Hei Mono
- template-win.tex: same chain with Microsoft YaHei / Microsoft JhengHei as first priority
- All fonts resolved to Noto CJK variants on this host

## COVER_FALLBACK_STATUS

PASS

- Both templates use \IfFileExists{img/cover.pdf}
- If cover exists: \includegraphics[scale=0.8]{img/cover.pdf}
- If cover missing: generates text cover with title, author, project name, source attribution
- Cover file present at contents/img/cover.pdf and latex/img/cover.pdf

## WEB_BUILD_STATUS

PASS

- `python3 scripts/generate_web.py` — PASS
- `make web` — PASS
- `web/index.html` exists and displays correct book count
- `web/data/books.json` exists with structured entries
- Search/filter functionality preserved
- Mobile responsive CSS intact
- No external CDN dependencies

## BOOK_EXTRACTION_STATUS

IMPROVED (73 → 97)

### Root Cause Analysis

Original count of 73 was caused by:
1. `generate_web.py` only parsed `**《title》**` format from chapter files
2. Appendix file (`contents/2-appendix1-sample.markdown`) was completely ignored
3. Chapters 19 and 45 contain no bold book titles, causing under-counting
4. Some chapter titles differ from appendix titles (punctuation variants: `：` vs `——` vs `—`)

### Fix Applied

- Added `parse_appendix()` function to extract numbered list entries
- Appendix format: `1、title author` (space-separated title and author)
- `books.json` now sourced from appendix as authoritative list
- Each entry includes: `id`, `title`, `author`, `raw`, `source`, `confidence`

### Confidence Levels

- `high`: author successfully extracted (space split, author ≤ 25 chars)
- `medium`: author extraction failed or ambiguous (e.g. entry #97 "城市之王：纽约市市长朱利安ni")

### Remaining Gap

- Target: 100 books (project title claims "100本")
- Actual appendix entries: 97
- Missing 3 books: not present in the appendix file `contents/2-appendix1-sample.markdown`
- The appendix file ends at entry #97 with no indication of entries 98-100
- Possible explanations:
  - Original magazine feature had 100 books but 3 were omitted during transcription
  - The "100" in the title is approximate/marketing rounding
  - 3 books exist in chapter text but were never added to the appendix

## BOOK_COUNT_BEFORE

73 (from chapter bold-title parsing only)

## BOOK_COUNT_AFTER

97 (from appendix authoritative list)

## VALIDATION_RESULTS

| Check | Result |
|-------|--------|
| `bash -n mmd2bok` | PASS |
| `bash -n scripts/build_pdf.sh` | PASS |
| `python3 -m py_compile scripts/generate_web.py` | PASS |
| `python3 scripts/generate_web.py` | PASS (97 books) |
| `make web` | PASS |
| `make pdf` | PASS (97 pages, 1.7MB) |
| `web/index.html` exists | PASS |
| `web/data/books.json` exists | PASS |
| `dist/2014books.pdf` exists | PASS |
| `2014books.pdf` exists | PASS |
| Font fallback in template.tex | PASS |
| Cover fallback in template.tex | PASS |
| books.json schema (id/title/author/raw/source/confidence) | PASS |

## PUSHED

Yes — pushed to origin/phase/2014books-modernization-b

## RECOMMENDED_NEXT_PHASE

**Phase C: Content Gap Resolution & EPUB Support**

- Investigate the missing 3 books (target 100 vs actual 97)
  - Check if any books in chapter text are not reflected in appendix
  - Cross-reference with original 第一财经周刊 source if available
- Add EPUB generation support (`make epub`)
- Add GitHub Actions CI workflow for automated PDF + web build on push
- Consider adding book cover images or ISBN metadata if available
