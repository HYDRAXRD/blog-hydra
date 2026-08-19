# 📝 How to Publish a New Blog Post

Publishing a post is **as simple as creating one file**. No code needed.

## Step 1 — Create a new `.json` file in this folder

Name the file using the post slug (lowercase, hyphens, no spaces). Example:
```
src/data/posts/my-new-post.json
```

## Step 2 — Fill in the template

Copy and paste this:

```json
{
  "id": "my-new-post",
  "title": "Your Post Title Here",
  "slug": "my-new-post",
  "excerpt": "A short 1-2 sentence summary shown on the blog listing page.",
  "content": "# Post Title\n\nWrite your full article here using Markdown.\n\n## Section Title\n\nParagraph text goes here.\n\n- Bullet point one\n- Bullet point two",
  "category": "News",
  "author": "HYDRA Team",
  "date": "2026-08-19",
  "readingTime": 5,
  "featured": false,
  "coverImage": "/images/my-cover.jpg",
  "tags": ["news", "hydra"]
}
```

## Available Categories
- `News`
- `Ecosystem`
- `Community`
- `Game Updates`
- `Guides`
- `Announcements`

## Markdown Formatting in `content`
| Syntax | Result |
|---|---|
| `# Heading 1` | Large title |
| `## Heading 2` | Section title |
| `**bold**` | **Bold text** |
| `*italic*` | *Italic text* |
| `` `code` `` | Inline code |
| `- item` | Bullet list |
| `[text](url)` | Hyperlink |
| `\n` | Line break (use inside JSON strings) |

## Set a Post as Featured
Set `"featured": true` — only the most recent featured post appears in the hero slot.

## Cover Images
Put image files in `public/images/` and reference them as `"/images/filename.jpg"`.
Leave `"coverImage": ""` to use the default gradient placeholder.

## That's it! 🎉
Save the file → commit → the blog updates automatically on next deploy.
