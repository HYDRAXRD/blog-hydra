/**
 * HYDRA Blog — memecoin news content store.
 *
 * Articles are NOT written by hand here. An external generation tool appends
 * objects to the `posts` array below (or replaces the whole file), keeping the
 * exact `Post` shape. Everything in the UI (listing, filters, featured slot,
 * article page, related posts) is derived from this data.
 *
 * Content language: English.
 */

export type PostCategory =
  | "News"
  | "Moonshots"
  | "Market Analysis"
  | "Case Studies"
  | "Guides";

export interface Post {
  /** URL slug, e.g. "dogecoin-2021-run" -> /blog/dogecoin-2021-run */
  slug: string;
  title: string;
  /** 1-2 sentence summary used on cards and meta description. */
  excerpt: string;
  category: PostCategory;
  /** ISO date string, e.g. "2026-08-19". */
  date: string;
  author: string;
  /** Estimated reading time in minutes. */
  readingMinutes: number;
  /** Absolute https URL for the cover image (optional). */
  coverImage?: string;
  /** Ticker symbols covered, e.g. ["DOGE", "PEPE"]. */
  tickers?: string[];
  tags?: string[];
  /** Show in the big featured slot at the top of /blog. */
  featured?: boolean;
  /** Article body as HTML (headings, paragraphs, lists, blockquotes). */
  contentHtml: string;
}

export const categories: PostCategory[] = [
  "News",
  "Moonshots",
  "Market Analysis",
  "Case Studies",
  "Guides",
];

/** Populated by the article generation tool. */
export const posts: Post[] = [];

export const sortedPosts = (): Post[] =>
  [...posts].sort((a, b) => (a.date < b.date ? 1 : -1));

export const getPostBySlug = (slug: string): Post | undefined =>
  posts.find((p) => p.slug === slug);

export const getFeaturedPost = (): Post | undefined =>
  sortedPosts().find((p) => p.featured) ?? sortedPosts()[0];

export const getRelatedPosts = (post: Post, limit = 3): Post[] =>
  sortedPosts()
    .filter((p) => p.slug !== post.slug)
    .sort((a, b) => Number(b.category === post.category) - Number(a.category === post.category))
    .slice(0, limit);

export const formatDate = (iso: string): string => {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};
