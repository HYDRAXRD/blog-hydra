/**
 * Minimal, dependency-free Markdown -> HTML renderer.
 *
 * The article generation tool writes plain Markdown into
 * `src/data/posts/*.json`, so we only need the subset it produces:
 * headings, paragraphs, bold/italic, links, lists, blockquotes and rules.
 */

const escapeHtml = (s: string): string =>
  s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

const inline = (s: string): string =>
  escapeHtml(s)
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");

/**
 * Map of exchange name patterns to their affiliate/referral URLs.
 * The key is a regex pattern (case-insensitive) to match the exchange name in text.
 * The value is the referral URL.
 */
const AFFILIATE_LINKS: { pattern: RegExp; url: string; label: string }[] = [
  {
    pattern: /\bBinance\b/gi,
    url: "https://www.binance.com/activity/referral-entry/CPA?ref=CPA_00ULM3PVBU",
    label: "Binance",
  },
  {
    pattern: /\bCoinbase\b/gi,
    url: "https://coinbase.com/join/48YKTHQ?src=ios-link",
    label: "Coinbase",
  },
  {
    pattern: /\bOKX\b|\bOKEx\b/gi,
    url: "https://okx.com/pt-br/join/3102874",
    label: "OKX",
  },
  {
    pattern: /\bMEXC\b/gi,
    url: "https://s.mexc.com/referral/7zWMbHQ5uu",
    label: "MEXC",
  },
  {
    pattern: /\bCrypto\.com\b/gi,
    url: "https://crypto.com/app/se52rhs8r9",
    label: "Crypto.com",
  },
  {
    pattern: /\bBybit\b/gi,
    url: "https://www.bybit.com/invite?ref=4RQBXK&medium=referral&utm_campaign=evergreen&share_to=post",
    label: "Bybit",
  },
  {
    pattern: /\bCoinEx\b/gi,
    url: "https://www.coinex.com/register?rc=qg926&channel=Referral",
    label: "CoinEx",
  },
];

/**
 * Replaces plain exchange name mentions in rendered HTML with affiliate links.
 * Only replaces text nodes (outside of existing <a> tags) to avoid double-linking.
 */
function injectAffiliateLinks(html: string): string {
  // We process text that is NOT already inside an <a>...</a> tag.
  // Strategy: split by existing anchor tags, only process non-anchor segments.
  const anchorSplit = /(<a[\s\S]*?<\/a>)/gi;
  const parts = html.split(anchorSplit);

  return parts
    .map((part) => {
      // If this part IS an anchor tag, leave it untouched
      if (/^<a[\s\S]*<\/a>$/i.test(part)) return part;

      // Otherwise inject affiliate links into the text
      let result = part;
      for (const { pattern, url, label } of AFFILIATE_LINKS) {
        result = result.replace(
          pattern,
          `<a href="${url}" target="_blank" rel="noopener noreferrer sponsored" title="Cadastre-se na ${label}">${label}</a>`,
        );
      }
      return result;
    })
    .join("");
}

export function markdownToHtml(markdown: string): string {
  const blocks = markdown.replace(/\r\n/g, "\n").split(/\n{2,}/);
  const html: string[] = [];

  for (const raw of blocks) {
    const block = raw.trim();
    if (!block) continue;

    if (/^(---|\\*\\*\\*|___)$/.test(block)) {
      html.push("<hr />");
      continue;
    }

    const heading = /^(#{1,6})\s+(.*)$/.exec(block);
    if (heading) {
      const level = Math.min(6, heading[1]!.length + 1);
      html.push(`<h${level}>${inline(heading[2]!)}</h${level}>`);
      continue;
    }

    const lines = block.split("\n");

    if (lines.every((l) => /^\s*[-*+]\s+/.test(l))) {
      html.push(
        `<ul>${lines.map((l) => `<li>${inline(l.replace(/^\s*[-*+]\s+/, ""))}</li>`).join("")}</ul>`,
      );
      continue;
    }

    if (lines.every((l) => /^\s*\d+[.)]\s+/.test(l))) {
      html.push(
        `<ol>${lines.map((l) => `<li>${inline(l.replace(/^\s*\d+[.)]\s+/, ""))}</li>`).join("")}</ol>`,
      );
      continue;
    }

    if (lines.every((l) => /^\s*>/.test(l))) {
      html.push(
        `<blockquote>${inline(lines.map((l) => l.replace(/^\s*>\s?/, "")).join(" "))}</blockquote>`,
      );
      continue;
    }

    html.push(`<p>${lines.map((l) => inline(l)).join("<br />")}</p>`);
  }

  return injectAffiliateLinks(html.join("\n"));
}
