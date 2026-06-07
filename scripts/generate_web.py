#!/usr/bin/env python3
"""
generate_web.py — Build a magazine-style static web version of 2014books.
Uses only the Python standard library.
Phase F: adds chapter pages, reading progress, reading mode, mobile drawer,
reading paths, OG sharing, and enhanced book archive.
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path


def find_repo_root() -> Path:
    script = Path(__file__).resolve()
    return script.parent.parent


def natural_sort(files: list[Path]) -> list[Path]:
    def key(p: Path) -> list:
        name = p.name
        parts = re.split(r'(\d+)', name)
        return [int(s) if s.isdigit() else s.lower() for s in parts]
    return sorted(files, key=key)


def read_markdown(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_summary(body_html: str, max_chars: int = 120) -> str:
    """Extract a short plain-text summary from HTML body."""
    text = re.sub(r'<[^>]+>', '', body_html)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    for delim in ['。', '；', '，', ' ']:
        idx = truncated.rfind(delim)
        if idx > max_chars * 0.6:
            return truncated[:idx + 1]
    return truncated + '…'


def parse_chapter(md: str, chapter_num: int) -> dict:
    """Parse a chapter markdown into structured data."""
    lines = md.splitlines()
    title = ""
    body_lines = []
    books = []

    in_book_section = False
    current_book = {}
    book_field_order = ["title", "author", "publisher", "price"]
    field_idx = 0

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("# ") and stripped.endswith(" #"):
            title = stripped[2:-2].strip()
            continue

        if stripped == "---":
            in_book_section = True
            continue

        if in_book_section:
            m = re.match(r'\*\*《(.+?)》\*\*$', stripped)
            if m:
                if current_book:
                    books.append(current_book)
                current_book = {"title": m.group(1)}
                field_idx = 1
                continue

            if current_book and stripped:
                field = book_field_order[field_idx] if field_idx < len(book_field_order) else "extra"
                if field not in current_book:
                    current_book[field] = stripped
                else:
                    current_book[field] += " " + stripped
                field_idx += 1
            continue
        else:
            body_lines.append(line)

    if current_book:
        books.append(current_book)

    body = "\n".join(body_lines).strip()
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)
    body = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', body)
    paragraphs = []
    for para in body.split("\n\n"):
        para = para.strip()
        if para:
            paragraphs.append(f"<p>{para}</p>")
    body_html = "\n".join(paragraphs)

    summary = extract_summary(body_html)

    return {
        "chapter_num": chapter_num,
        "title": title,
        "body_html": body_html,
        "summary": summary,
        "books": books,
    }


def parse_preface(md: str) -> str:
    lines = md.splitlines()
    body_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and stripped.endswith(" #"):
            continue
        body_lines.append(line)
    body = "\n".join(body_lines).strip()
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)
    body = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', body)
    paragraphs = []
    for para in body.split("\n\n"):
        para = para.strip()
        if para:
            paragraphs.append(f"<p>{para}</p>")
    return "\n".join(paragraphs)


def parse_appendix(md: str) -> list[dict]:
    """Parse appendix markdown into structured book entries."""
    books = []
    for line in md.splitlines():
        stripped = line.strip()
        m = re.match(r'^(\d+)[、.](.+)$', stripped)
        if not m:
            continue
        num = m.group(1)
        raw = m.group(2).strip()
        parts = raw.rsplit(' ', 1)
        if len(parts) == 2 and len(parts[1]) <= 25:
            title, author = parts
        else:
            title = raw
            author = ""
        books.append({
            "id": num,
            "title": title,
            "author": author,
            "raw": raw,
            "source": "appendix",
            "confidence": "high" if author else "medium",
        })
    return books


def generate_css() -> str:
    return """/* 2014books magazine-style web styles */
:root {
  --paper: #faf8f3;
  --ink: #1a1a1a;
  --ink-light: #4a4a4a;
  --muted: #7a7a7a;
  --accent: #8b3a3a;
  --accent-hover: #6e2e2e;
  --border: #d8d4cc;
  --border-light: #e8e4dc;
  --shadow: rgba(0,0,0,0.04);
  --warn-bg: #fff8f0;
  --warn-border: #e8d5c0;
  --warn-text: #8b5a2b;
  --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  --serif: "Noto Serif CJK SC", "Source Han Serif SC", "STSong", "SimSun", "Songti SC", serif;
}

/* Night mode variables */
html.night {
  --paper: #1e1e1e;
  --ink: #e0dcd0;
  --ink-light: #b8b4a8;
  --muted: #888480;
  --accent: #c07070;
  --accent-hover: #d08080;
  --border: #3a3a3a;
  --border-light: #2e2e2e;
  --shadow: rgba(0,0,0,0.2);
  --warn-bg: #2a2520;
  --warn-border: #4a4035;
  --warn-text: #c8a070;
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; }

html, body {
  margin: 0;
  padding: 0;
  font-family: var(--serif);
  background: var(--paper);
  color: var(--ink);
  line-height: 1.85;
  font-size: 17px;
}

/* Typography */
h1, h2, h3, h4 {
  font-family: var(--serif);
  font-weight: 600;
  line-height: 1.3;
  color: var(--ink);
}

