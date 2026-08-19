import { Link } from "@tanstack/react-router";
import { Clock, TrendingUp } from "lucide-react";
import { formatDate, type Post } from "@/data/posts";

const PostCard = ({ post, featured = false }: { post: Post; featured?: boolean }) => {
  return (
    <article
      className={`group relative overflow-hidden rounded-xl border border-border/60 bg-card/60 backdrop-blur transition-all hover:-translate-y-1 hover:border-primary/50 hover:box-glow ${
        featured ? "md:grid md:grid-cols-2" : ""
      }`}
    >
      <div className={`relative overflow-hidden bg-muted ${featured ? "h-full min-h-56" : "h-44"}`}>
        {post.coverImage ? (
          <img
            src={post.coverImage}
            alt={post.title}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-primary/20 via-secondary/15 to-accent/20">
            <TrendingUp className="h-10 w-10 text-primary" />
          </div>
        )}
      </div>

      <div className="flex flex-col gap-3 p-5">
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="rounded-full border border-primary/40 bg-primary/10 px-3 py-1 font-display font-bold text-primary">
            {post.category}
          </span>
          {post.tickers?.slice(0, 3).map((t) => (
            <span
              key={t}
              className="rounded-full border border-accent/40 bg-accent/10 px-2.5 py-1 font-display text-accent"
            >
              ${t}
            </span>
          ))}
        </div>

        <h3
          className={`font-display font-bold leading-snug transition-colors group-hover:text-primary ${
            featured ? "text-2xl md:text-3xl" : "text-lg"
          }`}
        >
          <Link to="/blog/$slug" params={{ slug: post.slug }}>
            {post.title}
          </Link>
        </h3>

        <p className="line-clamp-3 text-sm leading-relaxed text-muted-foreground">{post.excerpt}</p>

        <div className="mt-auto flex items-center gap-3 pt-2 text-xs text-muted-foreground">
          <span>{formatDate(post.date)}</span>
          <span className="opacity-40">•</span>
          <span className="inline-flex items-center gap-1">
            <Clock size={12} /> {post.readingMinutes} min
          </span>
          <span className="opacity-40">•</span>
          <span>{post.author}</span>
        </div>
      </div>
    </article>
  );
};

export default PostCard;
