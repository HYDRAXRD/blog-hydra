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

FACTS_PATH = ".github/data/hydra-facts.md"
try:
    with open(FACTS_PATH, "r", encoding="utf-8") as f:
        HYDRA_FACTS = f.read()
except FileNotFoundError:
    HYDRA_FACTS = ""
    print("WARNING: hydra-facts.md not found")

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

IMAGE_PROMPTS = {
    "HYDRA": "minimalist dark crypto blog banner, six-headed dragon silhouette in deep blue neon outline, clean black background, no text, professional web3 aesthetic",
    "HydraSwap": "minimalist dark crypto DEX banner, blue energy swap arrows, clean black background, no text, professional web3 aesthetic",
    "Dogecoin": "minimalist dark crypto banner, golden shiba inu coin on dark background, clean professional web3 aesthetic, no text",
    "DOGE": "minimalist dark crypto banner, golden shiba inu coin on dark background, clean professional web3 aesthetic, no text",
    "Shiba": "minimalist dark crypto banner, red and orange shiba inu dog silhouette, dark background, professional web3 aesthetic, no text",
    "SHIB": "minimalist dark crypto banner, red and orange shiba inu dog silhouette, dark background, professional web3 aesthetic, no text",
    "Pepe": "minimalist dark crypto banner, green frog silhouette in gold crown, dark moody background, professional web3 aesthetic, no text",
    "PEPE": "minimalist dark crypto banner, green frog silhouette in gold crown, dark moody background, professional web3 aesthetic, no text",
    "WIF": "minimalist dark crypto banner, small dog silhouette wearing a hat, purple solana-toned background, professional web3 aesthetic, no text",
    "dogwifhat": "minimalist dark crypto banner, small dog silhouette wearing a hat, purple solana-toned background, professional web3 aesthetic, no text",
    "BONK": "minimalist dark crypto banner, orange dog with bat icon, solana purple tones, dark background, professional web3 aesthetic, no text",
    "FLOKI": "minimalist dark crypto banner, viking helmet and shield silhouette, dark dramatic background, professional web3 aesthetic, no text",
    "memecoin": "minimalist dark crypto banner, rocket silhouette with coin trail, dark cosmic background, professional web3 aesthetic, no text",
    "market": "minimalist dark crypto banner, glowing candlestick chart lines, dark background, professional web3 aesthetic, no text",
    "DeFi": "minimalist dark crypto banner, interconnected blockchain nodes in blue, dark background, professional web3 aesthetic, no text",
    "Radix": "minimalist dark crypto banner, blue geometric network nodes, dark background, professional web3 aesthetic, no text",
    "guide": "minimalist dark crypto banner, compass and map silhouette on dark background, gold accent, professional web3 aesthetic, no text",
    "risks": "minimalist dark crypto banner, warning triangle with lightning bolt, dark red tones, professional web3 aesthetic, no text",
    "psychology": "minimalist dark crypto banner, brain silhouette with circuit lines, dark neon blue, professional web3 aesthetic, no text",
    "millionaires": "minimalist dark crypto banner, five gold coins on pedestals, dark dramatic background, professional web3 aesthetic, no text",
}
DEFAULT_IMAGE_PROMPT = "minimalist dark crypto blog banner, rocket silhouette and coin symbols, dark space background, professional web3 aesthetic, no text"

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
slug = f"post-{timestamp}"
image_prompt = IMAGE_PROMPTS.get(image_key, DEFAULT_IMAGE_PROMPT)

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
        market_context = f"\nReal Market Data (CoinGecko, fetched now):\nCurrent price: ${cg_data.get('price_usd', 'N/A')}\n24h change: {cg_data.get('change_24h', 'N/A')}%\nMarket cap: ${cg_data.get('market_cap_usd', 'N/A')} USD\n"
        print(f"CoinGecko data: {cg_data}")

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
    "Only use facts provided or widely established public knowledge. "
    f"End the content field with this exact disclaimer: {disclaimer}\n\n"
    "Return ONLY this JSON:\n"
    "{\n"
    f'  "id": "{slug}",\n'
    '  "title": "<catchy engaging title>",\n'
    f'  "slug": "{slug}",\n'
    '  "excerpt": "<compelling summary under 200 chars>",\n'
    '  "content": "<full article in markdown, use \\n for newlines, minimum 1200 words, NO bullet points, NO dashes, NO ### headers, ALL links masked>",\n'
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

word_count = len(post.get("content", "").split())
post["readingTime"] = max(1, round(word_count / 200))
post["author"] = "HYDRA"
post["category"] = category

encoded_prompt = urllib.parse.quote(image_prompt)
image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=630&nologo=true&seed={random.randint(1, 99999)}"
post["coverImage"] = image_url
print(f"Image key: {image_key}")
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
