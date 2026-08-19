import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Search, Rocket } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Particles from "@/components/Particles";
import PostCard from "@/components/PostCard";
import { categories, getFeaturedPost, sortedPosts, type PostCategory } from "@/data/posts";

export const Route = createFileRoute("/blog")({
  head: () => ({
    meta: [
      { title: "HYDRA Blog — Meme Coin News, Moonshots & Market Analysis" },
      {
        name: "description",
        content:
          "Daily meme coin news in English: moonshots, market analysis and case studies of tokens that turned small investors into whales.",
      },
      { property: "og:title", content: "HYDRA Blog — Meme Coin News & Moonshots" },
      {
        property: "og:description",
        content:
          "Meme coin news, moonshot breakdowns and market analysis from the HYDRA community.",
      },
      { property: "og:type", content: "website" },
      { property: "og:url", content: "/blog" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [{ rel: "canonical", href: "/blog" }],
    scripts: [
      {
        type: "application/ld+json",
        children: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "Blog",
          name: "HYDRA Blog",
          description: "Meme coin news, moonshots and market analysis.",
          url: "https://hydraxrd.com/blog",
        }),
      },
    ],
  }),
  component: BlogIndex,
});

function BlogIndex() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<PostCategory | "All">("All");

  const all = useMemo(() => sortedPosts(), []);
  const featured = useMemo(() => getFeaturedPost(), []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return all.filter((p) => {
      const matchCat = category === "All" || p.category === category;
      const matchQuery =
        !q ||
        p.title.toLowerCase().includes(q) ||
        p.excerpt.toLowerCase().includes(q) ||
        (p.tickers ?? []).some((t) => t.toLowerCase().includes(q)) ||
        (p.tags ?? []).some((t) => t.toLowerCase().includes(q));
      return matchCat && matchQuery;
    });
  }, [all, category, query]);

  const rest = filtered.filter((p) => !featured || p.slug !== featured.slug || query || category !== "All");

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero */}
      <header className="relative overflow-hidden pt-16">
        <Particles count={30} />
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute top-0 left-1/4 h-96 w-96 animate-pulse rounded-full bg-primary/10 blur-[120px]" />
          <div
            className="absolute right-1/4 bottom-0 h-80 w-80 animate-pulse rounded-full bg-secondary/10 blur-[120px]"
            style={{ animationDelay: "1s" }}
          />
        </div>

        <div className="container-hydra relative z-10 py-20 text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-accent/40 bg-accent/10 px-4 py-1.5 font-display text-xs font-bold tracking-widest text-accent uppercase">
            <Rocket size={14} /> Meme Coin Intelligence
          </span>
          <h1 className="mt-6 font-display text-4xl font-black tracking-tight text-glow md:text-6xl">
            HYDRA BLOG
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-base leading-relaxed text-muted-foreground md:text-lg">
            News, moonshot breakdowns and market analysis from the meme coin world — the tokens
            that pumped hard and turned small investors into big ones. 🐉🔥
          </p>

          <div className="mx-auto mt-8 flex max-w-xl items-center gap-2 rounded-xl border border-border bg-card/70 px-4 py-3 backdrop-blur focus-within:border-primary/60 focus-within:box-glow">
            <Search size={18} className="text-muted-foreground" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search coins, tickers or stories…"
              aria-label="Search articles"
              className="w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
            />
          </div>
        </div>
      </header>

      {/* Filters */}
      <section className="border-y border-border/50 bg-card/20">
        <div className="container-hydra flex flex-wrap items-center gap-2 py-4">
          {(["All", ...categories] as const).map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c as PostCategory | "All")}
              className={`rounded-full border px-4 py-1.5 font-display text-xs font-bold transition-all ${
                category === c
                  ? "border-primary bg-primary/15 text-primary box-glow"
                  : "border-border text-muted-foreground hover:border-primary/50 hover:text-primary"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
      </section>

      {/* Listing */}
      <main className="container-hydra py-14">
        {all.length === 0 ? (
          <EmptyState />
        ) : (
          <>
            {featured && category === "All" && !query && (
              <div className="mb-12 animate-rise-in">
                <h2 className="mb-4 font-display text-sm font-bold tracking-widest text-accent uppercase">
                  Featured
                </h2>
                <PostCard post={featured} featured />
              </div>
            )}

            <h2 className="mb-6 font-display text-sm font-bold tracking-widest text-muted-foreground uppercase">
              Latest articles
            </h2>

            {rest.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No articles match your search. Try another coin or category.
              </p>
            ) : (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {rest.map((p) => (
                  <PostCard key={p.slug} post={p} />
                ))}
              </div>
            )}
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}

function EmptyState() {
  return (
    <div className="rounded-2xl border border-dashed border-border bg-card/40 px-6 py-20 text-center">
      <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary animate-pulse-glow">
        <Rocket size={28} />
      </div>
      <h2 className="font-display text-2xl font-bold">No articles published yet</h2>
      <p className="mx-auto mt-3 max-w-lg text-sm leading-relaxed text-muted-foreground">
        The newsroom is live and waiting for content. Meme coin stories will appear here as soon
        as they are published.
      </p>
    </div>
  );
}
