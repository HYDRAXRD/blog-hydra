import os
import json
import urllib.request
import urllib.error
from datetime import date
import sys

today = date.today().isoformat()
day = date.today().weekday()  # 0=Monday, 6=Sunday
api_key = os.environ["OPENROUTER_API_KEY"]

topics = [
    {
        "slug": f"hydra-ecosystem-{today}",
        "tags": ["hydra", "radix", "ecosystem"],
        "topic": "Write about the HYDRA ecosystem on Radix DLT: token updates, HydraSwap, HydraBurn, HydraBattleArena, or community news. Be hype-driven and energetic."
    },
    {
        "slug": f"dogecoin-story-{today}",
        "tags": ["dogecoin", "doge", "memecoin", "history"],
        "topic": "Write an in-depth story about how Dogecoin (DOGE) exploded in popularity: origin, community, Elon Musk effect, key price moments. Educational and engaging tone."
    },
    {
        "slug": f"shiba-inu-deep-dive-{today}",
        "tags": ["shiba", "shib", "memecoin", "history"],
        "topic": "Write a deep dive into Shiba Inu (SHIB): how it launched, the ShibArmy, burn mechanism, and why it became a top memecoin. Educational tone."
    },
    {
        "slug": f"pepe-coin-story-{today}",
        "tags": ["pepe", "memecoin", "history", "culture"],
        "topic": "Write about Pepe (PEPE) coin: how a frog meme became a billion-dollar token in weeks, community culture, and what made it explode. Fun and educational tone."
    },
    {
        "slug": f"what-makes-memecoins-explode-{today}",
        "tags": ["memecoin", "guide", "doge", "shib", "pepe"],
        "topic": "Write a guide: What makes a memecoin explode? Analyze patterns from DOGE, SHIB, PEPE, WIF, BONK. What do they have in common? Community, timing, narrative."
    },
    {
        "slug": f"solana-memecoins-{today}",
        "tags": ["wif", "bonk", "solana", "memecoin"],
        "topic": "Write about Solana memecoins WIF (dogwifhat) and BONK: how they launched, viral growth, community culture. Compare with Ethereum memecoins."
    },
    {
        "slug": f"why-memecoins-matter-{today}",
        "tags": ["memecoin", "hydra", "community", "opinion"],
        "topic": "Write an opinion piece: Why memecoins matter in crypto. Community, culture, financial inclusion, and fun. Reference HYDRA as an example of a community-driven ecosystem."
    },
]

t = topics[day]
slug = t["slug"]
tags = t["tags"]
topic = t["topic"]

disclaimer = (
    "\n\n---\n\n"
    "**Disclaimer:** This article is for educational and entertainment purposes only. "
    "Nothing here constitutes financial advice. Crypto investments are highly volatile. "
    "Always do your own research (DYOR) before making any investment decisions."
)

system_msg = "You are the content writer for HYDRA Chronicles, a crypto blog. Return ONLY a raw JSON object with no markdown code fences and no extra text before or after."

user_msg = (
    f"Today is {today}. {topic}\n\n"
    f"Write a well-structured article of at least 400 words. "
    f"End the content field with this disclaimer: {disclaimer}\n\n"
    f"Return ONLY this JSON with no extra text:\n"
    "{\n"
    f'  "id": "{slug}",\n'
    '  "title": "<catchy title>",\n'
    f'  "slug": "{slug}",\n'
    '  "excerpt": "<max 200 chars summary>",\n'
    '  "content": "<full article in markdown, use \\n for newlines>",\n'
    '  "category": "<one of: News, Ecosystem, Community, Game Updates, Guides, Announcements>",\n'
    '  "author": "HYDRA AI",\n'
    f'  "date": "{today}",\n'
    '  "readingTime": 5,\n'
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

for model in MODELS:
    print(f"Trying model: {model}")
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.85,
        "max_tokens": 2500
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

        print(f"Full response: {json.dumps(data)[:300]}")

        # Extract content safely - handle null content (reasoning models)
        msg = data.get("choices", [{}])[0].get("message", {})
        content = msg.get("content") or msg.get("reasoning") or ""

        if not content or not content.strip():
            print(f"Model {model} returned empty content, trying next...")
            continue

        response_data = data
        content = content.strip()
        print(f"Success with model: {model} ({len(content)} chars)")
        break

    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Model {model} failed: {e.code} - {body}")
        continue

if not response_data or not content:
    print("All models failed or returned empty. Exiting.")
    sys.exit(1)

# Strip markdown fences if model wraps response
if content.startswith("```"):
    lines = content.split("\n")
    content = "\n".join(lines[1:-1]).strip()

# Find JSON block if there's extra text around it
if not content.startswith("{"):
    start = content.find("{")
    end = content.rfind("}") + 1
    if start != -1 and end > start:
        content = content[start:end]

# Validate JSON
try:
    post = json.loads(content)
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    print(f"Raw content: {content[:500]}")
    sys.exit(1)

os.makedirs("src/data/posts", exist_ok=True)
out_path = f"src/data/posts/{slug}.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(post, f, indent=2, ensure_ascii=False)

print(f"SUCCESS:{out_path}")
print(f"SLUG:{slug}")
