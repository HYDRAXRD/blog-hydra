import { Link } from '@tanstack/react-router';
import type { BlogPost } from '../../lib/blog';
import { formatDate } from '../../lib/blog';

interface FeaturedPostProps {
  post: BlogPost;
}

export function FeaturedPost({ post }: FeaturedPostProps) {
  return (
    <article className="group relative rounded-2xl overflow-hidden border border-white/[0.07] transition-all duration-300 hover:-translate-y-1 hover:border-cyan-500/25 hover:shadow-[0_0_40px_rgba(0,210,255,0.12)]">
      {/* Cover */}
      <div className="relative aspect-[21/9] sm:aspect-video overflow-hidden">
        {post.coverImage ? (
          <img
            src={post.coverImage}
            alt={post.title}
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-[1.02]"
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-[#030810] via-[#060f25] to-[#150015]" />
        )}
        {/* Cinematic overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#05060f]/95 via-[#05060f]/60 to-[#05060f]/10" />
      </div>

      {/* Content over image */}
      <div className="absolute inset-0 flex items-end p-8 md:p-10">
        <div className="max-w-xl">
          <span className="inline-flex items-center gap-1 text-[10px] font-bold tracking-[0.12em] uppercase text-cyan-400 bg-cyan-500/12 border border-cyan-500/30 px-3 py-1 rounded-full mb-4">
            ⭐ Featured
          </span>
          <h2
            className="font-black text-white leading-tight mb-3 text-xl md:text-2xl lg:text-3xl"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            {post.title}
          </h2>
          <p className="text-white/50 text-sm leading-relaxed mb-4 line-clamp-3">
            {post.excerpt}
          </p>
          <div className="flex items-center gap-4 text-[10px] text-white/25 mb-5">
            <span>📅 {formatDate(post.date)}</span>
            <span>⏱ {post.readingTime} min read</span>
            <span>✍️ {post.author}</span>
          </div>
          <Link
            to="/blog/$slug"
            params={{ slug: post.slug }}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-400 to-cyan-600 text-black font-bold text-xs tracking-widest uppercase rounded-full transition-all hover:-translate-y-0.5 hover:shadow-[0_0_30px_rgba(0,210,255,0.4)]"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            Read Article →
          </Link>
        </div>
      </div>
    </article>
  );
}
