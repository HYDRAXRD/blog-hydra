import os
import json
import urllib.request
import urllib.error
import urllib.parse
import re
from datetime import datetime, timezone
import sys
import random

now = datetime.now(timezone.utc)
today = now.strftime("%Y-%m-%d")
hour = now.hour
api_key = os.environ["OPENROUTER_API_KEY"]
unsplash_key = os.environ.get("UNSPLASH_API_KEY", "")
timestamp = now.strftime("%Y-%m-%d-%H")

FACTS_PATH = ".github/data/hydra-facts.md"
try:
    with open(FACTS_PATH, "r", encoding="utf-8") as f:
        HYDRA_FACTS = f.read()
except FileNotFoundError:
    HYDRA_FACTS = ""
    print("WARNING: hydra-facts.md not found")


def title_to_slug(title: str) -> str:
    """Convert a post title to a clean URL slug without dates."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    slug = slug[:80].rstrip("-")
    return slug


def generate_sitemap(posts_index: list) -> str:
    """Generate a full sitemap.xml from the posts index."""
    BASE_URL = "https://hydraxrd.com"
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '',
        '  <!-- Static pages -->',
        '  <url>',
        f'    <loc>{BASE_URL}/blog</loc>',
        f'    <lastmod>{today}</lastmod>',
        '    <changefreq>daily</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
    ]
    for post in posts_index:
        slug = post.get("slug", "")
        date = post.get("date", today)
        if not slug:
            continue
        lines += [
            '',
            '  <url>',
            f'    <loc>{BASE_URL}/blog/post/{slug}</loc>',
            f'    <lastmod>{date}</lastmod>',
            '    <changefreq>monthly</changefreq>',
            '    <priority>0.8</priority>',
            '  </url>',
        ]
    lines += ['', '</urlset>', '']
    return "\n".join(lines)


def format_price(price):
    if price is None or price == "N/A":
        return "N/A"
    try:
        price = float(price)
    except (ValueError, TypeError):
        return str(price)
    if price >= 1:
        return f"{price:,.2f}"
    if price >= 0.01:
        return f"{price:.4f}"
    formatted = f"{price:.10f}".rstrip("0")
    return formatted


def fetch_unsplash_image(query: str, width: int = 1200, height: int = 630) -> str:
    """
    Fetch a relevant image URL from Unsplash using their free API.
    Falls back to a curated fallback URL if the API is unavailable.
    """
    if not unsplash_key:
        print("WARNING: UNSPLASH_API_KEY not set, using fallback image")
        return _unsplash_fallback(query)

    # Map topic keywords to better Unsplash search terms
    QUERY_MAP = {
        "HYDRA": "blockchain crypto dragon dark",
        "HydraSwap": "decentralized exchange cryptocurrency dark",
        "Dogecoin": "dogecoin shiba inu cryptocurrency",
        "DOGE": "dogecoin shiba inu cryptocurrency",
        "Shiba": "shiba inu dog cryptocurrency",
        "SHIB": "shiba inu dog cryptocurrency",
        "Pepe": "frog meme cryptocurrency digital",
        "PEPE": "frog meme cryptocurrency digital",
        "WIF": "dog hat cryptocurrency solana",
        "dogwifhat": "dog hat cryptocurrency solana",
        "BONK": "dog cryptocurrency solana airdrop",
        "FLOKI": "viking warrior cryptocurrency",
        "memecoin": "meme cryptocurrency rocket moon",
        "market": "cryptocurrency market chart bitcoin",
        "DeFi": "decentralized finance blockchain network",
        "Radix": "blockchain network nodes blue",
        "guide": "crypto guide compass research",
        "risks": "risk warning cryptocurrency danger",
        "psychology": "trading psychology brain decision",
        "millionaires": "crypto wealth gold coins success",
    }

    search_query = QUERY_MAP.get(query, f"{query} cryptocurrency")
    print(f"Fetching Unsplash image for query: '{search_query}'")

    try:
        params = urllib.parse.urlencode({
            "query": search_query,
            "orientation": "landscape",
            "per_page": 10,
            "content_filter": "high",
        })
        url = f"https://api.unsplash.com/search/photos?{params}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Client-ID {unsplash_key}",
                "Accept-Version": "v1",
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        results = data.get("results", [])
        if not results:
            print(f"No Unsplash results for '{search_query}', using fallback")
            return _unsplash_fallback(query)

        # Pick a random result from the top results for variety
        photo = random.choice(results[:5])
        # Use raw URL with custom dimensions via Unsplash image CDN params
        raw_url = photo["urls"]["raw"]
        image_url = f"{raw_url}&w={width}&h={height}&fit=crop&auto=format&q=80"
        print(f"Unsplash image selected: {photo.get('id')} by {photo.get('user', {}).get('name', 'unknown')}")
        return image_url

    except Exception as e:
        print(f"Unsplash fetch failed: {e}, using fallback")
        return _unsplash_fallback(query)


def _unsplash_fallback(topic_key: str) -> str:
    """
    Curated fallback Unsplash photo IDs per topic.
    These are stable, high-quality photos available without API key.
    """
    FALLBACKS = {
        "HYDRA":      "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&h=630&fit=crop&auto=format",
        "HydraSwap":  "https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=1200&h=630&fit=crop&auto=format",
        "Dogecoin":   "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=630&fit=crop&auto=format",
        "DOGE":       "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=630&fit=crop&auto=format",
        "Shiba":      "https://images.unsplash.com/photo-1620321023374-d1a68fbc720d?w=1200&h=630&fit=crop&auto=format",
        "SHIB":       "https://images.unsplash.com/photo-1620321023374-d1a68fbc720d?w=1200&h=630&fit=crop&auto=format",
        "Pepe":       "https://images.unsplash.com/photo-1639762681057-408e52192e55?w=1200&h=630&fit=crop&auto=format",
        "PEPE":       "https://images.unsplash.com/photo-1639762681057-408e52192e55?w=1200&h=630&fit=crop&auto=format",
        "WIF":        "https://images.unsplash.com/photo-1645731012575-3799282e8da5?w=1200&h=630&fit=crop&auto=format",
        "BONK":       "https://images.unsplash.com/photo-1643101809204-6fb869816dbe?w=1200&h=630&fit=crop&auto=format",
        "FLOKI":      "https://images.unsplash.com/photo-1589254065878-42c9da997008?w=1200&h=630&fit=crop&auto=format",
        "memecoin":   "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200&h=630&fit=crop&auto=format",
        "market":     "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=630&fit=crop&auto=format",
        "DeFi":       "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&h=630&fit=crop&auto=format",
        "Radix":      "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&h=630&fit=crop&auto=format",
        "guide":      "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&h=630&fit=crop&auto=format",
        "risks":      "https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?w=1200&h=630&fit=crop&auto=format",
        "psychology": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&h=630&fit=crop&auto=format",
        "millionaires":"https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=1200&h=630&fit=crop&auto=format",
    }
    return FALLBACKS.get(
        topic_key,
        "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200&h=630&fit=crop&auto=format"
    )


def fetch_coingecko_news(coin_id="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false"
        req = urllib.request.Request(url, headers={"User-Agent": "HYDRABlog/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return {
            "price_usd": data.get("market_data", {}).get("current_price", {}).get("usd", "N/A"),
            "change_24h": data.get("market_data", {}).get("price_change_percentage_24h", "N/A"),
            "market_cap_usd": data.get("market_data", {}).get("market_cap", {}).get("usd", "N/A"),
        }
    except Exception as e:
        print(f"CoinGecko fetch failed for {coin_id}: {e}")
        return {}


def fetch_trending_coins():
    try:
        url = "https://api.coingecko.com/api/v3/search/trending"
        req = urllib.request.Request(url, headers={"User-Agent": "HYDRABlog/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        coins = data.get("coins", [])[:5]
        return [{"name": c["item"]["name"], "symbol": c["item"]["symbol"], "market_cap_rank": c["item"].get("market_cap_rank", "N/A")} for c in coins]
    except Exception as e:
        print(f"Trending fetch failed: {e}")
        return []


HYDRA_TOPICS = [
    ("HYDRA", "Write an educational article about the HYDRA memecoin on Radix DLT. Focus on the weekly burn mechanism (100,000 HYDRA burned every week), the HydraSwap DEX, and what makes it unique as a community-driven token launched on February 8, 2026."),
    ("HYDRA", "Write an article explaining how to buy HYDRA token on Radix DLT using HydraSwap. Explain what Radix DLT is, why it matters for DeFi, and what the HYDRA community is building."),
    ("HydraSwap", "Write about HydraSwap, the decentralized exchange (DEX) built on Radix DLT where HYDRA token is traded. Explain how DEXs work, why Radix DLT's asset-oriented model is different from EVM chains, and the role of HydraSwap in the HYDRA ecosystem."),
]

MEMECOIN_TOPICS = [
    ("Dogecoin", "Write the story of Dogecoin (DOGE): from joke to $80B market cap. Cover the 2013 origin, Reddit community, Elon Musk influence, and the 2021 explosion. Use real facts only."),
    ("Shiba", "Write a deep dive into Shiba Inu (SHIB): the DOGE killer narrative, ShibArmy, Vitalik Buterin burn event, Shibarium launch. Use real data from CoinGecko."),
    ("Pepe", "Write about Pepe (PEPE) coin: how a 4chan frog became a top memecoin in 2023. Cover the cultural roots and on-chain data."),
    ("WIF", "Write about WIF (dogwifhat) on Solana: the hat-wearing dog that reached multi-billion market cap. Cover the meme origin and Solana memecoin culture."),
    ("BONK", "Write about BONK on Solana: the community airdrop that energized Solana in December 2022. Cover how it distributed tokens and what happened next."),
    ("FLOKI", "Write about FLOKI: the Viking-branded memecoin, FlokiFi DeFi suite, and global marketing. Use real data."),
    ("millionaires", "Write about the top 5 memecoins that gave life-changing returns to early holders: DOGE, SHIB, PEPE, WIF, BONK. What patterns did they share?"),
    ("guide", "Write a guide: How to research a memecoin before investing. Cover on-chain data, community signals, liquidity, tokenomics red flags, and timing."),
    ("memecoin", "Write about memecoin culture: why internet memes are the most powerful marketing force in crypto, community as product, and viral mechanics."),
    ("risks", "Write an honest article about the risks of memecoins: rug pulls, wash trading, low liquidity traps, and how to protect yourself."),
]

MARKET_TOPICS = [
    ("market", "Write a market analysis of the current memecoin sector. Use trending coin data provided to discuss narratives and Bitcoin dominance signals."),
    ("DeFi", "Write about DeFi on Radix DLT: why Radix's asset-oriented model differs from EVM, and the opportunity for new projects like HYDRA."),
    ("psychology", "Write about the psychology of memecoin investing: FOMO, diamond hands, paper hands, and how emotion drives price action."),
]

if hour < 13:
    pool = HYDRA_TOPICS
elif hour < 20:
    pool = MEMECOIN_TOPICS
else:
    pool = MARKET_TOPICS + MEMECOIN_TOPICS

image_key, topic = random.choice(pool)

market_context = ""
coin_map = {
    "Dogecoin": "dogecoin", "DOGE": "dogecoin",
    "Shiba": "shiba-inu", "SHIB": "shiba-inu",
    "Pepe": "pepe", "PEPE": "pepe",
    "WIF": "dogwifcoin", "dogwifhat": "dogwifcoin",
    "BONK": "bonk", "FLOKI": "floki",
    "market": "bitcoin",
}
if image_key in coin_map:
    print(f"Fetching CoinGecko data for {coin_map[image_key]}...")
    cg_data = fetch_coingecko_news(coin_map[image_key])
    if cg_data:
        price_formatted = format_price(cg_data.get("price_usd", "N/A"))
        change_raw = cg_data.get("change_24h", "N/A")
        try:
            change_formatted = f"{float(change_raw):.2f}"
        except (ValueError, TypeError):
            change_formatted = str(change_raw)
        market_context = (
            f"\nReal Market Data (CoinGecko, fetched now):\n"
            f"Current price: ${price_formatted}\n"
            f"24h change: {change_formatted}%\n"
            f"Market cap: ${cg_data.get('market_cap_usd', 'N/A')} USD\n"
        )
        print(f"CoinGecko data (formatted): price=${price_formatted}, 24h={change_formatted}%")

if image_key == "market":
    trending = fetch_trending_coins()
    if trending:
        market_context += "\nTrending coins right now (CoinGecko):\n"
        for t in trending:
            market_context += f"{t['name']} ({t['symbol']}) - Rank #{t['market_cap_rank']}\n"

if pool == HYDRA_TOPICS:
    category = random.choice(["News", "Guides"])
elif image_key in ["Dogecoin","DOGE","Shiba","SHIB","Pepe","PEPE","WIF","dogwifhat","BONK","FLOKI","memecoin","millionaires"]:
    category = "Moonshots"
elif image_key == "guide":
    category = "Guides"
elif image_key in ["market","DeFi","Radix"]:
    category = "Market Analysis"
elif image_key == "psychology":
    category = "Market Analysis"
else:
    category = "Moonshots"

tags_map = {
    "HYDRA": ["hydra", "radix", "memecoin"],
    "HydraSwap": ["hydra", "hydraswap", "dex", "radix"],
    "Dogecoin": ["doge", "dogecoin", "memecoin"],
    "Shiba": ["shib", "shiba", "memecoin"],
    "Pepe": ["pepe", "memecoin", "culture"],
    "WIF": ["wif", "solana", "memecoin"],
    "BONK": ["bonk", "solana", "memecoin"],
    "FLOKI": ["floki", "memecoin", "defi"],
    "market": ["market", "analysis", "crypto"],
    "guide": ["guide", "memecoin", "crypto"],
    "risks": ["risk", "safety", "memecoin"],
    "psychology": ["psychology", "trading", "memecoin"],
    "millionaires": ["memecoin", "history", "doge"],
    "DeFi": ["defi", "radix", "blockchain"],
}
tags = tags_map.get(image_key, ["memecoin", "crypto"])

disclaimer = (
    "\n\n---\n\n"
    "**\u26a0\ufe0f Disclaimer:** This article is for educational and entertainment purposes only. "
    "Nothing here constitutes financial advice. Cryptocurrency investments are highly volatile and speculative. "
    "Always do your own research (DYOR) before making any investment decisions. "
    "Past performance is not indicative of future results."
)

hydra_instruction = ""
if pool == HYDRA_TOPICS and HYDRA_FACTS:
    hydra_instruction = f"\n\nMANDATORY: Official HYDRA Facts - use ONLY these, never invent:\n{HYDRA_FACTS}\n"

system_msg = (
    "You are the content writer for HYDRA Chronicles, a crypto and memecoin blog. "
    "You write accurate, engaging, human-sounding articles. "
    "CRITICAL FORMATTING RULES that you must follow without exception:\n"
    "1. NEVER use bullet points or dashes (-) to list items. Write everything as flowing prose paragraphs instead.\n"
    "2. Use ## for main section titles only (not ### or ####). Keep section titles short and punchy.\n"
    "3. NEVER use ### or #### headers ever.\n"
    "4. ALL links must be masked as markdown hyperlinks using the format [visible text](url). NEVER show a raw URL.\n"
    "5. Write in a natural, human tone. Avoid sounding like AI. No robotic transitions like 'Furthermore', 'Moreover', 'In conclusion'.\n"
    "6. You NEVER invent statistics, prices, or claims not provided to you.\n"
    "7. PRICE FORMATTING: When writing any crypto price, ALWAYS use standard decimal notation (e.g. $0.00002083). NEVER use scientific notation (e.g. 2.079e-05). NEVER use more than 2 decimal places for percentages (e.g. 3.98%, never 3.98116%).\n"
    "8. SLUG RULE: The slug must be derived ONLY from the title, lowercase, hyphens only, no dates, no timestamps. Example: title 'Dogecoin: From Joke to $80B' -> slug 'dogecoin-from-joke-to-80b'.\n"
    "Return ONLY a raw JSON object. No markdown fences. No extra text."
)

user_msg = (
    f"Today is {today}. {topic}\n"
    f"{hydra_instruction}"
    f"{market_context}\n"
    "Write a compelling article of AT LEAST 1200 words. "
    "Use ## section headers and bold text for emphasis. "
    "NO bullet points, NO dashes, NO ### headers. Write in flowing paragraphs only. "
    "ALL links must be [text](url) format, never raw URLs. "
    "IMPORTANT: Write all crypto prices in standard decimal notation (e.g. $0.00002083), NEVER scientific notation. Round percentages to 2 decimal places. "
    "Only use facts provided or widely established public knowledge. "
    f"End the content field with this exact disclaimer: {disclaimer}\n\n"
    "Return ONLY this JSON:\n"
    "{\n"
    '  "title": "<catchy engaging title>",\n'
    '  "slug": "<URL slug derived from the title: lowercase, hyphens only, NO dates, NO timestamps, max 80 chars. Example: dogecoin-from-joke-to-80b>",\n'
    '  "excerpt": "<compelling summary under 200 chars, prices in decimal notation only>",\n'
    '  "content": "<full article in markdown, use \\n for newlines, minimum 1200 words, NO bullet points, NO dashes, NO ### headers, ALL links masked, prices always in decimal notation>",\n'
    f'  "category": "{category}",\n'
    '  "author": "HYDRA",\n'
    f'  "date": "{today}",\n'
    '  "readingTime": 6,\n'
    '  "featured": false,\n'
    '  "coverImage": "",\n'
    f'  "tags": {json.dumps(tags)}\n'
    "}"
)

MODELS = [
    "openrouter/free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
]

response_data = None
content = ""

for model in MODELS:
    print(f"Trying model: {model}")
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.7,
        "max_tokens": 4500
    }).encode()

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://hydraxrd.com",
            "X-Title": "HYDRA Blog"
        }
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        msg = data.get("choices", [{}])[0].get("message", {})
        content = msg.get("content") or msg.get("reasoning") or ""
        if not content or not content.strip():
            print(f"Model {model} returned empty, trying next...")
            continue
        content = content.strip()
        response_data = data
        print(f"Success with {model} ({len(content)} chars)")
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Model {model} failed: {e.code} - {body[:200]}")
        continue

if not response_data or not content:
    print("All models failed. Exiting.")
    sys.exit(1)

if content.startswith("```"):
    lines = content.split("\n")
    content = "\n".join(lines[1:-1]).strip()

if not content.startswith("{"):
    start = content.find("{")
    end = content.rfind("}") + 1
    if start != -1 and end > start:
        content = content[start:end]

try:
    post = json.loads(content)
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    print(f"Raw content: {content[:500]}")
    sys.exit(1)

# --- Enforce clean slug from title (safety net) ---
raw_slug = post.get("slug", "")
if not raw_slug or re.search(r"\d{4}-\d{2}-\d{2}", raw_slug):
    raw_slug = title_to_slug(post.get("title", f"post-{timestamp}"))
    print(f"Slug regenerated from title: {raw_slug}")

# Deduplicate: if slug already exists, append short hash
existing_files = os.listdir("src/data/posts") if os.path.exists("src/data/posts") else []
existing_slugs = {f.replace(".json", "") for f in existing_files if f.endswith(".json")}
final_slug = raw_slug
if final_slug in existing_slugs:
    suffix = timestamp[-5:].replace("-", "")
    final_slug = f"{raw_slug}-{suffix}"
    print(f"Slug deduplicated: {final_slug}")

post["slug"] = final_slug
post["id"] = final_slug

word_count = len(post.get("content", "").split())
post["readingTime"] = max(1, round(word_count / 200))
post["author"] = "HYDRA"
post["category"] = category

# --- Fetch cover image from Unsplash ---
print(f"Fetching Unsplash image for topic key: {image_key}")
image_url = fetch_unsplash_image(image_key)
post["coverImage"] = image_url
print(f"Cover image URL: {image_url}")

# --- Save post JSON ---
os.makedirs("src/data/posts", exist_ok=True)
out_path = f"src/data/posts/{final_slug}.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(post, f, indent=2, ensure_ascii=False)
print(f"Saved: {out_path}")

# --- Update posts-index.json ---
index_path = "public/posts-index.json"
existing = []
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        try:
            existing = json.load(f)
        except Exception:
            existing = []

existing = [p for p in existing if p.get("slug") != final_slug]
existing.insert(0, post)

os.makedirs("public", exist_ok=True)
with open(index_path, "w", encoding="utf-8") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)
print(f"Index updated: {len(existing)} posts")

# --- Auto-update sitemap.xml ---
sitemap_path = "public/sitemap.xml"
sitemap_content = generate_sitemap(existing)
with open(sitemap_path, "w", encoding="utf-8") as f:
    f.write(sitemap_content)
print(f"Sitemap updated: {sitemap_path} ({len(existing)} posts)")

print(f"SUCCESS:{out_path}")
print(f"SLUG:{final_slug}")
