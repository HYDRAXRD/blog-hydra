import json
import os
from datetime import datetime, timezone

BASE_URL = "https://hydraxrd.com/blog"
INDEX_PATH = "public/posts-index.json"
SITEMAP_PATH = "public/sitemap.xml"

today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

posts = []
if os.path.exists(INDEX_PATH):
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        try:
            posts = json.load(f)
        except Exception:
            posts = []

lines = ['<?xml version="1.0" encoding="UTF-8"?>']
lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

# Homepage
lines.append('  <url>')
lines.append(f'    <loc>{BASE_URL}</loc>')
lines.append(f'    <lastmod>{today}</lastmod>')
lines.append('    <changefreq>daily</changefreq>')
lines.append('    <priority>1.0</priority>')
lines.append('  </url>')

# Each post
for post in posts:
    slug = post.get("slug") or post.get("id", "")
    date = post.get("date", today)
    if not slug:
        continue
    lines.append('  <url>')
    lines.append(f'    <loc>{BASE_URL}/post/{slug}</loc>')
    lines.append(f'    <lastmod>{date}</lastmod>')
    lines.append('    <changefreq>monthly</changefreq>')
    lines.append('    <priority>0.8</priority>')
    lines.append('  </url>')

lines.append('</urlset>')

os.makedirs("public", exist_ok=True)
with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Sitemap generated: {len(posts)} posts -> {SITEMAP_PATH}")
