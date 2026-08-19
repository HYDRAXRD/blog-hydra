import os
import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
import sys
import random

now = datetime.now(timezone.utc)
today = now.strftime("%Y-%m-%d")
hour = now.hour
api_key = os.environ["OPENROUTER_API_KEY"]
timestamp = now.strftime("%Y-%m-%d-%H")

HYDRA_TOPICS = [
    "Write about the HYDRA ecosystem on Radix DLT. Cover one of: HydraSwap DEX, HydraBurn token burn mechanics, HydraBattleArena game, HYDRA staking rewards, or community governance. Be energetic and hype-driven.",
    "Write about why HYDRA on Radix DLT is positioned to be the next big memecoin. Cover Radix's unique tech advantages, HYDRA tokenomics, and community growth.",
    "Write a guide on how to buy and hold HYDRA token on Radix DLT. Include wallet setup, where to swap, and why the community is bullish.",
]

MEMECOIN_TOPICS = [
    "Write the full story of Dogecoin (DOGE): from joke to $80B market cap. Cover the 2013 origin, Reddit community, Elon Musk tweets, and the 2021 explosion.",
    "Write a deep dive into Shiba Inu (SHIB): the DOGE killer narrative, ShibArmy, Vitalik Buterin burn, Shibarium launch, and price history.",
    "Write about Pepe (PEPE) coin: how a 4chan frog became a top-10 memecoin in 2023, the cultural roots, and the community explosion.",
    "Write about WIF (dogwifhat) on Solana: the hat-wearing dog that hit $4B market cap, the meme origin, and Solana memecoin culture.",
    "Write about BONK on Solana: the community airdrop that revived Solana in December 2022, how it distributed tokens, and what happened next.",
    "Write about FLOKI: the Elon Musk dog name inspiration, Viking branding, FlokiFi DeFi suite, and global marketing campaigns.",
    "Write about the top 5 memecoins that made early holders millionaires: DOGE, SHIB, PEPE, WIF, BONK. What patterns did they share?",
    "Write a guide: How to spot the next 1000x memecoin before it explodes. Cover community signals, liquidity, tokenomics, and timing.",
    "Write about memecoin culture: why memes are the most powerful marketing in crypto, community as product, and viral mechanics.",
    "Write about the risks of memecoins: rug pulls, wash trading, and how to protect yourself while still participating in the upside.",
]

MARKET_TOPICS = [
    "Write a market analysis of the current memecoin sector. Discuss Bitcoin dominance, altcoin season signals, and which narratives are trending.",
    "Write about DeFi on Radix DLT: why Radix's asset-oriented model is superior to EVM, and how HYDRA fits into the ecosystem.",
    "Write about the psychology of memecoin investing: FOMO, diamond hands, paper hands, and how emotion drives 10x moves.",
]

if hour < 13:
    pool = HYDRA_TOPICS
elif hour < 20:
    pool = MEMECOIN_TOPICS
else:
    pool = MARKET_TOPICS + MEMECOIN_TOPICS

topic = random.choice(pool)
slug = f"post-{timestamp}"

if pool == HYDRA_TOPICS:
    category = random.choice(["Ecosystem", "Community", "News"])
elif "guide" in topic.lower() or "how to" in topic.lower() or "spot" in topic.lower():
    category = "Guides"
elif "analysis" in topic.lower() or "market" in topic.lower():
    category = "News"
elif "story" in topic.lower() or "deep dive" in topic.lower():
    category = "Announcements"
else:
    category = "Community"

tags_map = {
    "HYDRA": ["hydra", "radix", "defi"],
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
    "DeFi": ["defi", "radix", "blockchain"],
}
tags = ["memecoin", "crypto"]
for key, t in tags_map.items():
    if key.lower() in topic.lower():
        tags = t
        break

disclaimer = (
    "\n\n---\n\n"
    "**\u26a0\ufe0f Disclaimer:** This article is for educational and entertainment purposes only. "
    "Nothing here constitutes financial advice. Cryptocurrency investments are highly volatile and speculative. "
    "Always do your own research (DYOR) before making any investment decisions. "
    "Past performance is not indicative of future results."
)

system_msg = "You are the content writer for HYDRA Chronicles, a crypto and memecoin blog. Return ONLY a raw JSON object. No markdown fences. No extra text before or after the JSON."

user_msg = (
    f"Today is {today}. {topic}\n\n"
    "Write a compelling, well-structured article of at least 500 words. Use headers, bullet points, and engaging storytelling. "
    f"Always end the content field with this exact disclaimer: {disclaimer}\n\n"
    "Also return an 'imagePrompt' field: a short vivid English description (max 15 words) of a cinematic crypto illustration for this article. Example: 'golden dogecoin rocket launching to the moon, neon cyberpunk city background'\n\n"
    "Return ONLY this JSON:\n"
    "{\n"
    f'  "id": "{slug}",\n'
    '  "title": "<catchy engaging title>",\n'
    f'  "slug": "{slug}",\n'
    '  "excerpt": "<compelling summary under 200 chars>",\n'
    '  "content": "<full article in markdown, use \\n for newlines>",\n'
    f'  "category": "{category}",\n'
    '  "author": "HYDRA AI",\n'
    f'  "date": "{today}",\n'
    '  "readingTime": 5,\n'
    '  "featured": false,\n'
    '  "coverImage": "",\n'
    f'  "tags": {json.dumps(tags)},\n'
    '  "imagePrompt": "<short vivid image description>"\n'
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
        "temperature": 0.9,
        "max_tokens": 3000
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

# --- Generate cover image via Pollinations.ai ---
image_prompt = post.pop("imagePrompt", "")
if not image_prompt:
    # Fallback prompt based on title
    image_prompt = f"cinematic crypto illustration for article titled {post.get('title', 'crypto memecoin')}, dark neon background"

# Enhance prompt for better visual quality
full_image_prompt = f"{image_prompt}, digital art, cinematic lighting, dark background, vibrant colors, 4k, high quality"
encoded_prompt = urllib.parse.quote(full_image_prompt)
image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=630&nologo=true&seed={random.randint(1, 99999)}"

print(f"Image prompt: {full_image_prompt}")
print(f"Image URL: {image_url}")

# Test that image URL is reachable
try:
    img_req = urllib.request.Request(image_url, method="HEAD")
    urllib.request.urlopen(img_req, timeout=10)
    post["coverImage"] = image_url
    print("Cover image URL set successfully")
except Exception as e:
    print(f"Image check failed (using empty): {e}")
    post["coverImage"] = ""

# Save post
os.makedirs("src/data/posts", exist_ok=True)
out_path = f"src/data/posts/{slug}.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(post, f, indent=2, ensure_ascii=False)
print(f"Saved: {out_path}")

# Update public/posts-index.json
index_path = "public/posts-index.json"
existing = []
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        try:
            existing = json.load(f)
        except Exception:
            existing = []

existing = [p for p in existing if p.get("slug") != post["slug"]]
existing.insert(0, post)

os.makedirs("public", exist_ok=True)
with open(index_path, "w", encoding="utf-8") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)
print(f"Index updated: {len(existing)} posts")

print(f"SUCCESS:{out_path}")
print(f"SLUG:{slug}")
