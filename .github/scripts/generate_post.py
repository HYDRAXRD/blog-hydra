import os
import json
import urllib.request
from datetime import date

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

payload = json.dumps({
    "model": "google/gemini-2.0-flash-exp:free",
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

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())

content = data["choices"][0]["message"]["content"].strip()

# Strip markdown fences if model wraps response
if content.startswith("```"):
    lines = content.split("\n")
    content = "\n".join(lines[1:-1]).strip()

# Validate JSON
post = json.loads(content)

os.makedirs("src/data/posts", exist_ok=True)
out_path = f"src/data/posts/{slug}.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(post, f, indent=2, ensure_ascii=False)

print(f"SUCCESS:{out_path}")
print(f"SLUG:{slug}")
