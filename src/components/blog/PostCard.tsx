import { Link } from '@tanstack/react-router';
import type { BlogPost } from '../../lib/blog';
import { formatDate } from '../../lib/blog';

const categoryColors: Record<string, string> = {
  News: 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40',
  Ecosystem: 'bg-pink-500/20 text-pink-400 border border-pink-500/40',
  Community: 'bg-purple-500/20 text-purple-400 border border-purple-500/40',
  'Game Updates': 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40',
  Guides: 'bg-amber-500/20 text-amber-400 border border-amber-500/40',
  Announcements: 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40',
};

interface PostCardProps {
  post: BlogPost;
}

export function PostCard({ post }: PostCardProps) {
  const colorClass =
    categoryColors[post.category] ??
    'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40';

  return (
    <article className="group flex flex-col bg-[#0a0c1a] border border-white/[0.07] rounded-xl overflow-hidden transition-all duration-200 hover:-translate-y-1 hover:border-cyan-500/25 hover:shadow-[0_0_30px_rgba(0,210,255,0.12)]">
      {/* Cover image */}
      <div className="relative overflow-hidden aspect-video">
        {post.coverImage ? (
          <img
            src={post.coverImage}
            alt={post.title}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-[#050a1a] via-[#0a1640] to-[#001a30] flex items-center justify-center">
            <svg
              className="w-12 h-12 text-cyan-500/20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1"
            >
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
              <polyline points="13 2 13 9 20 9" />
            </svg>
          </div>
        )}
        <span
          className={`absolute top-3 left-3 text-[10px] font-bold tracking-widest uppercase px-2 py-1 rounded-full ${colorClass}`}
        >
          {post.category}
        </span>
        <span className="absolute bottom-3 right-3 text-[10px] font-semibold bg-black/70 text-white/50 px-2 py-1 rounded-full backdrop-blur border border-white/10">
          {post.readingTime} min
        </span>
      </div>

      {/* Body */}
      <div className="flex flex-col flex-1 p-5">
        <h3
          className="font-bold text-white/90 text-sm leading-snug mb-2 transition-colors group-hover:text-cyan-400"
          style={{ fontFamily: 'Orbitron, monospace' }}
        >
          {post.title}
        </h3>
        <p className="text-white/40 text-xs leading-relaxed flex-1 line-clamp-3">
          {post.excerpt}
        </p>

        {/* Footer */}
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/[0.06]">
          <div className="flex items-center gap-3 text-[10px] text-white/25">
            <span>{formatDate(post.date)}</span>
          </div>
          <Link
            to="/blog/$slug"
            params={{ slug: post.slug }}
            className="text-[10px] font-bold tracking-widest uppercase text-cyan-400 flex items-center gap-1 transition-all group-hover:gap-2"
          >
            Read →
          </Link>
        </div>
      </div>
    </article>
  );
}
