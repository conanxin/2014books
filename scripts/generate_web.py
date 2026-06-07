#!/usr/bin/env python3
"""
generate_web.py — Build a static web version of 2014books.
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

    return {
        "chapter_num": chapter_num,
        "title": title,
        "body_html": body_html,
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


def generate_css() -> str:
    return """/* 2014books static web styles */
:root {
  --bg: #f7f5f0;
  --card: #ffffff;
  --text: #2c2c2c;
  --muted: #6b6b6b;
  --accent: #8b4513;
  --border: #e0dcd3;
  --shadow: rgba(0,0,0,0.06);
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  font-family: "Noto Serif CJK SC", "Source Han Serif SC", "STSong", "SimSun", serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.8;
}

header {
  background: var(--card);
  border-bottom: 1px solid var(--border);
  padding: 2rem 1rem;
  text-align: center;
  box-shadow: 0 2px 8px var(--shadow);
}

header h1 {
  margin: 0 0 0.5rem;
  font-size: 1.8rem;
  letter-spacing: 0.05em;
  color: var(--accent);
}

header p {
  margin: 0;
  color: var(--muted);
  font-size: 0.95rem;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
}

.search-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-bar input {
  flex: 1;
  min-width: 200px;
  padding: 0.6rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  background: var(--card);
}

.search-bar button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  background: var(--accent);
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
}

.search-bar button:hover { opacity: 0.9; }

.chapter-nav {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem 1.2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 6px var(--shadow);
}

.chapter-nav h2 {
  margin: 0 0 0.6rem;
  font-size: 1.1rem;
  color: var(--accent);
}

.chapter-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.3rem 0.8rem;
}

.chapter-nav li a {
  color: var(--text);
  text-decoration: none;
  font-size: 0.9rem;
}

.chapter-nav li a:hover {
  color: var(--accent);
  text-decoration: underline;
}

.chapter {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.2rem 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 6px var(--shadow);
}

.chapter h2 {
  margin: 0 0 0.8rem;
  font-size: 1.3rem;
  color: var(--accent);
  border-bottom: 2px solid var(--border);
  padding-bottom: 0.4rem;
}

.chapter-body {
  margin-bottom: 1rem;
  font-size: 1rem;
}

.chapter-body p {
  margin: 0 0 0.8rem;
  text-align: justify;
}

.chapter-body a {
  color: var(--accent);
  text-decoration: underline;
}

.book-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.8rem;
}

.book-card {
  background: #faf9f6;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.8rem 1rem;
  transition: box-shadow 0.2s;
}

.book-card:hover {
  box-shadow: 0 4px 10px var(--shadow);
}

.book-title {
  font-weight: bold;
  color: var(--accent);
  margin-bottom: 0.3rem;
}

.book-meta {
  font-size: 0.85rem;
  color: var(--muted);
  line-height: 1.5;
}

.hidden { display: none !important; }

footer {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--muted);
  font-size: 0.85rem;
  border-top: 1px solid var(--border);
  margin-top: 2rem;
}

@media (max-width: 600px) {
  header h1 { font-size: 1.4rem; }
  .chapter-nav ul { grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); }
  .book-list { grid-template-columns: 1fr; }
}
"""


def generate_html(preface_html: str, chapters: list[dict]) -> str:
    nav_items = []
    chapter_sections = []
    all_books = []

    for ch in chapters:
        cid = f"chapter-{ch['chapter_num']}"
        nav_items.append(f'<li><a href="#{cid}">{ch["chapter_num"]}. {ch["title"]}</a></li>')

        book_cards = []
        for b in ch["books"]:
            all_books.append({
                "title": b.get("title", ""),
                "author": b.get("author", ""),
                "publisher": b.get("publisher", ""),
                "price": b.get("price", ""),
                "chapter": ch["chapter_num"],
            })
            meta_parts = []
            for k in ["author", "publisher", "price"]:
                if b.get(k):
                    meta_parts.append(b[k])
            meta = " · ".join(meta_parts)
            book_cards.append(
                f'<div class="book-card" data-title="{b.get("title","")}" data-author="{b.get("author","")}">'
                f'<div class="book-title">《{b.get("title","")}》</div>'
                f'<div class="book-meta">{meta}</div></div>'
            )

        books_html = "\n".join(book_cards) if book_cards else "<p>（本章无书单）</p>"

        chapter_sections.append(f"""
