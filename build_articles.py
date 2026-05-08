#!/usr/bin/env python3
"""
build_articles.py — Convert articles/*.docx (and *.doc) into scripts/articles.js
==================================================================================

Word document format
--------------------
Each .docx file in the articles/ folder becomes one article.
The filename (without .docx) becomes the URL slug.

Structure inside the document:

  [Heading 1]  Article title
  [Normal]     Date: November 12, 2024
  [Normal]     Tags: Mac OS X, Snow Leopard, Opinion
  [Normal]     Excerpt: One or two sentence teaser for listings.
  [blank line — separates metadata from body]
  [rest of document — the article body]

Heading styles map to HTML:
  Heading 1 → <h2>
  Heading 2 → <h3>
  Heading 3 → <h4>
  List Bullet → <ul><li>
  List Number → <ol><li>
  Normal      → <p>
  Bold runs   → <strong>
  Italic runs → <em>

Usage
-----
  python3 build_articles.py

Run from the site root any time you add or edit a .docx file.
"""

import os
import re
import sys
import shutil
import subprocess
import tempfile
from datetime import datetime

try:
    from docx import Document
except ImportError:
    print("Error: python-docx is not installed.")
    print("Run: pip3 install python-docx")
    sys.exit(1)

ARTICLES_DIR = "articles"
OUTPUT_FILE  = "scripts/articles.js"
RSS_FILE     = "feed.xml"

# ── Update this to your real URL when you deploy ──────────────────────────────
SITE_URL = "https://example.com"


# ── .doc conversion helpers ────────────────────────────────────────────────────

def find_libreoffice():
    """Find the LibreOffice executable; return its path or None."""
    candidates = [
        '/Applications/LibreOffice.app/Contents/MacOS/soffice',
        '/usr/local/bin/soffice',
        shutil.which('soffice'),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def convert_doc_to_docx(doc_path):
    """Convert a legacy .doc file to a temporary .docx.

    Tries LibreOffice first, then falls back to macOS textutil.
    Returns (docx_path, tmp_dir) on success, or (None, None) on failure.
    The caller is responsible for deleting tmp_dir when done.
    """
    tmp_dir = tempfile.mkdtemp()

    # ── Try LibreOffice ──────────────────────────────────────────
    lo = find_libreoffice()
    if lo:
        try:
            result = subprocess.run(
                [lo, '--headless', '--convert-to', 'docx',
                 '--outdir', tmp_dir, doc_path],
                capture_output=True, timeout=60
            )
            if result.returncode == 0:
                base = os.path.splitext(os.path.basename(doc_path))[0]
                out = os.path.join(tmp_dir, base + '.docx')
                if os.path.isfile(out):
                    return out, tmp_dir
        except Exception:
            pass

    # ── Fall back to macOS textutil (built-in since 10.4) ────────
    textutil = '/usr/bin/textutil'
    if os.path.isfile(textutil):
        try:
            out = os.path.join(tmp_dir, 'converted.docx')
            result = subprocess.run(
                [textutil, '-convert', 'docx', '-output', out, doc_path],
                capture_output=True, timeout=60
            )
            if result.returncode == 0 and os.path.isfile(out):
                return out, tmp_dir
        except Exception:
            pass

    shutil.rmtree(tmp_dir, ignore_errors=True)
    return None, None


# ── Helpers ────────────────────────────────────────────────────────────────────

def slug_from_filename(filename):
    """'My Great Article.docx'  →  'my-great-article'"""
    name = os.path.splitext(filename)[0]
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    return name.strip('-')


def date_to_iso(date_str):
    """Parse a human date string to YYYY-MM-DD for sorting."""
    for fmt in ('%B %d, %Y', '%d %B %Y', '%Y-%m-%d', '%d/%m/%Y', '%B %Y'):
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return '1970-01-01'


def runs_to_html(paragraph):
    """Convert a paragraph's runs to an HTML string, applying bold/italic."""
    html = ''
    for run in paragraph.runs:
        text = (run.text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))
        if not text:
            continue
        if run.bold and run.italic:
            text = '<strong><em>{}</em></strong>'.format(text)
        elif run.bold:
            text = '<strong>{}</strong>'.format(text)
        elif run.italic:
            text = '<em>{}</em>'.format(text)
        html += text
    return html


