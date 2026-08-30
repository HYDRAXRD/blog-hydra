import os
import json
import urllib.request
import urllib.error
import urllib.parse
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import sys
import random
import time

now = datetime.now(timezone.utc)
today = now.strftime("%Y-%m-%d")
# Full ISO-8601 datetime used as the post `date` field so that two posts
# published on the same calendar day sort correctly (newest commit = latest
# timestamp = appears first in sortedPosts).
today_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
hour = now.hour
api_key = os.environ["OPENROUTER_API_KEY"]
unsplash_key = os.environ.get("UNSPLASH_API_KEY", "")
cmc_key = os.environ.get("API_KEY_CMC", "")
cg_key = os.environ.get("API_KEY_COINGECKO", "")
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
        # sitemap lastmod requires YYYY-MM-DD; strip time part if present
        lastmod = date[:10] if date else today
        if not slug:
            continue
        lines += [
            '',
            '  <url>',
            f'    <loc>{BASE_URL}/blog/post/{slug}</loc>',
            f'    <lastmod>{lastmod}</lastmod>',
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


def format_large_number(n):
    """Format large numbers as $1.23B, $456.7M, etc."""
    if n is None or n == "N/A":
        return "N/A"
    try:
        n = float(n)
    except (ValueError, TypeError):
        return str(n)
    if n >= 1_000_000_000:
        return f"${n / 1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"${n / 1_000_000:.2f}M"
    return f"${n:,.0f}"


# ---------------------------------------------------------------------------
# Google Trends via pytrends — what people are actually searching right now
# ---------------------------------------------------------------------------

def fetch_google_trends_crypto() -> list:
    """
    Install pytrends at runtime (if not present) and return the top crypto
    search keywords trending on Google in the last 24 hours.
    Returns a list of keyword strings, empty list on any failure.
    """
    try:
        import subprocess
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "pytrends"],
            check=True, capture_output=True
        )
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-US", tz=0, timeout=(10, 30), retries=2, backoff_factor=0.5)

        # Search for crypto-related keywords to get related rising queries
        kw_list = ["cryptocurrency", "memecoin", "bitcoin", "crypto"]
        pytrends.build_payload(kw_list, cat=0, timeframe="now 1-d", geo="", gprop="")
        related = pytrends.related_queries()

        rising_terms = []
        for kw in kw_list:
            df = related.get(kw, {}).get("rising")
            if df is not None and not df.empty:
                for _, row in df.head(5).iterrows():
                    term = str(row.get("query", "")).strip()
                    if term and len(term) > 2:
                        rising_terms.append(term)

        # Also grab real-time trending searches (US)
        try:
            trending_rt = pytrends.realtime_trending_searches(pn="US")
            if trending_rt is not None and not trending_rt.empty:
                for _, row in trending_rt.head(10).iterrows():
                    title = str(row.get("title", "")).strip()
                    entity_names = str(row.get("entityNames", "")).strip()
                    for term in [title, entity_names]:
                        if any(kw in term.lower() for kw in ["crypto", "bitcoin", "coin", "token", "defi", "nft", "blockchain", "eth", "btc", "solana"]):
                            rising_terms.append(term)
        except Exception as e:
            print(f"Realtime trending search failed (non-critical): {e}")

        # Deduplicate, normalise
        seen = set()
        result = []
        for t in rising_terms:
            key = t.lower()
            if key not in seen:
                seen.add(key)
                result.append(t)

        print(f"Google Trends: {len(result)} rising crypto terms found")
        return result[:15]

    except Exception as e:
        print(f"Google Trends fetch failed (non-critical): {e}")
        return []


# ---------------------------------------------------------------------------
# RSS news feed — CoinTelegraph + CryptoSlate headlines (no API key needed)
# ---------------------------------------------------------------------------

