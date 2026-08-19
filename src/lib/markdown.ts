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

export function markdownToHtml(markdown: string): string {
  const blocks = markdown.replace(/\r\n/g, "\n").split(/\n{2,}/);
  const html: string[] = [];

  for (const raw of blocks) {
    const block = raw.trim();
    if (!block) continue;

    if (/^(---|\*\*\*|___)$/.test(block)) {
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

  return html.join("\n");
}
