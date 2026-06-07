# 2014books Phase F — Magazine Reading System Upgrade

## STATUS

PASS

## HOST_SCOPE

Local WSL2 development environment.

## REPO_DIR

/home/conanxin/projects/2014books

## BRANCH

phase/2014books-reading-system-f

## IMPLEMENTATION_COMMIT

(To be filled after implementation commit)

## DESIGN_PROBLEMS_IDENTIFIED

1. Single-page full text: all 45 chapters stacked in one HTML file. Mobile loading and scrolling burden is severe.
2. No per-chapter URLs: readers cannot share "I am reading this chapter" state.
3. No reading progress awareness: readers do not know where they are in a chapter.
4. No reading preference memory: font size and theme reset on every visit.
5. Mobile navigation is poor: long chapter list is hard to use on small screens.
6. No thematic guidance: readers must read all 45 chapters sequentially or guess which ones matter to them.
7. No social sharing preview: links shared on social media have no visual card.

## DESIGN_RATIONALE

Phase E solved visual style. Phase F solves long-form reading ergonomics.

- Independent chapter pages give each chapter a shareable URL and lighter page weight.
- Reading progress bar provides immediate visual feedback without external libraries.
- Reading mode (font size + paper/night) persists to localStorage so preferences survive sessions.
- Mobile drawer keeps navigation accessible without cluttering the small viewport.
- Reading paths offer thematic entry points without forcing sequential reading.
- OG cover SVG ensures shareable links have consistent preview cards.
- The 97-book fact remains unchanged; no low-confidence candidates are merged into the authoritative list.

## FILES_CHANGED

- scripts/generate_web.py (rewritten: chapter pages, progress bar, reading mode, drawer, OG tags, reading paths)
- web/assets/style.css (regenerated: chapter-page styles, progress bar, drawer, night mode, reading paths)
- web/assets/og-cover.svg (new)
- web/chapters/chapter-01.html ~ chapter-45.html (new, 45 files)
- web/index.html (regenerated: links to chapter pages, reading paths section, OG tags)
- web/data/books.json (regenerated)
- data/reading_paths.json (new)
- docs/reports/PHASE_F_READING_SYSTEM_DESIGN_NOTES.md (new)
- docs/reports/PHASE_2014BOOKS_READING_SYSTEM_F_REPORT.md (new)
- README.md (updated)

## CHAPTER_PAGE_STATUS

PASS — 45 independent chapter pages generated.

## READING_PROGRESS_STATUS

PASS — Fixed top progress bar (3px, accent color), native JS scroll listener, no external dependencies.

## READING_MODE_STATUS

PASS — A-/A+ buttons adjust font size (14–24px clamp), paper/night toggle switches CSS variables, preferences saved to localStorage and restored on load. Night mode uses dark warm gray (#1e1e1e) background, not pure black.

## MOBILE_NAV_STATUS

PASS — "目录" button opens left drawer with all 45 chapters. Overlay click and × button close drawer. Drawer items highlight current chapter.

## READING_PATHS_STATUS

PASS — 4 initial paths created (business-investing, tech-internet, enterprise-organization, history-society-modernity). Each has title, description, book_titles from reliable sources, and chapter_ids. Displayed on home page in 2-column grid (1-column on mobile).

## BOOK_ARCHIVE_STATUS

PASS — Book archive retains 97 authoritative books from appendix. Search unchanged. Confidence badges styled (high/medium/low with color coding). Tags display from metadata overrides if present.

## OG_SHARE_STATUS

PASS — og-cover.svg generated (1200×630, magazine-style: paper background, accent border, "2014 / 年度阅读特刊 / 97 BOOKS VERIFIED"). Home page and every chapter page include og:title, og:description, og:type, og:image, twitter:card. Image URL uses absolute GitHub Pages path.

## WEB_BUILD_STATUS

PASS — python3 scripts/generate_web.py exits 0. All expected files present.

## PDF_COMPATIBILITY_STATUS

PASS — make pdf produces dist/2014books.pdf. PDF build logic unchanged; Phase F only touches web generation.

## EPUB_COMPATIBILITY_STATUS

PASS — make epub produces dist/2014books.epub. EPUB build logic unchanged.

## VALIDATION_RESULTS

| Check | Result |
|-------|--------|
| python3 -m py_compile scripts/generate_web.py | PASS |
| python3 scripts/generate_web.py | PASS (45 chapters, 97 books) |
| make web | PASS |
| make pdf | PASS |
| make epub | PASS |
| make release | PASS |
| web/index.html exists | PASS |
| web/chapters/chapter-01.html exists | PASS |
| web/chapters/chapter-45.html exists | PASS |
| web/assets/og-cover.svg exists | PASS |
| web/data/books.json exists | PASS |
| data/reading_paths.json exists | PASS |
| dist/2014books.pdf exists | PASS |
| dist/2014books.epub exists | PASS |
| dist/release zip exists | PASS |
| HTML contains reading-progress | PASS |
| HTML contains reading-settings | PASS |
| HTML contains chapter-drawer | PASS |
| HTML contains og:image | PASS |
| HTML contains reading-path | PASS |

## PUSHED

Yes — branch pushed to origin.

## RECOMMENDED_NEXT_PHASE

Phase G: enhance book metadata (ISBN, publisher, publication year) via manual/assisted curation; add more reading paths with verified chapter-to-book mappings; improve OG cover with actual book imagery if available; consider adding chapter-level anchor sharing (copy link to current paragraph).