def paragraphs_to_html(paras):
    """Convert a list of (style_name, paragraph) tuples to a HTML string."""
    html = ''
    i = 0
    while i < len(paras):
        style, para = paras[i]
        text = para.text.strip()

        if not text:
            i += 1
            continue

        if 'Heading 1' in style:
            html += '<h2>{}</h2>'.format(runs_to_html(para))

        elif 'Heading 2' in style:
            html += '<h3>{}</h3>'.format(runs_to_html(para))

        elif 'Heading 3' in style or 'Heading 4' in style:
            html += '<h4>{}</h4>'.format(runs_to_html(para))

        elif 'List Bullet' in style:
            items = '<li>{}</li>'.format(runs_to_html(para))
            while i + 1 < len(paras) and 'List Bullet' in paras[i + 1][0]:
                i += 1
                items += '<li>{}</li>'.format(runs_to_html(paras[i][1]))
            html += '<ul>{}</ul>'.format(items)

        elif 'List Number' in style:
            items = '<li>{}</li>'.format(runs_to_html(para))
            while i + 1 < len(paras) and 'List Number' in paras[i + 1][0]:
                i += 1
                items += '<li>{}</li>'.format(runs_to_html(paras[i][1]))
            html += '<ol>{}</ol>'.format(items)

        else:
            html += '<p>{}</p>'.format(runs_to_html(para))

        i += 1
    return html


# ── Document parser ────────────────────────────────────────────────────────────

def parse_docx(filepath):
    """
    Return a dict with keys: title, date, dateiso, tags, excerpt, body.
    """
    doc = Document(filepath)

    title   = ''
    date    = ''
    tags    = []
    excerpt = ''
    body_paras = []

    META_KEYS = ('date:', 'tags:', 'excerpt:')
    metadata_done = False
    title_found   = False

    for para in doc.paragraphs:
        style = para.style.name
        text  = para.text.strip()

        # First Heading 1 is the article title
        if not title_found and 'Heading 1' in style:
            title = text
            title_found = True
            continue

        # Before the blank separator: read metadata key:value lines
        if not metadata_done:
            if not text:
                metadata_done = True
                continue
            lower = text.lower()
            if lower.startswith('date:'):
                date = text[5:].strip()
            elif lower.startswith('tags:'):
                tags = [t.strip() for t in text[5:].split(',') if t.strip()]
            elif lower.startswith('excerpt:'):
                excerpt = text[8:].strip()
            # If it doesn't look like metadata and title has been found,
            # treat it as the start of the body
            elif title_found and not any(lower.startswith(k) for k in META_KEYS):
                metadata_done = True
                body_paras.append((style, para))
            continue

        body_paras.append((style, para))

    body_html = paragraphs_to_html(body_paras)

    return {
        'title':   title,
        'date':    date,
        'dateiso': date_to_iso(date),
        'tags':    tags,
        'excerpt': excerpt,
        'body':    body_html,
    }


# ── JS serialisation ───────────────────────────────────────────────────────────

def js_str(s):
    """Escape a Python string for embedding in a JS single-quoted string."""
    s = s.replace('\\', '\\\\')
    s = s.replace("'",  "\\'")
    s = s.replace('\r', '')
    s = s.replace('\n', ' ')   # HTML doesn't need literal newlines
    return s


JS_HELPERS = r"""
/* ============================================================
   Shared helpers — used by article.html, index.html, articles.html
   ============================================================ */

function articleTagsHtml(tags) {
  var html = '';
  for (var i = 0; i < tags.length; i++) {
    html += '<span class="tag">' + tags[i] + '</span>';
  }
  return html;
}

function articleCardHtml(a) {
  var href = a.body ? 'article.html?article=' + a.slug : '#';
  return '<div class="article-item">' +
    '<div class="article-date">' + a.date + '</div>' +
    '<div class="article-title"><a href="' + href + '">' + a.title + '</a></div>' +
    '<div class="article-excerpt">' + a.excerpt + '</div>' +
    '<div class="article-tags">' + articleTagsHtml(a.tags) + '</div>' +
    '</div>';
}

/* Parse a single query-string parameter — Safari 4/5 safe */
function getQueryParam(name) {
  var search = window.location.search;
  if (!search || search.length < 2) { return null; }
  var pairs = search.substring(1).split('&');
  for (var i = 0; i < pairs.length; i++) {
    var kv = pairs[i].split('=');
    if (kv[0] === name) {
      return kv.length > 1 ? decodeURIComponent(kv[1].replace(/\+/g, ' ')) : '';
    }
  }
  return null;
}
"""


def write_articles_js(articles):
    lines = []
    lines.append('/* ================================================================')
    lines.append('   scripts/articles.js')
    lines.append('   AUTO-GENERATED by build_articles.py — do not edit by hand.')
    lines.append('   Edit .docx files in articles/ then run: python3 build_articles.py')
    lines.append('   ================================================================ */')
    lines.append('')
    lines.append('var ARTICLES = [')

    for idx, a in enumerate(articles):
        comma = ',' if idx < len(articles) - 1 else ''
        tags_js = ', '.join("'{}'".format(js_str(t)) for t in a['tags'])
        lines.append('  {')
        lines.append("    slug:    '{}',".format(js_str(a['slug'])))
        lines.append("    date:    '{}',".format(js_str(a['date'])))
        lines.append("    dateiso: '{}',".format(js_str(a['dateiso'])))
        lines.append("    title:   '{}',".format(js_str(a['title'])))
        lines.append("    excerpt: '{}',".format(js_str(a['excerpt'])))
        lines.append("    tags:    [{}],".format(tags_js))
        lines.append("    body:    '{}'".format(js_str(a['body'])))
        lines.append('  }}{}'.format(comma))

    lines.append('];')
    lines.append(JS_HELPERS)

    content = '\n'.join(lines)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)


