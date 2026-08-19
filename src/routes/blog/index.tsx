import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { allPosts, featuredPost, getPostsByCategory } from '../../lib/blog';
import { PostCard } from '../../components/blog/PostCard';
import { FeaturedPost } from '../../components/blog/FeaturedPost';
import { CategoryFilter } from '../../components/blog/CategoryFilter';

export const Route = createFileRoute('/blog/')({ component: BlogPage });

function BlogPage() {
  const [activeCategory, setActiveCategory] = useState('All Posts');
  const filtered = getPostsByCategory(activeCategory).filter(
    (p) => !(p.featured && activeCategory === 'All Posts'),
  );

  return (
    <main className="min-h-dvh bg-[#05060f] text-white">
      {/* Ambient background blobs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden" aria-hidden>
        <div className="absolute -top-40 -left-20 w-[600px] h-[600px] rounded-full bg-cyan-500/[0.06] blur-[100px] animate-pulse" />
        <div className="absolute bottom-1/4 -right-20 w-[500px] h-[500px] rounded-full bg-pink-500/[0.06] blur-[100px]" />
        <div className="absolute top-1/2 left-1/3 w-[400px] h-[400px] rounded-full bg-purple-500/[0.04] blur-[120px]" />
      </div>

      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-[#05060f]/85 backdrop-blur-xl border-b border-white/[0.06]">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <a
            href="https://hydraxrd.com"
            className="font-black tracking-widest text-cyan-400 text-sm flex items-center gap-2"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            ⬡ HYDRA
          </a>
          <div className="hidden md:flex items-center gap-6 text-xs text-white/40">
            <a href="https://hydraxrd.com" className="hover:text-white transition-colors">Home</a>
            <span className="text-cyan-400 font-semibold">Blog</span>
            <a href="https://x.com/HYDRAXRD" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">X / Twitter</a>
            <a href="https://t.me/hydraxrd" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Telegram</a>
          </div>
          <a
            href="https://hydraxrd.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[10px] font-bold tracking-widest uppercase px-4 py-2 bg-cyan-400 text-black rounded-full hover:-translate-y-0.5 transition-transform shadow-[0_0_20px_rgba(0,210,255,0.3)]"
            style={{ fontFamily: 'Orbitron, monospace' }}
          >
            Buy $HYDR
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 pt-20 pb-16 text-center px-6">
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundImage:
              'linear-gradient(rgba(0,210,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0,210,255,0.04) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
            maskImage:
              'radial-gradient(ellipse 80% 80% at 50% 50%, black 20%, transparent 100%)',
          }}
          aria-hidden
        />
        <div className="inline-flex items-center gap-2 text-[10px] font-bold tracking-[0.15em] uppercase text-cyan-400 border border-cyan-500/30 px-4 py-2 rounded-full bg-cyan-500/5 mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#00d2ff] animate-pulse" />
          Official HYDRA Editorial Hub
        </div>
        <h1
          className="font-black leading-none mb-6"
          style={{ fontFamily: 'Orbitron, monospace', fontSize: 'clamp(3rem, 8vw, 7rem)' }}
        >
          <span className="block text-white">HYDRA</span>
          <span
            className="block"
            style={{
              background: 'linear-gradient(90deg, #00d2ff, #ff3cac)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              filter: 'drop-shadow(0 0 20px rgba(0,210,255,0.4))',
            }}
          >
            CHRONICLES
          </span>
        </h1>
        <p className="text-white/40 text-base max-w-xl mx-auto leading-relaxed mb-6">
          News, ecosystem updates, battle reports, and community stories from the many-headed
          movement on Radix DLT.
        </p>
        <div className="text-xs text-white/20">
          {allPosts.length} article{allPosts.length !== 1 ? 's' : ''} published
        </div>
      </section>

      {/* Main content */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 pb-24">
        {/* Featured post — only shown on All Posts tab */}
        {featuredPost && activeCategory === 'All Posts' && (
          <div className="mb-12">
            <FeaturedPost post={featuredPost} />
          </div>
        )}

        {/* Section label */}
        <div className="mb-6">
          <p className="text-[10px] font-bold tracking-[0.2em] uppercase text-cyan-400 mb-1">Latest Posts</p>
          <h2 className="text-xl font-bold text-white" style={{ fontFamily: 'Orbitron, monospace' }}>
            Recent from the HYDRA Universe
          </h2>
        </div>

        {/* Category filter */}
        <CategoryFilter active={activeCategory} onChange={setActiveCategory} />

        {/* Articles grid */}
        {filtered.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </div>
        ) : (
          <div className="text-center py-24 text-white/20">
            <p className="text-5xl mb-4">🐉</p>
            <p className="text-sm">No posts in this category yet. Check back soon.</p>
          </div>
        )}
      </section>

      {/* Community / Social section */}
      <section className="relative z-10 max-w-6xl mx-auto px-6 pb-24">
        <div className="relative bg-[#0a0c1a] border border-white/[0.07] rounded-2xl overflow-hidden p-10 text-center">
          <div
            className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-48 rounded-full pointer-events-none"
            style={{ background: 'radial-gradient(ellipse, rgba(0,210,255,0.08), transparent 70%)' }}
            aria-hidden
          />
          <h2
            className="font-bold text-2xl mb-4"
            style={{
              fontFamily: 'Orbitron, monospace',
              background: 'linear-gradient(90deg, #00d2ff, #ff3cac)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Stay in the Loop
          </h2>
          <p className="text-white/40 text-sm max-w-lg mx-auto mb-8 leading-relaxed">
            Follow HYDRA on every platform where the community lives. Never miss an update from
            the universe.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            {[
              { label: 'Website', href: 'https://hydraxrd.com', color: 'hover:border-cyan-400/40 hover:text-cyan-400' },
              { label: 'X / Twitter', href: 'https://x.com/HYDRAXRD', color: 'hover:border-white/30 hover:text-white' },
              { label: 'Telegram', href: 'https://t.me/hydraxrd', color: 'hover:border-sky-400/40 hover:text-sky-400' },
              { label: 'Discord', href: '#', color: 'hover:border-indigo-400/40 hover:text-indigo-400' },
              { label: 'YouTube', href: '#', color: 'hover:border-red-400/40 hover:text-red-400' },
              { label: 'Instagram', href: '#', color: 'hover:border-pink-400/40 hover:text-pink-400' },
              { label: 'TikTok', href: '#', color: 'hover:border-rose-400/40 hover:text-rose-400' },
              { label: 'Reddit', href: '#', color: 'hover:border-orange-400/40 hover:text-orange-400' },
            ].map(({ label, href, color }) => (
              <a
                key={label}
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className={`text-xs font-semibold px-4 py-2.5 rounded-lg border border-white/[0.08] bg-[#0f1226] text-white/40 transition-all duration-200 hover:-translate-y-0.5 ${color}`}
              >
                {label}
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/[0.05] py-10">
        <div className="max-w-6xl mx-auto px-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p
              className="font-black text-cyan-400 text-lg tracking-widest mb-1"
              style={{ fontFamily: 'Orbitron, monospace' }}
            >
              ⬡ HYDRA
            </p>
            <p className="text-xs text-white/20">
              Unite the Radix Meme Revolution.
            </p>
          </div>
          <div className="flex gap-5 text-xs text-white/25">
            <a href="https://x.com/HYDRAXRD" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">X / Twitter</a>
            <a href="https://t.me/hydraxrd" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Telegram</a>
            <a href="https://hydraxrd.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">hydraxrd.com</a>
          </div>
          <p className="text-xs text-white/15">© 2026 HYDRA · hydraxrd.com/blog · All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}
