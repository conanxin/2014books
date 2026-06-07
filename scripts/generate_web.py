#!/usr/bin/env python3
"""
generate_web.py — Build a magazine-style static web version of 2014books.
Uses only the Python standard library.
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
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', body_html)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= max_chars:
        return text
    # Break at sentence or clause boundary
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

        # Chapter title
        if stripped.startswith("# ") and stripped.endswith(" #"):
            title = stripped[2:-2].strip()
            continue

        # Book separator
        if stripped == "---":
            in_book_section = True
            continue

        if in_book_section:
            # Book title: **《xxx》**
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
    # Convert markdown bold to HTML
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)
    # Convert markdown links to HTML
    body = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', body)
    # Convert paragraphs
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
    """Parse appendix markdown into structured book entries.

    Format per line:
        1、书名 作者
    Returns list of dicts with keys: id, title, author, raw, source, confidence
    """
    books = []
    for line in md.splitlines():
        stripped = line.strip()
        m = re.match(r'^(\d+)[、.](.+)$', stripped)
        if not m:
            continue
        num = m.group(1)
        raw = m.group(2).strip()
        # Try to split title and author at the last space
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

* { box-sizing: border-box; }

html {
  scroll-behavior: smooth;
}

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

a:hover {
  border-bottom-color: var(--accent);
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
.editors-note {
  padding: 2.5rem 0;
}

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
  .featured-grid {
    grid-template-columns: 1fr;
  }
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
.archive-list {
  margin-top: 1.5rem;
}

.archive-item {
  display: flex;
  gap: 1.2rem;
  padding: 1.2rem 0;
  border-bottom: 1px solid var(--border-light);
  align-items: flex-start;
}

.archive-item:last-child {
  border-bottom: none;
}

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

.archive-content {
  flex: 1;
}

.archive-content h3 {
  font-size: 1.05rem;
  margin: 0 0 0.3rem;
  font-weight: 600;
}

.archive-content h3 a {
  color: var(--ink);
  border-bottom: none;
}

.archive-content h3 a:hover {
  color: var(--accent);
}

.archive-content p {
  font-size: 0.9rem;
  color: var(--muted);
  margin: 0;
  line-height: 1.6;
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

/* Chapter reading view */
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

/* Book list inside chapter */
.chapter-reading .book-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.8rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border-light);
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

.top-nav .nav-links a:hover {
  color: var(--accent);
}

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

.back-to-top.visible {
  opacity: 1;
}

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
  .archive-item { gap: 0.8rem; }
  .archive-num { font-size: 1.4rem; min-width: 2rem; }
}
"""


def generate_html(preface_html: str, chapters: list[dict], total_books: int, missing_candidates: list[dict]) -> str:
    # Pick featured chapters (spread across the range)
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
        featured_cards.append(f"""
<div class="featured-card" onclick="location.href='#chapter-{ch['chapter_num']}'">
  <div class="chapter-num">{ch['chapter_num']:02d}</div>
  <h3>{ch['title']}</h3>
  <p>{ch['summary']}</p>
  <a class="read-link" href="#chapter-{ch['chapter_num']}">阅读本章 →</a>
</div>
""")

    # Chapter archive
    archive_items = []
    for ch in chapters:
        archive_items.append(f"""
<div class="archive-item">
  <div class="archive-num">{ch['chapter_num']}</div>
  <div class="archive-content">
    <h3><a href="#chapter-{ch['chapter_num']}">{ch['title']}</a></h3>
    <p>{ch['summary']}</p>
  </div>
</div>
""")

    # Book cards
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
            book_cards.append(f"""
<div class="book-card" data-title="{book.get('title','')}" data-author="{book.get('author','')}">
  <div class="book-title">《{book.get('title','')}》</div>
  <div class="book-author">{book.get('author','')}</div>
  <div class="book-meta">{tags}</div>
</div>
""")

    # Chapter reading sections
    chapter_sections = []
    for ch in chapters:
        section_books = []
        for book in ch["books"]:
            meta_parts = []
            for k in ["author", "publisher", "price"]:
                if book.get(k):
                    meta_parts.append(book[k])
            meta = " · ".join(meta_parts)
            section_books.append(f"""
<div class="book-card" data-title="{book.get('title','')}" data-author="{book.get('author','')}">
  <div class="book-title">《{book.get('title','')}》</div>
  <div class="book-author">{book.get('author','')}</div>
  <div class="book-meta">{meta}</div>
</div>
""")
        books_html = "\n".join(section_books) if section_books else ""
        book_list_html = f'<div class="book-list">{books_html}</div>' if books_html else ""

        chapter_sections.append(f"""
<section class="chapter-reading" id="chapter-{ch['chapter_num']}">
  <h2><span style="color:var(--border);margin-right:0.5rem;">{ch['chapter_num']:02d}</span>{ch['title']}</h2>
  <div class="chapter-body">
    {ch['body_html']}
  </div>
  {book_list_html}
</section>
""")

    # Missing candidates
    candidates_html = ""
    if missing_candidates:
        candidate_items = "\n".join(
            f'<li><strong>{c["title"]}</strong>（{c["chapter"]}）— {c["reason"]}，置信度：{c["confidence"]}</li>'
            for c in missing_candidates
        )
        candidates_html = f"""
<div class="research-appendix" id="research-appendix">
  <div class="section-label">Research Appendix</div>
  <h2>待核实候选书目</h2>
  <p>以下书目在章节正文中以粗体形式出现，但未在附录中找到对应条目。它们可能是缺失的第 98–100 本，但缺乏足够证据直接纳入正式书单。</p>
  <ul>
    {candidate_items}
  </ul>
</div>
"""

    featured_html = "\n".join(featured_cards)
    archive_html = "\n".join(archive_items)
    book_grid_html = "\n".join(book_cards)
    chapters_reading_html = "\n".join(chapter_sections)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2014年值得你阅读的100本书 · 年度阅读特刊</title>
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
    <span class="badge">原始专题复刻</span>
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

  <section id="archive">
    <div class="section-label">Chapters Archive</div>
    <h2>章节目录</h2>
    <p style="color:var(--muted);font-size:0.95rem;">共 {len(chapters)} 章，点击标题可跳转至正文。</p>
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
    <p style="color:var(--muted);font-size:0.95rem;margin-bottom:2rem;">以下按章节顺序呈现全部正文内容，每章末尾附该章推荐书目。</p>
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

// Back to top visibility
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
"""


def main() -> int:
    repo = find_repo_root()
    contents_dir = repo / "contents"
    web_dir = repo / "web"
    assets_dir = web_dir / "assets"
    data_dir = web_dir / "data"

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
    candidates_path = repo / "data" / "missing_book_candidates.json"
    if candidates_path.exists():
        try:
            with open(candidates_path, "r", encoding="utf-8") as f:
                missing_candidates = json.load(f)
        except Exception as e:
            print(f"WARNING: Could not load missing_book_candidates.json: {e}", file=sys.stderr)

    html = generate_html(preface_html, chapters, total_books, missing_candidates)
    with open(web_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html)

    css = generate_css()
    with open(assets_dir / "style.css", "w", encoding="utf-8") as f:
        f.write(css)

    with open(data_dir / "books.json", "w", encoding="utf-8") as f:
        json.dump(all_books, f, ensure_ascii=False, indent=2)

    print(f"Generated: {web_dir / 'index.html'}")
    print(f"Generated: {assets_dir / 'style.css'}")
    print(f"Generated: {data_dir / 'books.json'}")
    print(f"Total chapters: {len(chapters)}")
    print(f"Total books: {total_books}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
