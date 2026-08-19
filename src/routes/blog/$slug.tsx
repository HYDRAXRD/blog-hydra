import { createFileRoute, notFound, Link } from '@tanstack/react-router';
import { getPostBySlug, formatDate } from '../../lib/blog';

export const Route = createFileRoute('/blog/$slug')({
  loader: ({ params }) => {
    const post = getPostBySlug(params.slug);
    if (!post) throw notFound();
    return post;
  },
  component: PostPage,
});

// Minimal Markdown → HTML renderer (no external dependencies needed)
function renderMarkdown(md: string): string {
  return md
    .split('\n')
    .map((line) => {
      if (line.startsWith('### '))
        return `<h3 class="text-lg font-bold text-white mt-8 mb-3" style="font-family:Orbitron,monospace">${line.slice(4)}</h3>`;
      if (line.startsWith('## '))
        return `<h2 class="text-xl font-bold text-cyan-400 mt-10 mb-4" style="font-family:Orbitron,monospace">${line.slice(3)}</h2>`;
      if (line.startsWith('# '))
        return `<h1 class="text-2xl font-black text-white mt-6 mb-6" style="font-family:Orbitron,monospace">${line.slice(2)}</h1>`;
      if (line.startsWith('- '))
        return `<li class="ml-5 list-disc text-white/60 mb-2 leading-relaxed">${parseMdInline(line.slice(2))}</li>`;
      if (line.trim() === '') return '<div class="mb-2"></div>';
      return `<p class="text-white/60 leading-relaxed mb-4">${parseMdInline(line)}</p>`;
    })
    .join('');
}

function parseMdInline(text: string): string {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em class="italic text-white/80">$1</em>')
    .replace(/`(.+?)`/g, '<code class="bg-white/10 text-cyan-400 px-1.5 py-0.5 rounded text-sm font-mono">$1</code>')
    .replace(
      /\[(.+?)\]\((.+?)\)/g,
      '<a href="$2" class="text-cyan-400 underline hover:text-cyan-300 transition-colors" target="_blank" rel="noopener noreferrer">$1</a>',
    );
}

function PostPage() {
  const post = Route.useLoaderData();

  return (
    <main className="min-h-dvh bg-[#05060f] text-white">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-[#05060f]/85 backdrop-blur-xl border-b border-white/[0.06]">
        <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
          <a
            href="https://hydraxrd.com"
            className="font-black tracking-widest text-cyan-400 text-sm"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            ⬡ HYDRA
          </a>
          <Link to="/blog" className="text-xs text-white/40 hover:text-white transition-colors flex items-center gap-1">
            ← Back to Blog
          </Link>
        </div>
      </nav>

      {/* Cover image */}
      {post.coverImage && (
        <div className="w-full max-h-[500px] overflow-hidden">
          <img
            src={post.coverImage}
            alt={post.title}
            className="w-full h-full object-cover"
          />
        </div>
      )}

      {/* Article content */}
      <article className="max-w-3xl mx-auto px-6 py-16">
        {/* Category + meta */}
        <div className="flex flex-wrap items-center gap-3 mb-6">
          <span className="px-3 py-1 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 font-bold tracking-wider uppercase text-[10px]">
            {post.category}
          </span>
          <span className="text-xs text-white/30">📅 {formatDate(post.date)}</span>
          <span className="text-xs text-white/30">⏱ {post.readingTime} min read</span>
          <span className="text-xs text-white/30">✍️ {post.author}</span>
        </div>

        {/* Title */}
        <h1
          className="font-black text-white leading-tight mb-6"
          style={{
            fontFamily: 'Orbitron, monospace',
            fontSize: 'clamp(1.5rem, 4vw, 2.5rem)',
          }}
        >
          {post.title}
        </h1>

        {/* Excerpt / lead */}
        <p className="text-white/40 text-base leading-relaxed border-l-2 border-cyan-500/40 pl-4 mb-10">
          {post.excerpt}
        </p>

        <hr className="border-white/[0.07] mb-10" />

        {/* Rendered content */}
        <div
          className="prose-hydra"
          dangerouslySetInnerHTML={{ __html: renderMarkdown(post.content) }}
        />

        {/* Tags */}
        {post.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-12 pt-8 border-t border-white/[0.06]">
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="text-[10px] px-3 py-1 rounded-full bg-white/5 text-white/30 border border-white/10"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* Back to blog */}
        <div className="mt-12">
          <Link
            to="/blog"
            className="inline-flex items-center gap-2 text-xs font-bold tracking-widest uppercase text-cyan-400 hover:gap-3 transition-all"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            ← Back to Chronicles
          </Link>
        </div>
      </article>

      {/* Footer */}
      <footer className="border-t border-white/[0.05] py-8">
        <div className="max-w-3xl mx-auto px-6 flex flex-wrap items-center justify-between gap-4">
          <p className="text-xs text-white/20">© 2026 HYDRA · hydraxrd.com/blog</p>
          <div className="flex gap-5 text-xs text-white/25">
            <a href="https://x.com/HYDRAXRD" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">X / Twitter</a>
            <a href="https://t.me/hydraxrd" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Telegram</a>
            <a href="https://hydraxrd.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">hydraxrd.com</a>
          </div>
        </div>
      </footer>
    </main>
  );
}