a {
  color: var(--accent);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}

a:hover { border-bottom-color: var(--accent); }

/* Reading progress bar */
.reading-progress {
  position: fixed;
  top: 0;
  left: 0;
  height: 3px;
  background: var(--accent);
  z-index: 200;
  width: 0%;
  transition: width 0.1s linear;
}

/* Hero / Masthead */
.hero {
  background: linear-gradient(180deg, #f5f2ec 0%, var(--paper) 100%);
  border-bottom: 1px solid var(--border);
  padding: 4rem 1.5rem 3rem;
  text-align: center;
  position: relative;
}

.hero::before {
  content: "";
  display: block;
  width: 48px;
  height: 3px;
  background: var(--accent);
  margin: 0 auto 1.5rem;
}

.hero .issue-label {
  font-family: var(--sans);
  font-size: 0.8rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 1rem;
}

.hero h1 {
  font-size: 2.6rem;
  margin: 0 0 1rem;
  letter-spacing: 0.02em;
  font-weight: 700;
}

.hero .subtitle {
  font-size: 1.15rem;
  color: var(--ink-light);
  margin: 0 0 1.5rem;
  font-style: italic;
}

.hero .lead {
  max-width: 600px;
  margin: 0 auto 2rem;
  font-size: 1rem;
  color: var(--muted);
  line-height: 1.8;
}

.hero-badges {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

.badge {
  font-family: var(--sans);
  font-size: 0.75rem;
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 2px;
  color: var(--muted);
  background: rgba(255,255,255,0.6);
  letter-spacing: 0.05em;
}

.hero-cta {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  font-family: var(--sans);
  font-size: 0.9rem;
  padding: 0.7rem 1.6rem;
  border: 1px solid var(--accent);
  border-radius: 2px;
  background: var(--accent);
  color: #fff;
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: all 0.2s;
}

.btn:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}

.btn-ghost {
  background: transparent;
  color: var(--accent);
}

.btn-ghost:hover {
  background: var(--accent);
  color: #fff;
}

.btn-small {
  font-size: 0.75rem;
  padding: 0.4rem 0.8rem;
}

/* Container */
.container {
  max-width: 860px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

/* Section divider */
.section-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 3rem 0;
}

.section-label {
  font-family: var(--sans);
  font-size: 0.7rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.5rem;
}

/* Editor's Note */
.editors-note { padding: 2.5rem 0; }

.editors-note h2 {
  font-size: 1.4rem;
  margin: 0 0 1.2rem;
  font-weight: 600;
}

.editors-note p {
  margin: 0 0 1rem;
  color: var(--ink-light);
  text-align: justify;
}

.editors-note .note-meta {
  font-family: var(--sans);
  font-size: 0.8rem;
  color: var(--muted);
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-light);
}

/* Featured Chapters */
.featured-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-top: 1.5rem;
}

@media (max-width: 700px) {
  .featured-grid { grid-template-columns: 1fr; }
}

.featured-card {
  background: #fff;
  border: 1px solid var(--border-light);
  padding: 1.5rem;
  transition: box-shadow 0.2s, border-color 0.2s;
  cursor: pointer;
}

.featured-card:hover {
  box-shadow: 0 4px 16px var(--shadow);
  border-color: var(--border);
}

.featured-card .chapter-num {
  font-family: var(--sans);
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--border);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.featured-card h3 {
  font-size: 1.15rem;
  margin: 0 0 0.6rem;
  font-weight: 600;
}

.featured-card p {
  font-size: 0.95rem;
  color: var(--ink-light);
  margin: 0 0 1rem;
  line-height: 1.7;
}

.featured-card .read-link {
  font-family: var(--sans);
  font-size: 0.8rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* Chapter Archive */
.archive-list { margin-top: 1.5rem; }

.archive-item {
  display: flex;
  gap: 1.2rem;
  padding: 1.2rem 0;
  border-bottom: 1px solid var(--border-light);
  align-items: flex-start;
}

.archive-item:last-child { border-bottom: none; }

.archive-num {
  font-family: var(--sans);
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--border);
  line-height: 1;
  min-width: 2.5rem;
  text-align: right;
  flex-shrink: 0;
}

.archive-content { flex: 1; }

.archive-content h3 {
  font-size: 1.05rem;
  margin: 0 0 0.3rem;
  font-weight: 600;
}

.archive-content h3 a {
  color: var(--ink);
  border-bottom: none;
}

.archive-content h3 a:hover { color: var(--accent); }

.archive-content p {
  font-size: 0.9rem;
  color: var(--muted);
  margin: 0;
  line-height: 1.6;
}

/* Reading Paths */
.reading-paths-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-top: 1.5rem;
}

@media (max-width: 700px) {
  .reading-paths-grid { grid-template-columns: 1fr; }
}

.path-card {
  background: #fff;
  border: 1px solid var(--border-light);
  padding: 1.5rem;
  transition: box-shadow 0.2s;
}

.path-card:hover {
  box-shadow: 0 4px 16px var(--shadow);
}

.path-card h3 {
  font-size: 1.1rem;
  margin: 0 0 0.5rem;
  font-weight: 600;
}

