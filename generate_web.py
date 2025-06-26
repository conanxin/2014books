import os
import re
import html

CONTENT_DIR = 'contents'
CHAPTER_PATTERN = re.compile(r'1-chapter.*\.markdown')

chapter_files = sorted([
    os.path.join(CONTENT_DIR, f) for f in os.listdir(CONTENT_DIR)
    if CHAPTER_PATTERN.match(f)
], key=lambda x: int(re.search(r'(\d+)', os.path.basename(x)).group(1)))

chapters = []
for path in chapter_files:
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        continue
    # first line title
    title_line = lines[0].strip('#\n ').strip()
    title = html.escape(title_line)

    html_lines = []
    for line in lines:
        stripped = line.strip('\n')
        if stripped.startswith('#'):
            level = len(stripped) - len(stripped.lstrip('#'))
            text = stripped.strip('# ').strip()
            html_lines.append(f'<h{level}>{html.escape(text)}</h{level}>')
        elif stripped == '':
            html_lines.append('<p></p>')
        else:
            html_lines.append('<p>' + html.escape(stripped) + '</p>')
    chapter_html = '\n'.join(html_lines)
    chapters.append({'title': title, 'content': chapter_html})

# parse appendix book list
book_list_path = os.path.join(CONTENT_DIR, '2-appendix1-sample.markdown')
books = []
if os.path.exists(book_list_path):
    with open(book_list_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            m = re.match(r'\d+\u3001(.+)', line)  # digits followed by ideographic comma
            if m:
                books.append(m.group(1))

# generate html
os.makedirs('web', exist_ok=True)
with open('web/index.html', 'w', encoding='utf-8') as f:
    f.write('<!DOCTYPE html>\n<html lang="zh">\n<head>\n<meta charset="utf-8">\n')
    f.write('<title>2014年值得你阅读的100本书</title>\n')
    f.write('<link rel="stylesheet" href="style.css">\n')
    f.write('</head>\n<body>\n')
    f.write('<h1>2014年值得你阅读的100本书</h1>\n')
    if books:
        f.write('<section class="book-list">\n')
        for b in books:
            f.write('<div class="book-card">')
            f.write('<div class="cover">封面</div>')
            f.write(f'<div class="title">{html.escape(b)}</div>')
            f.write('</div>\n')
        f.write('</section>\n')

    for ch in chapters:
        f.write('<details class="chapter">\n')
        f.write(f'<summary>{ch["title"]}</summary>\n')
        f.write(ch['content'])
        f.write('\n</details>\n')

    f.write('</body>\n</html>')
