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

IMAGE_PROMPTS = {
    "HYDRA": "six-headed blue hydra dragon in esports cartoon style, all six heads roaring with green eyes and sharp white fangs, metallic blue scales, black background with glowing blue neon ring border, circular badge composition, vibrant digital art, 4k",
    "HydraSwap": "six-headed blue hydra dragon mascot inside a glowing crypto DEX swap portal, neon blue energy arrows swirling, dark futuristic background, esports cartoon style, vibrant digital art, 4k",
    "Dogecoin": "the iconic shiba inu Doge meme dog wearing a gold astronaut helmet flying on a rocket to the moon, coins raining, neon night sky, vibrant digital art, 4k",
    "DOGE": "the iconic shiba inu Doge meme dog wearing a gold astronaut helmet flying on a rocket to the moon, coins raining, neon night sky, vibrant digital art, 4k",
    "Shiba": "a cute shiba inu dog wearing a red cape as crypto superhero, surrounded by burning SHIB coins, neon cityscape background, vibrant anime-style digital art, 4k",
    "SHIB": "a cute shiba inu dog wearing a red cape as crypto superhero, surrounded by burning SHIB coins, neon cityscape background, vibrant anime-style digital art, 4k",
    "Pepe": "the iconic Pepe the Frog wearing a suit sitting on a throne of gold crypto coins, dark moody lighting, meme culture aesthetic, vibrant digital art, 4k",
    "PEPE": "the iconic Pepe the Frog wearing a suit sitting on a throne of gold crypto coins, dark moody lighting, meme culture aesthetic, vibrant digital art, 4k",
    "WIF": "an adorable dog wearing a pink knitted hat in space surrounded by Solana purple neon lights, cute digital art, vibrant colors, cosmic background, 4k",
    "dogwifhat": "an adorable dog wearing a pink knitted hat in space surrounded by Solana purple neon lights, cute digital art, vibrant colors, cosmic background, 4k",
    "BONK": "a cartoon orange dog with a giant wooden bat smashing downward on crypto chart, Solana purple background, energetic explosive comic style digital art, 4k",
    "FLOKI": "a viking warrior shiba inu dog in Norse armor holding a crypto coin shield, dramatic northern lights background, epic cinematic digital art, 4k",
    "memecoin": "a rocket ship made of meme coin logos (doge, shib, pepe) blasting through a neon galaxy, epic cinematic digital art, vibrant colors, dark space background, 4k",
    "market": "a futuristic crypto trading floor with glowing green and red candles, holographic price charts, dark cyberpunk environment, cinematic digital art, 4k",
    "DeFi": "an intricate network of glowing blockchain nodes connecting across a dark digital universe, deep blue neon tones, cinematic art, 4k",
    "Radix": "the Radix DLT blockchain network visualized as glowing blue interconnected nodes in space, futuristic digital art, deep blue and white, cinematic, 4k",
    "guide": "a glowing treasure map overlaid on crypto charts and coin symbols, adventurer aesthetic, gold and dark blue tones, cinematic digital art, 4k",
    "risks": "a dramatic warning sign made of crypto coins on the edge of a cliff, dark stormy digital art, red warning glow, cinematic crypto illustration, 4k",
    "psychology": "a human brain made of glowing crypto candlesticks and coins, dark neon blue background, concept art, cinematic digital illustration, 4k",
    "millionaires": "five golden crypto coins (DOGE SHIB PEPE WIF BONK) on pedestals with trophy glow, dark dramatic background, cinematic digital art, 4k",
}

DEFAULT_IMAGE_PROMPT = "a dramatic crypto memecoin rocket launching through neon galaxy stars, vibrant digital art, dark space background, glowing coins, cinematic 4k illustration"

HYDRA_TOPICS = [
    ("HYDRA", "Write about the HYDRA ecosystem on Radix DLT. Cover one of: HydraSwap DEX, HydraBurn token burn mechanics, HydraBattleArena game, HYDRA staking rewards, or community governance. Be energetic and hype-driven."),
    ("HYDRA", "Write about why HYDRA on Radix DLT is positioned to be the next big memecoin. Cover Radix's unique tech advantages, HYDRA tokenomics, and community growth."),
    ("HYDRA", "Write a guide on how to buy and hold HYDRA token on Radix DLT. Include wallet setup, where to swap, and why the community is bullish."),
]