.path-card p {
  font-size: 0.9rem;
  color: var(--ink-light);
  margin: 0 0 1rem;
  line-height: 1.7;
}

.path-card .path-chapters {
  font-family: var(--sans);
  font-size: 0.8rem;
  color: var(--muted);
}

.path-card .path-chapters a {
  margin-right: 0.6rem;
  border-bottom: none;
}

/* Book Archive */
.book-search {
  margin: 1.5rem 0 2rem;
}

.book-search input {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid var(--border);
  border-radius: 2px;
  font-size: 1rem;
  font-family: var(--sans);
  background: #fff;
  color: var(--ink);
}

.book-search input:focus {
  outline: none;
  border-color: var(--accent);
}

.book-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.book-card {
  background: #fff;
  border: 1px solid var(--border-light);
  padding: 1.2rem;
  transition: box-shadow 0.2s;
}

.book-card:hover {
  box-shadow: 0 3px 12px var(--shadow);
}

.book-card .book-title {
  font-family: var(--serif);
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 0.4rem;
}

.book-card .book-author {
  font-size: 0.9rem;
  color: var(--ink-light);
  margin-bottom: 0.6rem;
}

.book-card .book-meta {
  font-family: var(--sans);
  font-size: 0.75rem;
  color: var(--muted);
  line-height: 1.5;
}

.book-tag {
  display: inline-block;
  font-family: var(--sans);
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  border: 1px solid var(--border-light);
  border-radius: 2px;
  color: var(--muted);
  margin-right: 0.4rem;
  margin-top: 0.4rem;
}

.book-confidence {
  display: inline-block;
  font-family: var(--sans);
  font-size: 0.7rem;
  padding: 0.15rem 0.4rem;
  border-radius: 2px;
  margin-left: 0.4rem;
}

.confidence-high {
  background: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #c8e6c9;
}

.confidence-medium {
  background: #fff8e1;
  color: #f57f17;
  border: 1px solid #ffecb3;
}

.confidence-low {
  background: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
}

/* Research Appendix */
.research-appendix {
  background: var(--warn-bg);
  border: 1px solid var(--warn-border);
  padding: 2rem;
  margin: 2rem 0;
}

.research-appendix h2 {
  font-size: 1.2rem;
  margin: 0 0 0.8rem;
  color: var(--warn-text);
}

.research-appendix > p {
  font-size: 0.95rem;
  color: var(--warn-text);
  margin: 0 0 1rem;
  opacity: 0.85;
}

.research-appendix ul {
  margin: 0;
  padding-left: 1.2rem;
}

.research-appendix li {
  font-size: 0.95rem;
  color: var(--ink-light);
  margin-bottom: 0.4rem;
}

/* Chapter reading view (home page inline) */
.chapter-reading {
  background: #fff;
  border: 1px solid var(--border-light);
  padding: 2.5rem 2rem;
  margin: 2rem 0;
}

.chapter-reading h2 {
  font-size: 1.6rem;
  margin: 0 0 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--border-light);
}

.chapter-reading .chapter-body {
  font-size: 1.05rem;
  line-height: 1.9;
  color: var(--ink-light);
}

.chapter-reading .chapter-body p {
  margin: 0 0 1.2rem;
  text-align: justify;
}

.chapter-reading .chapter-body a {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 0.2em;
}

.chapter-reading .book-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.8rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-light);
}

/* Chapter page styles */
.chapter-page .top-nav {
  position: sticky;
  top: 0;
  background: rgba(250,248,243,0.95);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
  padding: 0.6rem 1.5rem;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chapter-page .nav-title {
  font-family: var(--serif);
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ink);
}

.chapter-page .nav-links {
  display: flex;
  gap: 1.2rem;
  font-family: var(--sans);
  font-size: 0.8rem;
}

.chapter-page .nav-links a {
  color: var(--muted);
  border-bottom: none;
}

.chapter-page .nav-links a:hover { color: var(--accent); }

.chapter-page .reading-settings {
  display: flex;
  gap: 0.4rem;
  align-items: center;
}

.chapter-page .chapter-container {
  max-width: 760px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

.chapter-page .chapter-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-light);
}

.chapter-page .chapter-header .back-link {
  font-family: var(--sans);
  font-size: 0.8rem;
  color: var(--muted);
  margin-bottom: 1rem;
  display: inline-block;
}

.chapter-page .chapter-header .chapter-num-display {
  font-family: var(--sans);
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.5rem;
}

.chapter-page .chapter-header h1 {
  font-size: 1.8rem;
  margin: 0;
  font-weight: 700;
  line-height: 1.3;
}

.chapter-page .chapter-body-text {
  font-size: 1.05rem;
  line-height: 1.9;
  color: var(--ink-light);
}

.chapter-page .chapter-body-text p {
  margin: 0 0 1.4rem;
  text-align: justify;
}

.chapter-page .chapter-body-text a {
  color: var(--accent);
  text-decoration: underline;
  text-underline-offset: 0.2em;
}

.chapter-page .chapter-books {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border);
}

.chapter-page .chapter-books h3 {
  font-size: 1.1rem;
  margin: 0 0 1rem;
  font-weight: 600;
}