# ── RSS helpers ───────────────────────────────────────────────────────────────

def xml_escape(s):
    """Escape a string for safe embedding in XML."""
    s = s.replace('&',  '&amp;')
    s = s.replace('<',  '&lt;')
    s = s.replace('>',  '&gt;')
    s = s.replace('"',  '&quot;')
    s = s.replace("'",  '&apos;')
    return s


def iso_to_rfc822(dateiso):
    """Convert YYYY-MM-DD to RFC 822 date string required by RSS 2.0."""
    try:
        dt = datetime.strptime(dateiso, '%Y-%m-%d')
        return dt.strftime('%a, %d %b %Y 00:00:00 +0000')
    except ValueError:
        return 'Thu, 01 Jan 1970 00:00:00 +0000'


def write_feed_xml(articles):
    """Write an RSS 2.0 feed to feed.xml."""
    now = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">')
    lines.append('  <channel>')
    lines.append("    <title>Harry's Site</title>")
    lines.append('    <link>{}</link>'.format(SITE_URL))
    lines.append('    <description>writing · photography · projects · whatever else</description>')
    lines.append('    <language>en-gb</language>')
    lines.append('    <lastBuildDate>{}</lastBuildDate>'.format(now))
    lines.append('    <atom:link href="{}/feed.xml" rel="self" type="application/rss+xml"/>'.format(SITE_URL))
    lines.append('')

    published = [a for a in articles if a.get('body')]
    for a in published:
        url = '{}/article.html?article={}'.format(SITE_URL, a['slug'])
        lines.append('    <item>')
        lines.append('      <title>{}</title>'.format(xml_escape(a['title'])))
        lines.append('      <link>{}</link>'.format(url))
        lines.append('      <description>{}</description>'.format(xml_escape(a['excerpt'])))
        lines.append('      <pubDate>{}</pubDate>'.format(iso_to_rfc822(a['dateiso'])))
        lines.append('      <guid isPermaLink="true">{}</guid>'.format(url))
        lines.append('    </item>')

    lines.append('  </channel>')
    lines.append('</rss>')

    content = '\n'.join(lines) + '\n'
    with open(RSS_FILE, 'w', encoding='utf-8') as f:
        f.write(content)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    # Create articles/ directory if it doesn't exist
    if not os.path.isdir(ARTICLES_DIR):
        os.makedirs(ARTICLES_DIR)
        print("Created articles/ — add your .docx (or .doc) files there and re-run.")
        return

    all_files = sorted(
        f for f in os.listdir(ARTICLES_DIR)
        if f.lower().endswith(('.docx', '.doc')) and not f.startswith('~')
    )

    if not all_files:
        print("No .docx or .doc files found in articles/  — nothing to do.")
        return

    articles = []
    for filename in all_files:
        filepath = os.path.join(ARTICLES_DIR, filename)
        slug = slug_from_filename(filename)
        tmp_dir = None

        # Convert legacy .doc to a temporary .docx before parsing
        if filename.lower().endswith('.doc'):
            print("  Converting {} (.doc → .docx)...".format(filename))
            parse_path, tmp_dir = convert_doc_to_docx(filepath)
            if parse_path is None:
                print("    WARNING: could not convert {} — skipping.".format(filename))
                print("    Install LibreOffice (brew install --cask libreoffice) to enable .doc support.")
                continue
        else:
            parse_path = filepath

        print("  Reading {}...".format(filename))
        try:
            data = parse_docx(parse_path)
        except Exception as exc:
            print("    WARNING: could not parse {} — {}".format(filename, exc))
            if tmp_dir:
                shutil.rmtree(tmp_dir, ignore_errors=True)
            continue
        finally:
            if tmp_dir:
                shutil.rmtree(tmp_dir, ignore_errors=True)

        if not data['title']:
            data['title'] = os.path.splitext(filename)[0]

        data['slug'] = slug
        articles.append(data)

    # Sort newest first
    articles.sort(key=lambda a: a['dateiso'], reverse=True)

    write_articles_js(articles)
    write_feed_xml(articles)

    print("\nWrote {} article(s) to {}".format(len(articles), OUTPUT_FILE))
    print("Wrote RSS feed to {}".format(RSS_FILE))
    for a in articles:
        status = 'OK' if a['body'] else 'no body'
        print("  [{}]  {} ({})  [{}]".format(a['dateiso'], a['title'], a['slug'], status))


if __name__ == '__main__':
    main()