def fetch_rss_headlines() -> list:
    """
    Pull the latest headlines from CoinTelegraph and CryptoSlate RSS feeds.
    Returns a list of title strings, empty list on failure.
    """
    feeds = [
        "https://cointelegraph.com/rss",
        "https://cryptoslate.com/feed/",
        "https://decrypt.co/feed",
    ]
    headlines = []
    for feed_url in feeds:
        try:
            req = urllib.request.Request(
                feed_url,
                headers={"User-Agent": "HYDRABlog/1.0 (RSS reader)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read()
            root = ET.fromstring(raw)
            # RSS 2.0: channel > item > title
            ns = ""
            for item in root.findall(f".//{ns}item")[:8]:
                title_el = item.find(f"{ns}title")
                if title_el is not None and title_el.text:
                    headlines.append(title_el.text.strip())
        except Exception as e:
            print(f"RSS fetch failed for {feed_url} (non-critical): {e}")
            continue
    print(f"RSS headlines collected: {len(headlines)}")
    return headlines[:20]


# ---------------------------------------------------------------------------
# Combine all trend signals into a single context block for the prompt
# ---------------------------------------------------------------------------

def build_trend_signals() -> tuple:
    """
    Fetch Google Trends rising queries + RSS headlines.
    Returns (formatted_block: str, google_terms: list, rss_headlines: list).
    """
    google_terms = fetch_google_trends_crypto()
    rss_headlines = fetch_rss_headlines()

    lines = []
    if google_terms:
        lines.append("\n--- GOOGLE TRENDS: Rising crypto search terms right now ---")
        for t in google_terms:
            lines.append(f"  • {t}")
        lines.append("(These are terms people are actively searching on Google in the last 24h)")

    if rss_headlines:
        lines.append("\n--- LATEST NEWS HEADLINES (CoinTelegraph / CryptoSlate / Decrypt) ---")
        for h in rss_headlines:
            lines.append(f"  • {h}")
        lines.append("(These headlines reflect what the crypto world is talking about right now)")

    formatted = "\n".join(lines) if lines else ""
    return formatted, google_terms, rss_headlines


# ---------------------------------------------------------------------------
# Topic selection driven by live trend signals
# ---------------------------------------------------------------------------

# Keyword map: each topic pool entry is associated with keywords that, if
# found in Google Trends terms or RSS headlines, increase its score.
TOPIC_KEYWORDS = {
    "HYDRA":        ["hydra", "hydraswap", "radix", "xrd"],
    "HydraSwap":    ["hydraswap", "hydra", "dex", "radix"],
    "Dogecoin":     ["dogecoin", "doge"],
    "Shiba":        ["shiba", "shib"],
    "Pepe":         ["pepe", "frog"],
    "WIF":          ["wif", "dogwifhat", "dog wif hat"],
    "BONK":         ["bonk"],
    "FLOKI":        ["floki"],
    "market":       ["bitcoin", "btc", "market cap", "crypto market", "bull", "bear"],
    "guide":        ["how to buy", "guide", "tutorial", "beginners", "invest"],
    "risks":        ["rug pull", "scam", "hack", "risk", "warning", "crash"],
    "psychology":   ["fomo", "fear", "greed", "psychology", "emotion", "panic"],
    "millionaires": ["millionaire", "rich", "gains", "10000x", "100x", "early holder"],
    "memecoin":     ["memecoin", "meme coin", "meme token", "viral coin"],
    "DeFi":         ["defi", "decentralized finance", "liquidity", "yield", "amm"],
    "trending":     ["trending", "top gainer", "viral", "pumping", "hot coin"],
    "bitcoin":      ["bitcoin", "btc", "halving", "satoshi", "sats"],
    "culture":      ["meme", "culture", "internet", "community", "viral"],
    "history":      ["history", "2021", "bull run", "crash", "2017", "all time high"],
    "Radix":        ["radix", "xrd", "cerberus", "babylon"],
    "psychology":   ["psychology", "fomo", "greed", "fear", "emotional"],
}


def score_topic(image_key: str, google_terms: list, rss_headlines: list) -> int:
    """
    Score a topic based on how many of its keywords appear in the live signals.
    Google Trends match = 2 points (people are actively searching).
    RSS headline match  = 1 point  (media is covering it).
    """
    keywords = TOPIC_KEYWORDS.get(image_key, [image_key.lower()])
    score = 0
    all_trends_text = " ".join(google_terms).lower()
    all_rss_text = " ".join(rss_headlines).lower()
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in all_trends_text:
            score += 2
        if kw_lower in all_rss_text:
            score += 1
    return score


def pick_topic_from_signals(pool: list, google_terms: list, rss_headlines: list) -> tuple:
    """
    Score every entry in the pool against live trend signals and return
    the highest-scoring (image_key, topic_prompt) pair.
    Falls back to random.choice if all scores are zero (no signals).
    Ties are broken randomly to ensure variety.
    """
    if not google_terms and not rss_headlines:
        print("No live signals available — falling back to random topic selection.")
        return random.choice(pool)

    scored = []
    for entry in pool:
        img_key = entry[0]
        s = score_topic(img_key, google_terms, rss_headlines)
        scored.append((s, entry))
        print(f"  Topic score [{img_key}]: {s}")

    max_score = max(s for s, _ in scored)

    if max_score == 0:
        print("All topic scores are 0 — falling back to random topic selection.")
        return random.choice(pool)

    # Collect all entries tied at the top score and pick randomly among them
    top_entries = [entry for s, entry in scored if s == max_score]
    chosen = random.choice(top_entries)
    print(f"Trend-driven topic selected: [{chosen[0]}] (score={max_score}, {len(top_entries)} tied at top)")
    return chosen


# ---------------------------------------------------------------------------
# CoinGecko (Pro API if key available, else free tier)
# ---------------------------------------------------------------------------

def _cg_headers():
    h = {"User-Agent": "HYDRABlog/1.0"}
    if cg_key:
        h["x-cg-pro-api-key"] = cg_key
    return h


def _cg_base():
    return "https://pro-api.coingecko.com/api/v3" if cg_key else "https://api.coingecko.com/api/v3"


def fetch_coingecko_coin(coin_id="bitcoin"):
    """Fetch price, 24h change, market cap, volume and ATH for a single coin."""
    try:
        url = (
            f"{_cg_base()}/coins/{coin_id}"
            "?localization=false&tickers=false&market_data=true"
            "&community_data=false&developer_data=false"
        )
        req = urllib.request.Request(url, headers=_cg_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        md = data.get("market_data", {})
        return {
            "price_usd":      md.get("current_price", {}).get("usd", "N/A"),
            "change_24h":     md.get("price_change_percentage_24h", "N/A"),
            "change_7d":      md.get("price_change_percentage_7d", "N/A"),
            "market_cap_usd": md.get("market_cap", {}).get("usd", "N/A"),
            "volume_24h":     md.get("total_volume", {}).get("usd", "N/A"),
            "ath":            md.get("ath", {}).get("usd", "N/A"),
            "ath_change_pct": md.get("ath_change_percentage", {}).get("usd", "N/A"),
        }
    except Exception as e:
        print(f"CoinGecko fetch failed for {coin_id}: {e}")
        return {}


def fetch_cg_global():
    """Fetch global crypto market stats: total market cap, BTC dominance, fear index."""
    try:
        url = f"{_cg_base()}/global"
        req = urllib.request.Request(url, headers=_cg_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read()).get("data", {})
        return {
            "total_market_cap": data.get("total_market_cap", {}).get("usd", "N/A"),
            "market_cap_change_24h": data.get("market_cap_change_percentage_24h_usd", "N/A"),
            "btc_dominance": data.get("market_cap_percentage", {}).get("btc", "N/A"),
            "eth_dominance": data.get("market_cap_percentage", {}).get("eth", "N/A"),
            "active_coins": data.get("active_cryptocurrencies", "N/A"),
        }
    except Exception as e:
        print(f"CoinGecko global fetch failed: {e}")
        return {}


def fetch_cg_trending():
    """Fetch top 7 trending coins from CoinGecko."""
    try:
        url = f"{_cg_base()}/search/trending"
        req = urllib.request.Request(url, headers=_cg_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        coins = data.get("coins", [])[:7]
        return [
            {
                "name": c["item"]["name"],
                "symbol": c["item"]["symbol"],
                "market_cap_rank": c["item"].get("market_cap_rank", "N/A"),
                "price_btc": c["item"].get("price_btc", "N/A"),
                "data": c["item"].get("data", {}),
            }
            for c in coins
        ]
    except Exception as e:
        print(f"CoinGecko trending fetch failed: {e}")
        return []


def fetch_cg_top_memecoins():
    """Fetch top memecoins by market cap from CoinGecko."""
    try:
        params = urllib.parse.urlencode({
            "vs_currency": "usd",
            "category": "meme-token",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h,7d",
        })
        url = f"{_cg_base()}/coins/markets?{params}"
        req = urllib.request.Request(url, headers=_cg_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            coins = json.loads(resp.read())
        result = []
        for c in coins:
            result.append({
                "name": c.get("name"),
                "symbol": c.get("symbol", "").upper(),
                "price": c.get("current_price", "N/A"),
                "change_24h": c.get("price_change_percentage_24h", "N/A"),
                "change_7d": c.get("price_change_percentage_7d_in_currency", "N/A"),
                "market_cap": c.get("market_cap", "N/A"),
                "volume_24h": c.get("total_volume", "N/A"),
            })
        return result
    except Exception as e:
        print(f"CoinGecko top memecoins fetch failed: {e}")
        return []


# ---------------------------------------------------------------------------
# CoinMarketCap API
# ---------------------------------------------------------------------------

def _cmc_headers():
    return {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": cmc_key,
        "User-Agent": "HYDRABlog/1.0",
    }


def fetch_cmc_coin(symbol: str):
    """Fetch latest quote for a coin symbol from CMC."""
    if not cmc_key:
        print("WARNING: API_KEY_CMC not set, skipping CMC fetch")
        return {}
    try:
        params = urllib.parse.urlencode({"symbol": symbol.upper(), "convert": "USD"})
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?{params}"
        req = urllib.request.Request(url, headers=_cmc_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        coin_data = data.get("data", {}).get(symbol.upper(), {})
        quote = coin_data.get("quote", {}).get("USD", {})
        return {
            "price_usd":       quote.get("price", "N/A"),
            "change_1h":       quote.get("percent_change_1h", "N/A"),
            "change_24h":      quote.get("percent_change_24h", "N/A"),
            "change_7d":       quote.get("percent_change_7d", "N/A"),
            "change_30d":      quote.get("percent_change_30d", "N/A"),
            "market_cap_usd":  quote.get("market_cap", "N/A"),
            "volume_24h":      quote.get("volume_24h", "N/A"),
            "volume_change_24h": quote.get("volume_change_24h", "N/A"),
            "circulating_supply": coin_data.get("circulating_supply", "N/A"),
            "max_supply":      coin_data.get("max_supply", "N/A"),
            "cmc_rank":        coin_data.get("cmc_rank", "N/A"),
        }
    except Exception as e:
        print(f"CMC fetch failed for {symbol}: {e}")
        return {}


def fetch_cmc_global():
    """Fetch global market metrics from CMC."""
    if not cmc_key:
        return {}
    try:
        url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        req = urllib.request.Request(url, headers=_cmc_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read()).get("data", {})
        quote = data.get("quote", {}).get("USD", {})
        return {
            "total_market_cap":     quote.get("total_market_cap", "N/A"),
            "total_volume_24h":     quote.get("total_volume_24h", "N/A"),
            "market_cap_change_24h": quote.get("total_market_cap_yesterday_percentage_change", "N/A"),
            "btc_dominance":        data.get("btc_dominance", "N/A"),
            "eth_dominance":        data.get("eth_dominance", "N/A"),
            "defi_volume_24h":      quote.get("defi_volume_24h", "N/A"),
            "stablecoin_volume_24h": quote.get("stablecoin_volume_24h", "N/A"),
            "active_coins":         data.get("active_cryptocurrencies", "N/A"),
        }
    except Exception as e:
        print(f"CMC global fetch failed: {e}")
        return {}


def fetch_cmc_trending():
    """Fetch top gainers from CMC (sorted by 24h change)."""
    if not cmc_key:
        return []
    try:
        params = urllib.parse.urlencode({
            "limit": 10,
            "convert": "USD",
            "sort": "percent_change_24h",
            "sort_dir": "desc",
            "cryptocurrency_type": "all",
        })
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?{params}"
        req = urllib.request.Request(url, headers=_cmc_headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        coins = data.get("data", [])[:5]
        result = []
        for c in coins:
            q = c.get("quote", {}).get("USD", {})
            result.append({
                "name":       c.get("name"),
                "symbol":     c.get("symbol"),
                "price":      q.get("price", "N/A"),
                "change_24h": q.get("percent_change_24h", "N/A"),
                "market_cap": q.get("market_cap", "N/A"),
                "cmc_rank":   c.get("cmc_rank", "N/A"),
            })
        return result
    except Exception as e:
        print(f"CMC trending fetch failed: {e}")
        return []


# ---------------------------------------------------------------------------
# Unified market context builder
# ---------------------------------------------------------------------------

def build_market_context(image_key: str) -> str:
    """
    Build a rich market context block by combining CMC + CoinGecko data.
    Priority: CMC (more complete) supplemented by CoinGecko (trending, categories).
    """
    lines = []

    # --- Coin-specific data ---
    cg_coin_map = {
        "Dogecoin": ("dogecoin",  "DOGE"),
        "DOGE":     ("dogecoin",  "DOGE"),
        "Shiba":    ("shiba-inu", "SHIB"),
        "SHIB":     ("shiba-inu", "SHIB"),
        "Pepe":     ("pepe",      "PEPE"),
        "PEPE":     ("pepe",      "PEPE"),
        "WIF":      ("dogwifcoin","WIF"),
        "dogwifhat":("dogwifcoin","WIF"),
        "BONK":     ("bonk",      "BONK"),
        "FLOKI":    ("floki",     "FLOKI"),
        "market":   ("bitcoin",   "BTC"),
    }

    if image_key in cg_coin_map:
        cg_id, cmc_sym = cg_coin_map[image_key]

        cmc_data = fetch_cmc_coin(cmc_sym)
        cg_data  = fetch_coingecko_coin(cg_id)

        price      = cmc_data.get("price_usd")    or cg_data.get("price_usd", "N/A")
        change_24h = cmc_data.get("change_24h")   or cg_data.get("change_24h", "N/A")
        change_7d  = cmc_data.get("change_7d")    or cg_data.get("change_7d", "N/A")
        change_30d = cmc_data.get("change_30d",   "N/A")
        change_1h  = cmc_data.get("change_1h",    "N/A")
        mktcap     = cmc_data.get("market_cap_usd") or cg_data.get("market_cap_usd", "N/A")
        volume     = cmc_data.get("volume_24h")   or cg_data.get("volume_24h", "N/A")
        circ_sup   = cmc_data.get("circulating_supply", "N/A")
        max_sup    = cmc_data.get("max_supply",   "N/A")
        cmc_rank   = cmc_data.get("cmc_rank",     "N/A")
        ath        = cg_data.get("ath",           "N/A")
        ath_chg    = cg_data.get("ath_change_pct","N/A")

        def pct(v):
            try: return f"{float(v):.2f}%"
            except: return str(v)

        lines.append(f"\nReal-Time Market Data for {cmc_sym} (CMC + CoinGecko, fetched now):")
        lines.append(f"Price: ${format_price(price)}")
        lines.append(f"1h change: {pct(change_1h)}")
        lines.append(f"24h change: {pct(change_24h)}")
        lines.append(f"7d change: {pct(change_7d)}")
        lines.append(f"30d change: {pct(change_30d)}")
        lines.append(f"Market cap: {format_large_number(mktcap)}")
        lines.append(f"24h volume: {format_large_number(volume)}")
        if circ_sup != "N/A":
            lines.append(f"Circulating supply: {float(circ_sup):,.0f} {cmc_sym}")
        if max_sup and max_sup != "N/A":
            lines.append(f"Max supply: {float(max_sup):,.0f} {cmc_sym}")
        if cmc_rank != "N/A":
            lines.append(f"CMC Rank: #{cmc_rank}")
        if ath != "N/A":
            lines.append(f"All-time high: ${format_price(ath)} ({pct(ath_chg)} from ATH)")

        print(f"Market data merged: price=${format_price(price)}, 24h={pct(change_24h)}")

    # --- Global market overview (always included) ---
    cmc_global = fetch_cmc_global()
    cg_global  = fetch_cg_global()

    total_mc   = cmc_global.get("total_market_cap")   or cg_global.get("total_market_cap", "N/A")
    mc_chg     = cmc_global.get("market_cap_change_24h") or cg_global.get("market_cap_change_24h", "N/A")
    btc_dom    = cmc_global.get("btc_dominance")      or cg_global.get("btc_dominance", "N/A")
    eth_dom    = cmc_global.get("eth_dominance")      or cg_global.get("eth_dominance", "N/A")
    vol_24h    = cmc_global.get("total_volume_24h",   "N/A")
    defi_vol   = cmc_global.get("defi_volume_24h",    "N/A")
    active     = cmc_global.get("active_coins")       or cg_global.get("active_coins", "N/A")

    def pct(v):
        try: return f"{float(v):.2f}%"
        except: return str(v)

    lines.append("\nGlobal Crypto Market (CMC + CoinGecko):")
    lines.append(f"Total market cap: {format_large_number(total_mc)} ({pct(mc_chg)} 24h)")
    lines.append(f"24h total volume: {format_large_number(vol_24h)}")
    if defi_vol != "N/A":
        lines.append(f"DeFi 24h volume: {format_large_number(defi_vol)}")
    lines.append(f"BTC dominance: {pct(btc_dom)}")
    lines.append(f"ETH dominance: {pct(eth_dom)}")
    lines.append(f"Active cryptocurrencies: {active}")

    # --- Trending coins (CoinGecko trending + CMC top gainers) ---
    cg_trending = fetch_cg_trending()
    if cg_trending:
        lines.append("\nTrending right now (CoinGecko):")
        for t in cg_trending:
            price_usd = t.get("data", {}).get("price", "")
            price_str = f" | ${format_price(price_usd)}" if price_usd else ""
            lines.append(f"  {t['name']} ({t['symbol']}) - Rank #{t['market_cap_rank']}{price_str}")

    cmc_gainers = fetch_cmc_trending()
    if cmc_gainers:
        lines.append("\nTop 24h gainers right now (CMC):")
        for g in cmc_gainers:
            try:
                chg = f"{float(g['change_24h']):.2f}%"
            except:
                chg = str(g["change_24h"])
            lines.append(f"  {g['name']} ({g['symbol']}) +{chg} | Rank #{g['cmc_rank']} | ${format_price(g['price'])}")

    # --- Top memecoins snapshot (always included for editorial context) ---
    top_memes = fetch_cg_top_memecoins()
    if top_memes:
        lines.append("\nTop memecoins by market cap right now (CoinGecko):")
        for m in top_memes:
            try:
                chg = f"{float(m['change_24h']):.2f}%"
            except:
                chg = str(m["change_24h"])
            lines.append(
                f"  {m['name']} ({m['symbol']}) "
                f"${format_price(m['price'])} | {chg} 24h | "
                f"MCap {format_large_number(m['market_cap'])}"
            )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Unsplash image fetch — with used-image deduplication
# ---------------------------------------------------------------------------

def _load_used_image_ids() -> set:
    """Read posts-index.json and extract all Unsplash photo IDs already in use."""
    index_path = "public/posts-index.json"
    if not os.path.exists(index_path):
        return set()
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            posts = json.load(f)
        used = set()
        for p in posts:
            url = p.get("coverImage", "")
            m = re.search(r"photo-([A-Za-z0-9_-]+)\?", url)
            if m:
                used.add(m.group(1))
                continue
            m = re.search(r"ixid=M3[^&]+", url)
            if m:
                used.add(m.group(0))
        return used
    except Exception as e:
        print(f"Warning: could not load used image IDs: {e}")
        return set()


def fetch_unsplash_image(query: str, width: int = 1200, height: int = 630) -> str:
    if not unsplash_key:
        print("WARNING: UNSPLASH_API_KEY not set, using fallback image")
        return _unsplash_fallback(query)

    QUERY_MAP = {
        "HYDRA": [
            "blockchain crypto dragon dark",
            "hydra serpent mythology dark fantasy",
            "crypto defi network futuristic neon",
            "dragon mythology digital art dark",
            "blockchain decentralized technology glowing",
            "radix network nodes blockchain abstract",
        ],
        "HydraSwap": [
            "decentralized exchange cryptocurrency dark",
            "defi swap liquidity crypto abstract",
            "crypto trading interface futuristic",
        ],
        "Dogecoin": [
            "dogecoin shiba inu cryptocurrency",
            "doge meme dog finance coin",
            "shiba inu dog funny crypto",
        ],
        "DOGE": [
            "dogecoin shiba inu cryptocurrency",
            "doge meme dog finance coin",
        ],
        "Shiba": [
            "shiba inu dog cryptocurrency",
            "shiba dog golden crypto token",
        ],
        "SHIB": [
            "shiba inu dog cryptocurrency",
            "shiba dog golden crypto token",
        ],
        "Pepe": [
            "frog meme cryptocurrency digital",
            "green frog internet meme art",
            "pepe frog digital culture",
        ],
        "PEPE": [
            "frog meme cryptocurrency digital",
            "green frog internet meme art",
        ],
        "WIF": [
            "dog hat cryptocurrency solana",
            "dog wearing hat funny meme",
        ],
        "dogwifhat": [
            "dog hat cryptocurrency solana",
            "dog wearing hat funny meme",
        ],
        "BONK": [
            "dog cryptocurrency solana airdrop",
            "bonk dog meme solana crypto",
        ],
        "FLOKI": [
            "viking warrior cryptocurrency",
            "viking helmet norse mythology",
        ],
        "memecoin": [
            "meme cryptocurrency rocket moon",
            "crypto meme community coins viral",
        ],
        "market": [
            "cryptocurrency market chart bitcoin",
            "crypto trading chart analysis dark",
            "bitcoin market bull run abstract",
        ],
        "DeFi": [
            "decentralized finance blockchain network",
            "defi protocol smart contract futuristic",
        ],
        "Radix": [
            "blockchain network nodes blue",
            "radix technology network abstract blue",
        ],
        "guide": [
            "crypto guide compass research",
            "research investment guide map direction",
        ],
        "risks": [
            "risk warning cryptocurrency danger",
            "crypto risk caution red warning",
        ],
        "psychology": [
            "trading psychology brain decision",
            "mind decision finance stress trading",
        ],
        "millionaires": [
            "crypto wealth gold coins success",
            "rich success wealth cryptocurrency gold",
        ],
        "trending": [
            "cryptocurrency trending chart viral",
            "trending crypto coins social media",
        ],
        "bitcoin": [
            "bitcoin gold digital currency",
            "bitcoin coin glowing dark abstract",
            "bitcoin halving blockchain digital art",
        ],
        "culture": [
            "internet meme culture digital art",
            "meme culture online community viral",
        ],
        "history": [
            "crypto history timeline blockchain",
            "cryptocurrency history milestones abstract",
        ],
    }

    query_list = QUERY_MAP.get(query, [f"{query} cryptocurrency"])
    search_query = random.choice(query_list)
    print(f"Fetching Unsplash image for query: '{search_query}'")

    used_ids = _load_used_image_ids()
    print(f"Already used image IDs: {len(used_ids)}")

    pages_to_try = random.sample(range(1, 4), min(3, 3))

    for page in pages_to_try:
        try:
            params = urllib.parse.urlencode({
                "query": search_query,
                "orientation": "landscape",
                "per_page": 30,
                "page": page,
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
                print(f"No Unsplash results for '{search_query}' page {page}")
                continue

            fresh = [r for r in results if r["id"] not in used_ids]
            if not fresh:
                print(f"All {len(results)} results on page {page} already used, trying next page...")
                continue

            photo = random.choice(fresh[:10])
            raw_url = photo["urls"]["raw"]
            image_url = f"{raw_url}&w={width}&h={height}&fit=crop&auto=format&q=80"
            print(f"Unsplash image selected: {photo.get('id')} by {photo.get('user', {}).get('name', 'unknown')}")
            return image_url

        except Exception as e:
            print(f"Unsplash fetch failed (page {page}): {e}")
            continue

    if len(query_list) > 1:
        fallback_query = random.choice([q for q in query_list if q != search_query])
        print(f"Trying fallback query: '{fallback_query}'")
        try:
            params = urllib.parse.urlencode({
                "query": fallback_query,
                "orientation": "landscape",
                "per_page": 30,
                "page": 1,
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
            fresh = [r for r in results if r["id"] not in used_ids]
            pool_imgs = fresh[:10] if fresh else results[:10]
            if pool_imgs:
                photo = random.choice(pool_imgs)
                raw_url = photo["urls"]["raw"]
                image_url = f"{raw_url}&w={width}&h={height}&fit=crop&auto=format&q=80"
                print(f"Unsplash fallback query image: {photo.get('id')} by {photo.get('user', {}).get('name', 'unknown')}")
                return image_url
        except Exception as e:
            print(f"Unsplash fallback query failed: {e}")

    print("All Unsplash attempts exhausted, using static fallback")
    return _unsplash_fallback(query)


def _unsplash_fallback(topic_key: str) -> str:
    FALLBACKS = {
        "HYDRA":       "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&h=630&fit=crop&auto=format",
        "HydraSwap":   "https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=1200&h=630&fit=crop&auto=format",
        "Dogecoin":    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=630&fit=crop&auto=format",
        "DOGE":        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=630&fit=crop&auto=format",
        "Shiba":       "https://images.unsplash.com/photo-1620321023374-d1a68fbc720d?w=1200&h=630&fit=crop&auto=format",
        "SHIB":        "https://images.unsplash.com/photo-1620321023374-d1a68fbc720d?w=1200&h=630&fit=crop&auto=format",
        "Pepe":        "https://images.unsplash.com/photo-1639762681057-408e52192e55?w=1200&h=630&fit=crop&auto=format",
        "PEPE":        "https://images.unsplash.com/photo-1639762681057-408e52192e55?w=1200&h=630&fit=crop&auto=format",
        "WIF":         "https://images.unsplash.com/photo-1645731012575-3799282e8da5?w=1200&h=630&fit=crop&auto=format",
        "BONK":        "https://images.unsplash.com/photo-1643101809204-6fb869816dbe?w=1200&h=630&fit=crop&auto=format",
        "FLOKI":       "https://images.unsplash.com/photo-1589254065878-42c9da997008?w=1200&h=630&fit=crop&auto=format",
        "memecoin":    "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200&h=630&fit=crop&auto=format",
        "market":      "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&h=630&fit=crop&auto=format",
        "DeFi":        "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&h=630&fit=crop&auto=format",
        "Radix":       "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&h=630&fit=crop&auto=format",
        "guide":       "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&h=630&fit=crop&auto=format",
        "risks":       "https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?w=1200&h=630&fit=crop&auto=format",
        "psychology":  "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&h=630&fit=crop&auto=format",
        "millionaires":"https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=1200&h=630&fit=crop&auto=format",
        "trending":    "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200&h=630&fit=crop&auto=format",
        "bitcoin":     "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&h=630&fit=crop&auto=format",
        "culture":     "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200&h=630&fit=crop&auto=format",
        "history":     "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200&h=630&fit=crop&auto=format",
    }
    return FALLBACKS.get(
        topic_key,
        "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200&h=630&fit=crop&auto=format"
    )


# ---------------------------------------------------------------------------
# Topic pools
# ---------------------------------------------------------------------------

HYDRA_TOPICS = [
    ("HYDRA", "Write an educational article about the HYDRA memecoin on Radix DLT. Focus on the weekly burn mechanism (100,000 HYDRA burned every week), the HydraSwap DEX, and what makes it unique as a community-driven token launched on February 8, 2026."),
    ("HYDRA", "Write an article explaining how to buy HYDRA token on Radix DLT using HydraSwap. Explain what Radix DLT is, why it matters for DeFi, and what the HYDRA community is building."),
    ("HydraSwap", "Write about HydraSwap, the decentralized exchange (DEX) built on Radix DLT where HYDRA token is traded. Explain how DEXs work, why Radix DLT's asset-oriented model is different from EVM chains, and the role of HydraSwap in the HYDRA ecosystem."),
]

MEMECOIN_TOPICS = [
    ("trending", "Using ALL the data provided — CoinGecko trending coins, CMC top gainers, top memecoins by market cap, Google Trends rising search terms, and latest news headlines — identify the single most interesting crypto topic attracting real attention RIGHT NOW. Prioritize topics that appear across multiple data sources simultaneously (e.g., a coin trending on CoinGecko AND appearing in Google search spikes AND mentioned in recent headlines). Tell the full story: where the narrative came from, why people are paying attention today, verified facts about the project or event, and what the market data shows. Do not default to Dogecoin, Shiba Inu, Pepe, Bonk, WIF or Floki unless they are genuinely leading across multiple data signals."),
    ("Dogecoin",    "Write the story of Dogecoin (DOGE): from joke to massive market cap. Cover the 2013 origin, Reddit community, Elon Musk influence, and the 2021 explosion. Use real facts and current market data provided."),
    ("Shiba",       "Write a deep dive into Shiba Inu (SHIB): the DOGE killer narrative, ShibArmy, Vitalik Buterin burn event, Shibarium launch. Use real data provided."),
    ("Pepe",        "Write about Pepe (PEPE) coin: how a 4chan frog became a top memecoin in 2023. Cover the cultural roots and current on-chain data provided."),
    ("WIF",         "Write about WIF (dogwifhat) on Solana: the hat-wearing dog that reached multi-billion market cap. Cover the meme origin, Solana memecoin culture, and current market data provided."),
    ("BONK",        "Write about BONK on Solana: the community airdrop that energized Solana in December 2022. Cover how it distributed tokens and current market position using data provided."),
    ("FLOKI",       "Write about FLOKI: the Viking-branded memecoin, FlokiFi DeFi suite, and global marketing. Use current market data provided."),
    ("millionaires","Write about the memecoins that gave life-changing returns to early holders. What patterns did they share? Use current market data provided."),
    ("guide",       "Write a guide: How to research a memecoin before investing. Cover on-chain data, community signals, liquidity, tokenomics red flags, and timing. Reference current market data provided as examples."),
    ("memecoin",    "Write about memecoin culture: why internet memes are the most powerful marketing force in crypto, community as product, and viral mechanics. Use current top memecoin data provided."),
    ("risks",       "Write an honest article about the risks of memecoins: rug pulls, wash trading, low liquidity traps, and how to protect yourself. Use current market data provided as real examples."),
    ("culture",     "Write about the cultural history of memecoins: from Dogecoin's Shibe meme to the explosion of Solana memecoins. Explore how internet culture became a financial force."),
    ("history",     "Write about a significant moment in memecoin history — chosen based on whatever is most relevant to the trending data and news headlines provided. Tell the full story with verified facts."),
]

MARKET_TOPICS = [
    ("market",     "Write a market analysis of the current crypto and memecoin sector. Use ALL the real-time market data provided (global market cap, BTC dominance, trending coins, top gainers, Google Trends signals, and latest news headlines) to build a comprehensive narrative about what is actually happening in the market right now."),
    ("DeFi",       "Write about DeFi on Radix DLT: why Radix's asset-oriented model differs from EVM, and the opportunity for new projects like HYDRA. Reference current DeFi volume data provided."),
    ("psychology", "Write about the psychology of memecoin investing: FOMO, diamond hands, paper hands, and how emotion drives price action. Use current trending coin data provided as real examples."),
    ("bitcoin",    "Write about Bitcoin's current role in the crypto market. Use the global market data and BTC dominance figures provided to anchor the article in what is actually happening now."),
]

if hour < 13:
    pool = HYDRA_TOPICS
elif hour < 20:
    pool = MEMECOIN_TOPICS
else:
    pool = MARKET_TOPICS + MEMECOIN_TOPICS

# ---------------------------------------------------------------------------
# STEP 1: Fetch live trend signals BEFORE picking the topic
# ---------------------------------------------------------------------------
print("Fetching external trend signals (Google Trends + RSS) to guide topic selection...")
trend_signals_text, google_terms, rss_headlines = build_trend_signals()

# ---------------------------------------------------------------------------
# STEP 2: Pick topic driven by live signals
# ---------------------------------------------------------------------------
print("Scoring topic pool against live signals...")
image_key, topic = pick_topic_from_signals(pool, google_terms, rss_headlines)

# ---------------------------------------------------------------------------
# Fetch rich market context after topic is known
# ---------------------------------------------------------------------------
print(f"Building market context for topic key: {image_key}")
print(f"CoinMarketCap API: {'enabled' if cmc_key else 'disabled (no key)'}")
print(f"CoinGecko API: {'Pro' if cg_key else 'free tier'}")
market_context = build_market_context(image_key)

# ---------------------------------------------------------------------------
# Category & tags
# ---------------------------------------------------------------------------

if pool == HYDRA_TOPICS:
    category = random.choice(["News", "Guides"])
elif image_key in ["Dogecoin","DOGE","Shiba","SHIB","Pepe","PEPE","WIF","dogwifhat","BONK","FLOKI","memecoin","millionaires","trending","culture","history"]:
    category = "Moonshots"
elif image_key == "guide":
    category = "Guides"
elif image_key in ["market","DeFi","Radix","bitcoin"]:
    category = "Market Analysis"
elif image_key == "psychology":
    category = "Market Analysis"
else:
    category = "Moonshots"

tags_map = {
    "HYDRA":       ["hydra", "radix", "memecoin"],
    "HydraSwap":   ["hydra", "hydraswap", "dex", "radix"],
    "Dogecoin":    ["doge", "dogecoin", "memecoin"],
    "Shiba":       ["shib", "shiba", "memecoin"],
    "Pepe":        ["pepe", "memecoin", "culture"],
    "WIF":         ["wif", "solana", "memecoin"],
    "BONK":        ["bonk", "solana", "memecoin"],
    "FLOKI":       ["floki", "memecoin", "defi"],
    "market":      ["market", "analysis", "crypto"],
    "guide":       ["guide", "memecoin", "crypto"],
    "risks":       ["risk", "safety", "memecoin"],
    "psychology":  ["psychology", "trading", "memecoin"],
    "millionaires":["memecoin", "history", "doge"],
    "DeFi":        ["defi", "radix", "blockchain"],
    "trending":    ["trending", "memecoin", "crypto"],
    "bitcoin":     ["bitcoin", "btc", "market"],
    "culture":     ["memecoin", "culture", "history"],
    "history":     ["memecoin", "history", "crypto"],
}
tags = tags_map.get(image_key, ["memecoin", "crypto"])

# ---------------------------------------------------------------------------
# System prompt — full HYDRA Chronicles editorial policy
# ---------------------------------------------------------------------------

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

system_msg = """You are the senior English language content writer, researcher, and editorial strategist for HYDRA Chronicles, the official blog of HYDRA, published at hydraxrd.com/blog.

Your mission is to create accurate, engaging, well-researched, human-sounding articles about memecoins, cryptocurrency culture, Bitcoin, crypto trends, blockchain ecosystems, and the broader cryptocurrency market.

The primary editorial focus is memecoins that are currently trending or attracting significant attention, especially those appearing in trending sections or receiving notable market attention on platforms such as CoinMarketCap and CoinGecko.

HYDRA Chronicles must not become a blog that talks only about HYDRA. The publication should cover the memecoin ecosystem as a whole, tell the stories behind trending memecoins, explore the biggest memes and cultural moments in cryptocurrency, discuss Bitcoin, and occasionally connect relevant topics to the HYDRA ecosystem and Radix DLT.

The central editorial principle is simple: Never invent anything. Every factual claim must be confirmed through a reliable source before being presented as fact.

CORE EDITORIAL MISSION
Write about what is actually happening in the cryptocurrency and memecoin ecosystem. You are provided with three layers of real-time signals: (1) market data from CoinGecko and CoinMarketCap showing trending coins and top gainers, (2) Google Trends data showing what people are actively searching right now, and (3) the latest news headlines from major crypto publications. Use all three layers together. A topic that appears in all three sources simultaneously is the strongest possible editorial signal — that is what the world wants to read about today. Do not default to writing about the same tokens repeatedly. Choose the subject based on genuine relevance to all the data provided.

When an article focuses on a trending memecoin, tell its story. Explain where the meme or narrative came from when that information can be verified. Explain how the project emerged. Explain why people started paying attention to it. Explain relevant milestones. Explain the community or cultural narrative surrounding it. Explain what can actually be verified about the project. Do not simply write an article consisting of price statistics. The story behind a memecoin is often more interesting than its price.

VERIFY EVERYTHING
Accuracy is more important than speed, hype, or article length. Never invent a founder, launch date, partnership, listing, market capitalization, trading volume, community size, token supply, technical feature, roadmap, price, historical event, or explanation for a price movement. If something cannot be verified, do not present it as fact. If different reputable sources provide conflicting information, acknowledge the discrepancy. Never fill missing information with assumptions.

NO FINANCIAL PROMISES
HYDRA Chronicles is an editorial publication, not a financial advisor. Never guarantee profits. Never tell readers that a token will definitely rise or fall. Never describe a cryptocurrency as a guaranteed investment. Never create artificial urgency designed to make readers buy a token. Market analysis must remain factual, balanced, and clearly separated from speculation.

HYDRA
HYDRA may be discussed when there is a legitimate editorial connection to the topic. The HYDRA ecosystem includes HydraSwap, HydraBurn, HydraBubbles, and HydraBattleArena. Do not force HYDRA into an article simply for promotional purposes. Never invent HYDRA statistics, users, transaction numbers, trading volume, revenue, partnerships, or exchange listings. Before describing a HYDRA feature, verify the information using an official HYDRA source.

RADIX DLT
When discussing Radix DLT, use only verifiable information. Do not invent technical capabilities, adoption numbers, partnerships, or network performance claims. Explain technical concepts clearly for readers who are not blockchain experts.

BITCOIN
Articles may discuss Bitcoin's history, market movements, narratives, major milestones, cultural influence, relationship with altcoins and memecoins, and market cycles. Never portray Bitcoin as guaranteed to rise or fall. When discussing Bitcoin's price or market data, verify the information from a reliable current source.

ABSOLUTE FORMATTING RULES
NEVER use bullet points. NEVER use numbered lists. NEVER use dash-based lists. NEVER use asterisks for lists. The article must be written entirely as flowing prose organized with headings and paragraphs. Use ## for main section headings only. Never use ### or ####.

LINKS
All links must be masked as markdown hyperlinks using [visible text](url) format. Never display raw URLs.

CRYPTOCURRENCY PRICES
Always express cryptocurrency prices in United States dollars using standard decimal notation (e.g. $0.00002083). Never use scientific notation. Percentages must contain no more than two decimal places.

ARTICLE LENGTH
Every article must contain at least 1,200 words in the content field. Never reach the minimum by repeating information or padding with generic statements.

TITLE AND SLUG
The slug must be derived ONLY from the final title: lowercase, hyphens only, no dates, no timestamps, max 80 characters.

SEO
Optimize every article naturally for search engines without sacrificing readability. Do not keyword stuff. Do not create clickbait titles. The article should satisfy the reader's search intent. Use the Google Trends keywords naturally within the article text where editorially appropriate — this improves organic search relevance without stuffing.

FINAL QUALITY CONTROL
Before returning, verify: article is in English, at least 1,200 words, no bullet points, no numbered lists, no ### or #### headings, no raw URLs, prices in USD decimal notation, percentages max 2 decimal places, slug from title only, no unsupported claims, no fictional statistics.

OUTPUT FORMAT
Return ONLY a valid raw JSON object. No markdown fences. No explanations before or after the JSON."""

trend_block = f"\n{trend_signals_text}" if trend_signals_text else ""

user_msg = (
    f"Today is {today}. {topic}\n"
    f"{hydra_instruction}"
    f"{market_context}"
    f"{trend_block}\n\n"
    "IMPORTANT EDITORIAL INSTRUCTION: You have been given three layers of real-time signals above:\n"
    "1. Market data (CoinGecko + CMC): which coins are trending and gaining right now.\n"
    "2. Google Trends: what people are actively searching for in the crypto space right now.\n"
    "3. News headlines: what the crypto media is covering right now.\n\n"
    "Cross-reference all three layers. A topic appearing in all three simultaneously is the strongest editorial signal. "
    "A topic appearing in two is strong. A topic in only one is weak. "
    "Choose the most relevant subject based on this combined signal — not random selection.\n\n"
    "Do not write about Dogecoin, Shiba Inu, Pepe, Bonk, WIF or Floki by default — only choose them if the combined data confirms they are genuinely leading right now.\n\n"
    "Write a compelling article of AT LEAST 1200 words. "
    "Use ## section headers. NO bullet points, NO dashes, NO ### headers. Write in flowing paragraphs only. "
    "ALL links must be [text](url) format, never raw URLs. "
    "Write all crypto prices in standard decimal notation (e.g. $0.00002083), NEVER scientific notation. Round percentages to 2 decimal places. "
    "Weave prices, volumes, market cap, dominance, trending coins, and Google search signals naturally into the article. "
    "Only use facts provided or widely established public knowledge. "
    f"End the content field with this exact disclaimer: {disclaimer}\n\n"
    "Return ONLY this JSON:\n"
    "{\n"
    '  "title": "<catchy engaging title that accurately reflects the article subject>",\n'
    '  "slug": "<URL slug derived from the title: lowercase, hyphens only, NO dates, NO timestamps, max 80 chars>",\n'
    '  "excerpt": "<compelling summary under 200 chars, prices in decimal notation only>",\n'
    '  "content": "<full article in markdown, use \\n for newlines, minimum 1200 words, NO bullet points, NO dashes, NO ### headers, ALL links masked, prices always in decimal notation>",\n'
    f'  "category": "{category}",\n'
    '  "author": "HYDRA",\n'
    f'  "date": "{today_iso}",\n'
    '  "readingTime": 6,\n'
    '  "featured": false,\n'
    '  "coverImage": "",\n'
    f'  "tags": {json.dumps(tags)}\n'
    "}"
)

# ---------------------------------------------------------------------------
# LLM call via OpenRouter — up to 5 attempts across all models
# ---------------------------------------------------------------------------

# Models ordered by reliability — most consistent free models first.
MODELS = [
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "openrouter/free",
]

MAX_ATTEMPTS = 5
response_data = None
content = ""
attempt = 0

while attempt < MAX_ATTEMPTS and not response_data:
    model = MODELS[attempt % len(MODELS)]
    attempt += 1
    print(f"Attempt {attempt}/{MAX_ATTEMPTS} — model: {model}")

    if attempt > 1:
        wait_secs = 3 * (attempt - 1)
        print(f"Waiting {wait_secs}s before retry...")
        time.sleep(wait_secs)

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.7,
        "max_tokens": 8000
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
            print(f"Attempt {attempt}: model {model} returned empty content, retrying...")
            continue
        content = content.strip()
        if "{" not in content:
            print(f"Attempt {attempt}: model {model} returned non-JSON, skipping: {content[:120]}")
            continue
        lower_content = content.lower().lstrip()
        non_json_prefixes = ("user safety", "i cannot", "i'm sorry", "as an ai", "sorry,")
        if any(lower_content.startswith(p) for p in non_json_prefixes):
            print(f"Attempt {attempt}: model {model} returned refusal/safety message, retrying: {content[:120]}")
            continue
        response_data = data
        print(f"Attempt {attempt}: SUCCESS with {model} ({len(content)} chars)")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Attempt {attempt}: HTTP error from {model}: {e.code} - {body[:200]}")
        continue
    except Exception as e:
        print(f"Attempt {attempt}: unexpected error with {model}: {e}")
        continue

if not response_data or not content:
    print(f"All {MAX_ATTEMPTS} attempts failed. Exiting.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Parse JSON response
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Slug enforcement & deduplication
# ---------------------------------------------------------------------------

raw_slug = post.get("slug", "")
if not raw_slug or re.search(r"\d{4}-\d{2}-\d{2}", raw_slug):
    raw_slug = title_to_slug(post.get("title", f"post-{timestamp}"))
    print(f"Slug regenerated from title: {raw_slug}")

existing_files = os.listdir("src/data/posts") if os.path.exists("src/data/posts") else []
existing_slugs = {f.replace(".json", "") for f in existing_files if f.endswith(".json")}
final_slug = raw_slug
if final_slug in existing_slugs:
    suffix = timestamp[-5:].replace("-", "")
    final_slug = f"{raw_slug}-{suffix}"
    print(f"Slug deduplicated: {final_slug}")

post["slug"] = final_slug
post["id"] = final_slug

# Always overwrite the date with the full ISO-8601 datetime so the blog's
# sortedPosts() can break ties between same-day articles correctly.
post["date"] = today_iso
print(f"Date set to ISO datetime: {today_iso}")

word_count = len(post.get("content", "").split())
post["readingTime"] = max(1, round(word_count / 200))
post["author"] = "HYDRA"
post["category"] = category

# ---------------------------------------------------------------------------
# Cover image (Unsplash)
# ---------------------------------------------------------------------------

print(f"Fetching Unsplash image for topic key: {image_key}")
image_url = fetch_unsplash_image(image_key)
post["coverImage"] = image_url
print(f"Cover image URL: {image_url}")

# ---------------------------------------------------------------------------
# Save post JSON
# ---------------------------------------------------------------------------

os.makedirs("src/data/posts", exist_ok=True)
out_path = f"src/data/posts/{final_slug}.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(post, f, indent=2, ensure_ascii=False)
print(f"Saved: {out_path}")

# ---------------------------------------------------------------------------
# Update posts-index.json
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Auto-update sitemap.xml
# ---------------------------------------------------------------------------

sitemap_path = "public/sitemap.xml"
sitemap_content = generate_sitemap(existing)
with open(sitemap_path, "w", encoding="utf-8") as f:
    f.write(sitemap_content)
print(f"Sitemap updated: {sitemap_path} ({len(existing)} posts)")

print(f"SUCCESS:{out_path}")
print(f"SLUG:{final_slug}")
