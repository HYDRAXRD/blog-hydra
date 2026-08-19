import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { ArrowLeft, Clock } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Particles from "@/components/Particles";
import PostCard from "@/components/PostCard";
import Comments from "@/components/Comments";
import { formatDate, getPostBySlug, getRelatedPosts } from "@/data/posts";
import { SITE_URL, SITE_NAME } from "@/lib/siteConfig";

export const Route = createFileRoute("/$slug")({
  loader: ({ params }) => {
    const post = getPostBySlug(params.slug);
    if (!post) throw notFound();
    return { post };
  },
  head: ({ params, loaderData }) => {
    if (!loaderData) {
      return {
        meta: [
          { title: `Article not found — ${SITE_NAME}` },
          { name: "robots", content: "noindex" },
        ],
      };
    }
    const { post } = loaderData;
    const canonicalUrl = `${SITE_URL}/blog/${params.slug}`;
    const ogImage = post.coverImage?.startsWith("https://") ? post.coverImage : undefined;

    return {
      meta: [
        { title: `${post.title} — ${SITE_NAME}` },
        { name: "description", content: post.excerpt },
        { name: "robots", content: "index, follow" },
        { property: "og:type", content: "article" },
        { property: "og:url", content: canonicalUrl },
        { property: "og:title", content: post.title },
        { property: "og:description", content: post.excerpt },
        { property: "og:site_name", content: SITE_NAME },
        ...(ogImage
          ? [
              { property: "og:image", content: ogImage },
              { property: "og:image:width", content: "1200" },
              { property: "og:image:height", content: "630" },
            ]
          : []),
        { name: "twitter:card", content: "summary_large_image" },
        { name: "twitter:site", content: "@HYDRAXRD" },
        { name: "twitter:title", content: post.title },
        { name: "twitter:description", content: post.excerpt },
        ...(ogImage ? [{ name: "twitter:image", content: ogImage }] : []),
        { property: "article:published_time", content: post.date },
        { property: "article:author", content: "HYDRA" },
        { property: "article:section", content: post.category },
      ],
      links: [{ rel: "canonical", href: canonicalUrl }],
      scripts: [
        {
          type: "application/ld+json",
          children: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            headline: post.title,
            description: post.excerpt,
            datePublished: post.date,
            dateModified: post.date,
            url: canonicalUrl,
            author: {
              "@type": "Person",
              name: post.author,
              url: SITE_URL,
            },
            publisher: {
              "@type": "Organization",
              name: "HYDRA",
              url: SITE_URL,
              logo: {
                "@type": "ImageObject",
                url: `${SITE_URL}/favicon.png`,
              },
            },
            mainEntityOfPage: canonicalUrl,
            ...(ogImage ? { image: { "@type": "ImageObject", url: ogImage, width: 1200, height: 630 } } : {}),
          }),
        },
      ],
    };
  },
  notFoundComponent: ArticleNotFound,
  component: ArticlePage,
});

function ArticleShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      {children}
      <Footer />
    </div>
  );
}

function ArticleNotFound() {
  return (
    <ArticleShell>
      <main className="container-hydra flex min-h-[60vh] flex-col items-center justify-center pt-24 text-center">
        <h1 className="font-display text-3xl font-bold text-glow">Article not found</h1>
        <p className="mt-3 text-sm text-muted-foreground">
          This story doesn't exist or hasn't been published yet.
        </p>
        <Link
          to="/"
          className="mt-6 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-primary-foreground transition-opacity hover:opacity-90"
        >
          <ArrowLeft size={16} /> Back to the blog
        </Link>
      </main>
    </ArticleShell>
  );
}

function ArticlePage() {
  const { post } = Route.useLoaderData();
  const related = getRelatedPosts(post);

  return (
    <ArticleShell>
      <header className="relative overflow-hidden pt-16">
        <Particles count={18} />
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute top-0 left-1/3 h-80 w-80 animate-pulse rounded-full bg-primary/10 blur-[120px]" />
        </div>
        <div className="container-hydra relative z-10 max-w-3xl py-14">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-xs font-medium text-muted-foreground transition-colors hover:text-primary"
          >
            <ArrowLeft size={14} /> All articles
          </Link>

          <div className="mt-6 flex flex-wrap items-center gap-2 text-xs">
            <span className="rounded-full border border-primary/40 bg-primary/10 px-3 py-1 font-display font-bold text-primary">
              {post.category}
            </span>
            {post.tickers?.map((t) => (
              <span
                key={t}
                className="rounded-full border border-accent/40 bg-accent/10 px-2.5 py-1 font-display text-accent"
              >
                ${t}
              </span>
            ))}
          </div>

          <h1 className="mt-5 font-display text-3xl leading-tight font-black md:text-5xl">
            {post.title}
          </h1>
          <p className="mt-4 text-base leading-relaxed text-muted-foreground">{post.excerpt}</p>

          <div className="mt-5 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
            <span>{post.author}</span>
            <span className="opacity-40">•</span>
            <span>{formatDate(post.date)}</span>
            <span className="opacity-40">•</span>
            <span className="inline-flex items-center gap-1">
              <Clock size={12} /> {post.readingMinutes} min read
            </span>
          </div>
        </div>
      </header>

      {post.coverImage && (
        <div className="container-hydra max-w-4xl">
          <img
            src={post.coverImage}
            alt={post.title}
            className="w-full rounded-2xl border border-border/60 object-cover box-glow"
            loading="lazy"
            width={1200}
            height={630}
          />
        </div>
      )}

      <main className="container-hydra max-w-3xl py-12">
        <div
          className="prose-hydra space-y-5 text-base leading-relaxed text-foreground/90 [&_a]:text-primary [&_a:hover]:underline [&_blockquote]:border-l-2 [&_blockquote]:border-accent [&_blockquote]:pl-4 [&_blockquote]:text-muted-foreground [&_h2]:mt-10 [&_h2]:font-display [&_h2]:text-2xl [&_h2]:font-bold [&_h3]:mt-8 [&_h3]:font-display [&_h3]:text-xl [&_h3]:font-bold [&_li]:ml-5 [&_li]:list-disc [&_strong]:text-foreground"
          dangerouslySetInnerHTML={{ __html: post.contentHtml }}
        />

        {post.tags && post.tags.length > 0 && (
          <div className="mt-10 flex flex-wrap gap-2 border-t border-border/50 pt-6">
            {post.tags.map((t) => (
              <span
                key={t}
                className="rounded-full border border-border bg-muted/40 px-3 py-1 text-xs text-muted-foreground"
              >
                #{t}
              </span>
            ))}
          </div>
        )}

        <Comments slug={post.slug} />
      </main>

      {related.length > 0 && (
        <section className="container-hydra pb-16">
          <h2 className="mb-6 font-display text-sm font-bold tracking-widest text-muted-foreground uppercase">
            Related stories
          </h2>
          <div className="grid gap-6 md:grid-cols-3">
            {related.map((p) => (
              <PostCard key={p.slug} post={p} />
            ))}
          </div>
        </section>
      )}
    </ArticleShell>
  );
}