MEMECOIN_TOPICS = [
    ("Dogecoin", "Write the full story of Dogecoin (DOGE): from joke to $80B market cap. Cover the 2013 origin, Reddit community, Elon Musk tweets, and the 2021 explosion."),
    ("Shiba", "Write a deep dive into Shiba Inu (SHIB): the DOGE killer narrative, ShibArmy, Vitalik Buterin burn, Shibarium launch, and price history."),
    ("Pepe", "Write about Pepe (PEPE) coin: how a 4chan frog became a top-10 memecoin in 2023, the cultural roots, and the community explosion."),
    ("WIF", "Write about WIF (dogwifhat) on Solana: the hat-wearing dog that hit $4B market cap, the meme origin, and Solana memecoin culture."),
    ("BONK", "Write about BONK on Solana: the community airdrop that revived Solana in December 2022, how it distributed tokens, and what happened next."),
    ("FLOKI", "Write about FLOKI: the Elon Musk dog name inspiration, Viking branding, FlokiFi DeFi suite, and global marketing campaigns."),
    ("millionaires", "Write about the top 5 memecoins that made early holders millionaires: DOGE, SHIB, PEPE, WIF, BONK. What patterns did they share?"),
    ("guide", "Write a guide: How to spot the next 1000x memecoin before it explodes. Cover community signals, liquidity, tokenomics, and timing."),
    ("memecoin", "Write about memecoin culture: why memes are the most powerful marketing in crypto, community as product, and viral mechanics."),
    ("risks", "Write about the risks of memecoins: rug pulls, wash trading, and how to protect yourself while still participating in the upside."),
]

MARKET_TOPICS = [
    ("market", "Write a market analysis of the current memecoin sector. Discuss Bitcoin dominance, altcoin season signals, and which narratives are trending."),
    ("DeFi", "Write about DeFi on Radix DLT: why Radix's asset-oriented model is superior to EVM, and how HYDRA fits into the ecosystem."),
    ("psychology", "Write about the psychology of memecoin investing: FOMO, diamond hands, paper hands, and how emotion drives 10x moves."),
]

if hour < 13:
    pool = HYDRA_TOPICS
elif hour < 20:
    pool = MEMECOIN_TOPICS
else:
    pool = MARKET_TOPICS + MEMECOIN_TOPICS

image_key, topic = random.choice(pool)
slug = f"post-{timestamp}"
image_prompt = IMAGE_PROMPTS.get(image_key, DEFAULT_IMAGE_PROMPT)

# Category logic
if pool == HYDRA_TOPICS:
    category = random.choice(["Ecosystem", "Community", "News"])
elif image_key in ["Dogecoin", "DOGE", "Shiba", "SHIB", "Pepe", "PEPE", "WIF", "dogwifhat", "BONK", "FLOKI", "memecoin", "millionaires"]:
    category = "Memecoin"
elif image_key == "guide":
    category = "Guides"
elif image_key in ["market", "DeFi", "Radix"]:
    category = "News"
elif image_key == "psychology":
    category = "Community"
else:
    category = "Memecoin"

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

system_msg = "You are the content writer for HYDRA Chronicles, a crypto and memecoin blog. Return ONLY a raw JSON object. No markdown fences. No extra text before or after the JSON."

user_msg = (
    f"Today is {today}. {topic}\n\n"
    "Write a compelling, well-structured article of AT LEAST 1500 words. "
    "Use multiple headers (##), bullet points, numbered lists, bold highlights, and engaging storytelling. "
    "Include historical context, data points, community stories, and analysis. Make it long, detailed and informative. "
    f"Always end the content field with this exact disclaimer: {disclaimer}\n\n"
    "Return ONLY this JSON:\n"
    "{\n"
    f'  "id": "{slug}",\n'
    '  "title": "<catchy engaging title>",\n'
    f'  "slug": "{slug}",\n'
    '  "excerpt": "<compelling summary under 200 chars>",\n'
    '  "content": "<full article in markdown, use \\n for newlines, minimum 1500 words>",\n'
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
        "temperature": 0.9,
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

# Dynamic reading time: ~200 words per minute
word_count = len(post.get("content", "").split())
post["readingTime"] = max(1, round(word_count / 200))

# Force correct author and category
post["author"] = "HYDRA"
post["category"] = category

print(f"Image key: {image_key}")
print(f"Image prompt: {image_prompt}")

encoded_prompt = urllib.parse.quote(image_prompt)
image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=630&nologo=true&seed={random.randint(1, 99999)}"
post["coverImage"] = image_url
print(f"Cover image URL: {image_url}")

os.makedirs("src/data/posts", exist_ok=True)
out_path = f"src/data/posts/{slug}.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(post, f, indent=2, ensure_ascii=False)
print(f"Saved: {out_path}")

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