<section class="chapter" id="{cid}">
  <h2>{ch['chapter_num']}. {ch['title']}</h2>
  <div class="chapter-body">
    {ch['body_html']}
  </div>
  <div class="book-list">
    {books_html}
  </div>
</section>
""")

    nav_html = "\n".join(nav_items)
    chapters_html = "\n".join(chapter_sections)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2014年值得你阅读的100本书</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header>
  <h1>2014年值得你阅读的100本书</h1>
  <p>一个被重新整理的 Markdown 制书项目 · 第一财经周刊专题回顾</p>
</header>

<div class="container">
  <div class="search-bar">
    <input type="text" id="searchInput" placeholder="搜索书名或作者…">
    <button onclick="doSearch()">搜索</button>
    <button onclick="clearSearch()">清除</button>
  </div>

  <nav class="chapter-nav">
    <h2>章节目录</h2>
    <ul>
      {nav_html}
    </ul>
  </nav>

  <section class="chapter" id="preface">
    <h2>前言</h2>
    <div class="chapter-body">
      {preface_html}
    </div>
  </section>

  {chapters_html}
</div>

<footer>
  <p>原始内容来自第一财经周刊 · 由 Conan Xin 整理 · 仅供学习交流</p>
</footer>

<script>
function doSearch() {{
  const q = document.getElementById('searchInput').value.trim().toLowerCase();
  const cards = document.querySelectorAll('.book-card');
  const chapters = document.querySelectorAll('.chapter');
  if (!q) {{ clearSearch(); return; }}
  cards.forEach(c => {{
    const t = (c.dataset.title || '').toLowerCase();
    const a = (c.dataset.author || '').toLowerCase();
    if (t.includes(q) || a.includes(q)) {{
      c.classList.remove('hidden');
    }} else {{
      c.classList.add('hidden');
    }}
  }});
  chapters.forEach(ch => {{
    const visible = ch.querySelectorAll('.book-card:not(.hidden)');
    if (visible.length === 0 && ch.querySelector('.book-list')) {{
      ch.classList.add('hidden');
    }} else {{
      ch.classList.remove('hidden');
    }}
  }});
}}

function clearSearch() {{
  document.getElementById('searchInput').value = '';
  document.querySelectorAll('.book-card').forEach(c => c.classList.remove('hidden'));
  document.querySelectorAll('.chapter').forEach(ch => ch.classList.remove('hidden'));
}}

document.getElementById('searchInput').addEventListener('keydown', function(e) {{
  if (e.key === 'Enter') doSearch();
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

    html = generate_html(preface_html, chapters)
    with open(web_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html)

    css = generate_css()
    with open(assets_dir / "style.css", "w", encoding="utf-8") as f:
        f.write(css)

    # Build books.json
    all_books = []
    for ch in chapters:
        for b in ch["books"]:
            all_books.append({
                "title": b.get("title", ""),
                "author": b.get("author", ""),
                "publisher": b.get("publisher", ""),
                "price": b.get("price", ""),
                "chapter": ch["chapter_num"],
                "chapter_title": ch["title"],
            })

    with open(data_dir / "books.json", "w", encoding="utf-8") as f:
        json.dump(all_books, f, ensure_ascii=False, indent=2)

    print(f"Generated: {web_dir / 'index.html'}")
    print(f"Generated: {assets_dir / 'style.css'}")
    print(f"Generated: {data_dir / 'books.json'}")
    print(f"Total chapters: {len(chapters)}")
    print(f"Total books: {len(all_books)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
