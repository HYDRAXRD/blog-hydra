"""Update coverImage for all existing posts using Unsplash API."""
import os
import json
import urllib.request
import urllib.parse
import random

UNSPLASH_API_KEY = os.environ.get("UNSPLASH_API_KEY", "")
POSTS_DIR = "src/data/posts"
INDEX_PATH = "public/posts-index.json"

# Map keywords found in tags/title/slug to a focused Unsplash query
IMAGE_QUERIES = {
    "hydra":       "blockchain crypto dragon dark",
    "hydraswap":   "decentralized exchange cryptocurrency dark",
    "doge":        "dogecoin shiba inu cryptocurrency",
    "dogecoin":    "dogecoin shiba inu cryptocurrency",
    "shib":        "shiba inu dog cryptocurrency",
    "shiba":       "shiba inu dog cryptocurrency",
    "pepe":        "frog meme cryptocurrency digital",
    "wif":         "dog hat cryptocurrency solana",
    "bonk":        "dog cryptocurrency solana airdrop",
    "floki":       "viking warrior cryptocurrency",
    "memecoin":    "meme cryptocurrency rocket moon",
    "market":      "cryptocurrency market chart bitcoin",
    "analysis":    "cryptocurrency market chart bitcoin",
    "defi":        "decentralized finance blockchain network",
    "radix":       "blockchain network nodes blue",
    "guide":       "crypto guide compass research",
    "risk":        "risk warning cryptocurrency danger",
    "psychology":  "trading psychology brain decision",
    "millionaire": "crypto wealth gold coins success",
    "history":     "crypto wealth gold coins success",
    "culture":     "meme cryptocurrency rocket moon",
    "trading":     "trading psychology brain decision",
    "safety":      "risk warning cryptocurrency danger",
    "solana":      "solana blockchain purple cryptocurrency",
    "bitcoin":     "bitcoin gold cryptocurrency dark",
}
DEFAULT_QUERY = "cryptocurrency bitcoin dark abstract"


def get_query_for_post(post: dict) -> str:
    """Determine the best Unsplash search query based on post metadata."""
    tags = [t.lower() for t in post.get("tags", [])]
    title = post.get("title", "").lower()
    slug = post.get("slug", "").lower()
    combined = " ".join(tags) + " " + title + " " + slug
    for key, query in IMAGE_QUERIES.items():
        if key in combined:
            return query
    return DEFAULT_QUERY


def fetch_unsplash_image(query: str) -> str:
    """Search Unsplash for a landscape photo matching the query."""
    try:
        params = urllib.parse.urlencode({
            "query": query,
            "orientation": "landscape",
            "per_page": 10,
            "content_filter": "high",
        })
        url = f"https://api.unsplash.com/search/photos?{params}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Client-ID {UNSPLASH_API_KEY}",
                "Accept-Version": "v1",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        results = data.get("results", [])
        if not results:
            print(f"  No results for '{query}'")
            return ""
        photo = random.choice(results[:5])
        raw_url = photo["urls"]["raw"]
        image_url = f"{raw_url}&w=1200&h=630&fit=crop&auto=format&q=80"
        author = photo.get("user", {}).get("name", "unknown")
        print(f"  -> photo id={photo['id']} by {author}")
        return image_url
    except Exception as e:
        print(f"  ERROR fetching image: {e}")
        return ""


if not UNSPLASH_API_KEY:
    print("ERROR: UNSPLASH_API_KEY environment variable is not set. Aborting.")
    raise SystemExit(1)

if not os.path.exists(POSTS_DIR):
    print(f"ERROR: Posts directory not found: {POSTS_DIR}")
    raise SystemExit(1)

# --- Process each post JSON file ---
updated = 0
skipped = 0
posts_map: dict = {}

post_files = sorted(f for f in os.listdir(POSTS_DIR) if f.endswith(".json"))
print(f"Found {len(post_files)} post(s) to process.\n")

for filename in post_files:
    path = os.path.join(POSTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        try:
            post = json.load(f)
        except json.JSONDecodeError as err:
            print(f"[{filename}] SKIP — invalid JSON: {err}")
            skipped += 1
            continue

    query = get_query_for_post(post)
    print(f"[{filename}] query='{query}'")

    new_url = fetch_unsplash_image(query)
    if new_url:
        post["coverImage"] = new_url
        with open(path, "w", encoding="utf-8") as f:
            json.dump(post, f, indent=2, ensure_ascii=False)
        print(f"  UPDATED: {new_url[:80]}...")
        updated += 1
    else:
        print(f"  SKIPPED (no image returned)")
        skipped += 1

    posts_map[post.get("slug", "")] = post

# --- Sync coverImage into posts-index.json ---
if os.path.exists(INDEX_PATH):
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        try:
            index = json.load(f)
        except json.JSONDecodeError:
            index = []

    changed = 0
    for i, entry in enumerate(index):
        slug = entry.get("slug", "")
        if slug in posts_map and posts_map[slug].get("coverImage"):
            old = entry.get("coverImage", "")
            new = posts_map[slug]["coverImage"]
            if old != new:
                index[i]["coverImage"] = new
                changed += 1

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"\nposts-index.json updated ({changed} entries changed).")
else:
    print(f"WARNING: {INDEX_PATH} not found — index not updated.")

print(f"\nDone. {updated} updated, {skipped} skipped.")