.chapter-page .chapter-nav {
  display: flex;
  justify-content: space-between;
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 1px solid var(--border);
}

.chapter-page .chapter-nav a {
  font-family: var(--sans);
  font-size: 0.85rem;
  color: var(--muted);
  border-bottom: none;
}

.chapter-page .chapter-nav a:hover { color: var(--accent); }

/* Mobile drawer */
.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 150;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s, visibility 0.3s;
}

.drawer-overlay.open {
  opacity: 1;
  visibility: visible;
}

.chapter-drawer {
  position: fixed;
  top: 0;
  left: 0;
  width: 280px;
  height: 100%;
  background: var(--paper);
  border-right: 1px solid var(--border);
  z-index: 160;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  overflow-y: auto;
  padding: 1.5rem;
}

.chapter-drawer.open {
  transform: translateX(0);
}

.chapter-drawer .drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-light);
}

.chapter-drawer .drawer-title {
  font-family: var(--sans);
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
}

.chapter-drawer .drawer-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--muted);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.chapter-drawer .drawer-item {
  display: block;
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border-light);
  font-size: 0.9rem;
  color: var(--ink-light);
  border-bottom: none;
}

.chapter-drawer .drawer-item:hover { color: var(--accent); }

.chapter-drawer .drawer-item .drawer-num {
  font-family: var(--sans);
  font-size: 0.75rem;
  color: var(--muted);
  margin-right: 0.5rem;
  min-width: 1.5rem;
  display: inline-block;
}

/* Navigation */
.top-nav {
  position: sticky;
  top: 0;
  background: rgba(250,248,243,0.95);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
  padding: 0.6rem 1.5rem;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.top-nav .nav-title {
  font-family: var(--serif);
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ink);
}

.top-nav .nav-links {
  display: flex;
  gap: 1.2rem;
  font-family: var(--sans);
  font-size: 0.8rem;
}

.top-nav .nav-links a {
  color: var(--muted);
  border-bottom: none;
}

.top-nav .nav-links a:hover { color: var(--accent); }

.back-to-top {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 40px;
  height: 40px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.2rem;
  color: var(--muted);
  box-shadow: 0 2px 8px var(--shadow);
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 99;
}

.back-to-top.visible { opacity: 1; }

.back-to-top:hover {
  color: var(--accent);
  border-color: var(--accent);
}

/* Footer */
.site-footer {
  border-top: 1px solid var(--border);
  padding: 3rem 1.5rem;
  margin-top: 4rem;
  text-align: center;
}

.site-footer p {
  font-size: 0.85rem;
  color: var(--muted);
  margin: 0 0 0.5rem;
  font-family: var(--sans);
}

.site-footer .footer-links {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 1rem;
  font-family: var(--sans);
  font-size: 0.8rem;
}

/* Hidden utility */
.hidden { display: none !important; }

/* Responsive */
@media (max-width: 700px) {
  html { font-size: 16px; }
  .hero { padding: 2.5rem 1rem 2rem; }
  .hero h1 { font-size: 1.8rem; }
  .hero .subtitle { font-size: 1rem; }
  .container { padding: 0 1rem; }
  .chapter-reading { padding: 1.5rem 1rem; }
  .top-nav { padding: 0.5rem 1rem; }
  .top-nav .nav-links { display: none; }
  .back-to-top { right: 1rem; bottom: 1rem; }
  .featured-grid { grid-template-columns: 1fr; }
  .reading-paths-grid { grid-template-columns: 1fr; }
  .archive-item { gap: 0.8rem; }
  .archive-num { font-size: 1.4rem; min-width: 2rem; }
  .chapter-page .chapter-container { padding: 1.5rem 1rem 3rem; }
  .chapter-page .chapter-header h1 { font-size: 1.5rem; }
}
"""


def generate_og_cover_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#faf8f3"/>
  <rect x="60" y="60" width="1080" height="510" fill="none" stroke="#8b3a3a" stroke-width="2"/>
  <line x1="60" y1="180" x2="1140" y2="180" stroke="#8b3a3a" stroke-width="1" opacity="0.3"/>
  <text x="600" y="140" font-family="Georgia, serif" font-size="72" font-weight="700" fill="#1a1a1a" text-anchor="middle">2014</text>
  <text x="600" y="260" font-family="Georgia, serif" font-size="42" font-weight="400" fill="#1a1a1a" text-anchor="middle">年度阅读特刊</text>
  <text x="600" y="340" font-family="-apple-system, sans-serif" font-size="24" fill="#4a4a4a" text-anchor="middle">2014年值得你阅读的100本书</text>
  <text x="600" y="460" font-family="-apple-system, sans-serif" font-size="18" fill="#8b3a3a" text-anchor="middle" letter-spacing="3">97 BOOKS VERIFIED</text>
  <text x="600" y="510" font-family="-apple-system, sans-serif" font-size="14" fill="#7a7a7a" text-anchor="middle">Conan Xin · Markdown Book Project</text>
</svg>'''


def generate_chapter_page(ch: dict, chapters: list[dict], total_books: int, reading_paths: list[dict]) -> str:
    """Generate an independent chapter page."""
    num = ch['chapter_num']
    prev_ch = chapters[num - 2] if num > 1 else None
    next_ch = chapters[num] if num < len(chapters) else None

    # Build chapter books HTML
    section_books = []
    for book in ch["books"]:
        meta_parts = []
        for k in ["author", "publisher", "price"]:
            if book.get(k):
                meta_parts.append(book[k])
        meta = " · ".join(meta_parts)
        section_books.append(f'''<div class="book-card">
  <div class="book-title">《{book.get('title','')}》</div>
  <div class="book-author">{book.get('author','')}</div>
  <div class="book-meta">{meta}</div>
</div>''')
    books_html = "\n".join(section_books) if section_books else ""
    book_list_html = f'<div class="book-grid" style="margin-top:1rem;">{books_html}</div>' if books_html else ""

    # Drawer items
    drawer_items = []
    for c in chapters:
        active = ' style="color:var(--accent);font-weight:600;"' if c['chapter_num'] == num else ''
        drawer_items.append(f'<a href="chapter-{c["chapter_num"]:02d}.html" class="drawer-item"{active}><span class="drawer-num">{c["chapter_num"]:02d}</span>{c["title"]}</a>')
    drawer_html = "\n".join(drawer_items)

    # Nav links
    prev_link = f'<a href="chapter-{prev_ch["chapter_num"]:02d}.html">← 上一章</a>' if prev_ch else '<span></span>'
    next_link = f'<a href="chapter-{next_ch["chapter_num"]:02d}.html">下一章 →</a>' if next_ch else '<span></span>'

    og_image = "https://conanxin.github.io/2014books/assets/og-cover.svg"
    og_title = f"第{num}章：{ch['title']} · 2014年值得你阅读的100本书"
    og_desc = ch['summary'][:120] if ch['summary'] else "2014年度阅读特刊独立章节"

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{og_title}</title>
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:type" content="article">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body class="chapter-page">

<div class="reading-progress" id="readingProgress"></div>

<nav class="top-nav">
  <div style="display:flex;align-items:center;gap:0.8rem;">
    <button class="btn btn-small" id="drawerToggle" style="padding:0.3rem 0.6rem;font-size:0.75rem;">目录</button>
    <a href="../index.html" class="nav-title" style="border-bottom:none;">2014books</a>
  </div>
  <div class="reading-settings">
    <button class="btn btn-small" onclick="adjustFontSize(-1)" title="减小字号">A-</button>
    <button class="btn btn-small" onclick="adjustFontSize(1)" title="增大字号">A+</button>
    <button class="btn btn-small" onclick="toggleTheme()" title="切换纸张/夜间">◐</button>
  </div>
</nav>

<div class="drawer-overlay" id="drawerOverlay" onclick="closeDrawer()"></div>
<div class="chapter-drawer" id="chapterDrawer">
  <div class="drawer-header">
    <span class="drawer-title">章节目录</span>
    <button class="drawer-close" onclick="closeDrawer()">×</button>
  </div>
  {drawer_html}
</div>

<div class="chapter-container">
  <div class="chapter-header">
    <a href="../index.html#archive" class="back-link">← 返回首页</a>
    <div class="chapter-num-display">Chapter {num:02d} / {len(chapters)}</div>
    <h1>{ch['title']}</h1>
  </div>

  <div class="chapter-body-text" id="chapterBody">
    {ch['body_html']}
  </div>

  {f'<div class="chapter-books"><h3>本章推荐书目</h3>{book_list_html}</div>' if book_list_html else ''}

  <div class="chapter-nav">
    {prev_link}
    <a href="../index.html#books" style="color:var(--muted);">书目档案</a>
    {next_link}
  </div>
</div>

<footer class="site-footer">
  <p>原始内容来自《第一财经周刊》· 由 Conan Xin 整理</p>
  <p>本项目为学习交流用途，不代表原出版方立场</p>
  <div class="footer-links">
    <a href="https://github.com/conanxin/2014books">GitHub</a>
    <a href="../index.html">首页</a>
  </div>
</footer>

<script>
// Reading progress
const progressBar = document.getElementById('readingProgress');
window.addEventListener('scroll', () => {{
  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
  progressBar.style.width = pct + '%';
}});

// Font size
let currentSize = 17;
function adjustFontSize(delta) {{
  currentSize += delta;
  if (currentSize < 14) currentSize = 14;
  if (currentSize > 24) currentSize = 24;
  document.documentElement.style.fontSize = currentSize + 'px';
  localStorage.setItem('2014books_font_size', currentSize);
}}

// Theme
function toggleTheme() {{
  const html = document.documentElement;
  if (html.classList.contains('night')) {{
    html.classList.remove('night');
    localStorage.setItem('2014books_theme', 'paper');
  }} else {{
    html.classList.add('night');
    localStorage.setItem('2014books_theme', 'night');
  }}
}}

// Restore preferences
(function(){{
  const savedSize = localStorage.getItem('2014books_font_size');
  if (savedSize) {{
    currentSize = parseInt(savedSize, 10);
    document.documentElement.style.fontSize = currentSize + 'px';
  }}
  const savedTheme = localStorage.getItem('2014books_theme');
  if (savedTheme === 'night') {{
    document.documentElement.classList.add('night');
  }}
}})();

// Drawer
const drawer = document.getElementById('chapterDrawer');
const overlay = document.getElementById('drawerOverlay');
document.getElementById('drawerToggle').addEventListener('click', () => {{
  drawer.classList.add('open');
  overlay.classList.add('open');
}});
function closeDrawer() {{
  drawer.classList.remove('open');
  overlay.classList.remove('open');
}}
</script>

</body>
</html>'''


def generate_html(preface_html: str, chapters: list[dict], total_books: int, missing_candidates: list[dict], reading_paths: list[dict]) -> str:
    # Pick featured chapters
    featured_indices = []
    if len(chapters) >= 6:
        step = len(chapters) // 6
        featured_indices = [i * step for i in range(6)]
    elif len(chapters) >= 4:
        step = len(chapters) // 4
        featured_indices = [i * step for i in range(4)]
    else:
        featured_indices = list(range(len(chapters)))

    featured_cards = []
    for idx in featured_indices:
        ch = chapters[idx]
        featured_cards.append(f'''
<div class="featured-card" onclick="location.href='chapters/chapter-{ch['chapter_num']:02d}.html'">
  <div class="chapter-num">{ch['chapter_num']:02d}</div>
  <h3>{ch['title']}</h3>
  <p>{ch['summary']}</p>
  <a class="read-link" href="chapters/chapter-{ch['chapter_num']:02d}.html">阅读本章 →</a>
</div>
''')

    # Chapter archive
    archive_items = []
    for ch in chapters:
        archive_items.append(f'''
<div class="archive-item">
  <div class="archive-num">{ch['chapter_num']}</div>
  <div class="archive-content">
    <h3><a href="chapters/chapter-{ch['chapter_num']:02d}.html">{ch['title']}</a></h3>
    <p>{ch['summary']}</p>
  </div>
</div>
''')

    # Book cards from chapter inline books
    book_cards = []
    for b in chapters:
        for book in b["books"]:
            meta_parts = []
            for k in ["author", "publisher", "price"]:
                if book.get(k):
                    meta_parts.append(book[k])
            meta = " · ".join(meta_parts)
            tags = ""
            if meta:
                tags = f'<span class="book-tag">{meta}</span>'
            book_cards.append(f'''
<div class="book-card" data-title="{book.get('title','')}" data-author="{book.get('author','')}">
  <div class="book-title">《{book.get('title','')}》</div>
  <div class="book-author">{book.get('author','')}</div>
  <div class="book-meta">{tags}</div>
</div>
''')

    # Chapter reading sections (inline on home page, keep for fallback)
    chapter_sections = []
    for ch in chapters:
        section_books = []
        for book in ch["books"]:
            meta_parts = []
            for k in ["author", "publisher", "price"]:
                if book.get(k):
                    meta_parts.append(book[k])
            meta = " · ".join(meta_parts)
            section_books.append(f'''
<div class="book-card" data-title="{book.get('title','')}" data-author="{book.get('author','')}">
  <div class="book-title">《{book.get('title','')}》</div>
  <div class="book-author">{book.get('author','')}</div>
  <div class="book-meta">{meta}</div>
</div>
''')
        books_html = "\n".join(section_books) if section_books else ""
        book_list_html = f'<div class="book-list">{books_html}</div>' if books_html else ""

        chapter_sections.append(f'''
<section class="chapter-reading" id="chapter-{ch['chapter_num']}">
  <h2><span style="color:var(--border);margin-right:0.5rem;">{ch['chapter_num']:02d}</span>{ch['title']}</h2>
  <div class="chapter-body">
    {ch['body_html']}
  </div>
  {book_list_html}
  <p style="margin-top:1.5rem;"><a href="chapters/chapter-{ch['chapter_num']:02d}.html" style="font-family:var(--sans);font-size:0.85rem;">在独立页面阅读本章 →</a></p>
</section>
''')

    # Missing candidates
    candidates_html = ""
    if missing_candidates:
        candidate_items = "\n".join(
            f'<li><strong>{c["title"]}</strong>（{c["chapter"]}）— {c["reason"]}，置信度：{c["confidence"]}</li>'
            for c in missing_candidates
        )
        candidates_html = f'''
<div class="research-appendix" id="research-appendix">
  <div class="section-label">Research Appendix</div>
  <h2>待核实候选书目</h2>
  <p>以下书目在章节正文中以粗体形式出现，但未在附录中找到对应条目。它们可能是缺失的第 98–100 本，但缺乏足够证据直接纳入正式书单。</p>
  <ul>
    {candidate_items}
  </ul>
</div>
'''

    # Reading paths
    paths_html = ""
    if reading_paths:
        path_cards = []
        for p in reading_paths:
            ch_links = " ".join(
                f'<a href="chapters/chapter-{int(cid):02d}.html">第{int(cid)}章</a>'
                for cid in p.get("chapter_ids", [])
            )
            book_tags = " ".join(
                f'<span class="book-tag">{t}</span>'
                for t in p.get("book_titles", [])
            )
            path_cards.append(f'''
<div class="path-card">
  <h3>{p.get("title","")}</h3>
  <p>{p.get("description","")}</p>
  <div class="path-chapters">相关章节：{ch_links}</div>
  <div style="margin-top:0.5rem;">{book_tags}</div>
</div>
''')
        paths_html = f'''
<section id="reading-paths">
  <div class="section-label">Reading Paths</div>
  <h2>阅读路线</h2>
  <p style="color:var(--muted);font-size:0.95rem;">按兴趣选择阅读路径，不必按顺序读完 45 章。</p>
  <div class="reading-paths-grid">
    {chr(10).join(path_cards)}
  </div>
</section>

<hr class="section-divider">
'''

    featured_html = "\n".join(featured_cards)
    archive_html = "\n".join(archive_items)
    book_grid_html = "\n".join(book_cards)
    chapters_reading_html = "\n".join(chapter_sections)

    og_image = "https://conanxin.github.io/2014books/assets/og-cover.svg"

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2014年值得你阅读的100本书 · 年度阅读特刊</title>
<meta property="og:title" content="2014年值得你阅读的100本书 · 年度阅读特刊">
<meta property="og:description" content="一份从旧专题中复活的年度阅读特刊。已结构化整理 {total_books} 本书，支持搜索、章节阅读和离线下载。">
<meta property="og:type" content="website">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>

<nav class="top-nav">
  <div class="nav-title">2014books</div>
  <div class="nav-links">
    <a href="#editors-note">编者序</a>
    <a href="#featured">精选</a>
    <a href="#archive">目录</a>
    <a href="#books">书目</a>
    <a href="#research-appendix">附录</a>
  </div>
</nav>

<header class="hero">
  <div class="issue-label">Annual Reading Special · 2014</div>
  <h1>2014年值得你阅读的100本书</h1>
  <p class="subtitle">一份从旧专题中复活的年度阅读特刊</p>
  <p class="lead">十年前，《第一财经周刊》做了一份年度书单。十年后，我们把它从网页存档中打捞出来，重新整理成可以阅读、可以搜索、可以带走的数字版本。</p>
  <div class="hero-badges">
    <span class="badge">已结构化整理 {total_books} 本</span>
    <span class="badge">PDF · EPUB · Web</span>
    <span class="badge">独立章节页 · 阅读进度 · 阅读模式</span>
  </div>
  <div class="hero-cta">
    <a href="#featured" class="btn">开始阅读</a>
    <a href="#books" class="btn btn-ghost">浏览书单</a>
  </div>
</header>

<main class="container">

  <section class="editors-note" id="editors-note">
    <div class="section-label">Editor's Note</div>
    <h2>编者序</h2>
    <p>这个项目始于一次偶然的发现——2014 年《第一财经周刊》的专题页面还在，但排版已经支离破碎，图片全部失效，文字混在一堆广告代码中间。我们决定把它救出来。</p>
    <p>原始专题声称推荐了 100 本书。经过结构化整理，我们从附录中可靠地提取到 <strong>{total_books} 本</strong>，剩余 3 本因原始来源缺失而无法确认。我们没有为了凑数而编造，而是把不确定的信息单独隔离在"待核实候选"中。</p>
    <p>你可以按章节阅读每一篇短评，也可以直接搜索某本书的作者和出版社信息。所有内容均可下载为 PDF 或 EPUB，在离线环境下完整阅读。</p>
    <div class="note-meta">
      Conan Xin · Markdown Book Project · 仅供学习交流
    </div>
  </section>

  <hr class="section-divider">

  <section id="featured">
    <div class="section-label">Featured Chapters</div>
    <h2>精选章节</h2>
    <div class="featured-grid">
      {featured_html}
    </div>
  </section>

  <hr class="section-divider">

  {paths_html}

  <section id="archive">
    <div class="section-label">Chapters Archive</div>
    <h2>章节目录</h2>
    <p style="color:var(--muted);font-size:0.95rem;">共 {len(chapters)} 章，点击标题进入独立章节页阅读。</p>
    <div class="archive-list">
      {archive_html}
    </div>
  </section>

  <hr class="section-divider">

  <section id="books">
    <div class="section-label">Book Archive</div>
    <h2>书目检索</h2>
    <p style="color:var(--muted);font-size:0.95rem;">正式书单 {total_books} 本，支持按书名或作者搜索。</p>
    <div class="book-search">
      <input type="text" id="searchInput" placeholder="搜索书名或作者…" oninput="doSearch()">
    </div>
    <div class="book-grid" id="bookGrid">
      {book_grid_html}
    </div>
    <p id="noResults" class="hidden" style="text-align:center;color:var(--muted);padding:2rem 0;">未找到匹配的书目</p>
  </section>

  {candidates_html}

  <hr class="section-divider">

  <section id="reading">
    <div class="section-label">Full Text</div>
    <h2>完整正文</h2>
    <p style="color:var(--muted);font-size:0.95rem;margin-bottom:2rem;">以下按章节顺序呈现全部正文内容，每章末尾附该章推荐书目。也可点击章节标题进入独立页面阅读。</p>
    {chapters_reading_html}
  </section>

</main>

<footer class="site-footer">
  <p>原始内容来自《第一财经周刊》· 由 Conan Xin 整理</p>
  <p>本项目为学习交流用途，不代表原出版方立场</p>
  <div class="footer-links">
    <a href="https://github.com/conanxin/2014books">GitHub</a>
    <a href="#" onclick="window.print();return false;">打印友好版</a>
    <a href="https://conanxin.github.io/2014books/">在线版本</a>
  </div>
</footer>

<button class="back-to-top" id="backToTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" aria-label="回到顶部">↑</button>

<script>
function doSearch() {{
  const q = document.getElementById('searchInput').value.trim().toLowerCase();
  const cards = document.querySelectorAll('#bookGrid .book-card');
  const noResults = document.getElementById('noResults');
  let visibleCount = 0;
  cards.forEach(c => {{
    const t = (c.dataset.title || '').toLowerCase();
    const a = (c.dataset.author || '').toLowerCase();
    if (!q || t.includes(q) || a.includes(q)) {{
      c.classList.remove('hidden');
      visibleCount++;
    }} else {{
      c.classList.add('hidden');
    }}
  }});
  if (visibleCount === 0 && q) {{
    noResults.classList.remove('hidden');
  }} else {{
    noResults.classList.add('hidden');
  }}
}}

const backToTop = document.getElementById('backToTop');
window.addEventListener('scroll', () => {{
  if (window.scrollY > 600) {{
    backToTop.classList.add('visible');
  }} else {{
    backToTop.classList.remove('visible');
  }}
}});
</script>

</body>
</html>
'''


def main() -> int:
    repo = find_repo_root()
    contents_dir = repo / "contents"
    web_dir = repo / "web"
    assets_dir = web_dir / "assets"
    data_dir = web_dir / "data"
    chapters_dir = web_dir / "chapters"
    repo_data_dir = repo / "data"

    if not contents_dir.exists():
        print(f"ERROR: contents/ not found at {contents_dir}", file=sys.stderr)
        return 1

    # Preface
    preface_files = natural_sort(list(contents_dir.glob("0-preface*.markdown")))
    preface_html = ""
    if preface_files:
        preface_html = parse_preface(read_markdown(preface_files[0]))

    # Chapters
    chapter_files = natural_sort(list(contents_dir.glob("1-chapter*.markdown")))
    chapters = []
    for i, cf in enumerate(chapter_files, start=1):
        md = read_markdown(cf)
        ch = parse_chapter(md, i)
        chapters.append(ch)

    # Build web output
    web_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    chapters_dir.mkdir(parents=True, exist_ok=True)

    # Parse appendix for authoritative book list
    appendix_files = natural_sort(list(contents_dir.glob("2-appendix*.markdown")))
    appendix_books = []
    if appendix_files:
        appendix_books = parse_appendix(read_markdown(appendix_files[0]))

    # Build books.json from appendix (authoritative source)
    all_books = []
    for b in appendix_books:
        all_books.append({
            "id": b.get("id", ""),
            "title": b.get("title", ""),
            "author": b.get("author", ""),
            "raw": b.get("raw", ""),
            "source": b.get("source", "appendix"),
            "confidence": b.get("confidence", "medium"),
        })

    total_books = len(all_books)

    # Load missing book candidates
    missing_candidates = []
    candidates_path = repo_data_dir / "missing_book_candidates.json"
    if candidates_path.exists():
        try:
            with open(candidates_path, "r", encoding="utf-8") as f:
                missing_candidates = json.load(f)
        except Exception as e:
            print(f"WARNING: Could not load missing_book_candidates.json: {e}", file=sys.stderr)

    # Load reading paths
    reading_paths = []
    paths_path = repo_data_dir / "reading_paths.json"
    if paths_path.exists():
        try:
            with open(paths_path, "r", encoding="utf-8") as f:
                reading_paths = json.load(f)
        except Exception as e:
            print(f"WARNING: Could not load reading_paths.json: {e}", file=sys.stderr)

    # Generate OG cover SVG
    og_svg = generate_og_cover_svg()
    with open(assets_dir / "og-cover.svg", "w", encoding="utf-8") as f:
        f.write(og_svg)

    # Generate home page
    html = generate_html(preface_html, chapters, total_books, missing_candidates, reading_paths)
    with open(web_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Generate chapter pages
    for ch in chapters:
        ch_html = generate_chapter_page(ch, chapters, total_books, reading_paths)
        with open(chapters_dir / f"chapter-{ch['chapter_num']:02d}.html", "w", encoding="utf-8") as f:
            f.write(ch_html)

    css = generate_css()
    with open(assets_dir / "style.css", "w", encoding="utf-8") as f:
        f.write(css)

    with open(data_dir / "books.json", "w", encoding="utf-8") as f:
        json.dump(all_books, f, ensure_ascii=False, indent=2)

    print(f"Generated: {web_dir / 'index.html'}")
    print(f"Generated: {assets_dir / 'style.css'}")
    print(f"Generated: {assets_dir / 'og-cover.svg'}")
    print(f"Generated: {data_dir / 'books.json'}")
    print(f"Generated: {len(chapters)} chapter pages in {chapters_dir}")
    print(f"Total chapters: {len(chapters)}")
    print(f"Total books: {total_books}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
