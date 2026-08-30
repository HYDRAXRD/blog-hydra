/**
 * HYDRA Blog — memecoin news content store.
 *
 * Articles are NOT written by hand here. The generation tool (GitHub Action)
 * drops one JSON file per article into `src/data/posts/*.json` and this module
 * loads every one of them automatically at build time.
 *
 * Content language: English.
 */

import { markdownToHtml } from "@/lib/markdown";

/** Free-form category coming from the generator (e.g. "Memecoin", "News"). */
export type PostCategory = string;

/** Raw shape written by the generation tool into src/data/posts/*.json */
export interface RawPost {
  id?: string;
  slug: string;
  title: string;
  excerpt: string;
  /** Article body in Markdown. */
  content: string;
  category?: string;
  author?: string;
  /** ISO date string, e.g. "2026-08-19" or "2026-08-30T15:09:00Z". */
  date: string;
  readingTime?: number;
  featured?: boolean;
  coverImage?: string;
  tags?: string[];
  tickers?: string[];
}

export interface Post {
  slug: string;
  title: string;
  excerpt: string;
  category: PostCategory;
  date: string;
  author: string;
  readingMinutes: number;
  coverImage?: string;
  tickers?: string[];
  tags?: string[];
  featured?: boolean;
  /** Article body rendered as HTML. */
  contentHtml: string;
}

const estimateReadingMinutes = (content: string): number =>
  Math.max(1, Math.ceil(content.trim().split(/\s+/).length / 200));

const toPost = (raw: RawPost): Post => ({
  slug: raw.slug,
  title: raw.title,
  excerpt: raw.excerpt,
  category: raw.category?.trim() || "News",
  date: raw.date,
  author: raw.author?.trim() || "HYDRA",
  readingMinutes: raw.readingTime ?? estimateReadingMinutes(raw.content ?? ""),
  ...(raw.coverImage ? { coverImage: raw.coverImage } : {}),
  ...(raw.tickers?.length ? { tickers: raw.tickers } : {}),
  ...(raw.tags?.length ? { tags: raw.tags } : {}),
  ...(raw.featured ? { featured: true } : {}),
  contentHtml: markdownToHtml(raw.content ?? ""),
});

// Auto-detects every JSON article in the posts folder at build time.
const postModules = import.meta.glob("./posts/*.json", { eager: true }) as Record<
  string,
  { default: RawPost }
>;

export const posts: Post[] = Object.values(postModules)
  .map((m) => m.default)
  .filter((raw) => Boolean(raw?.slug && raw?.title))
  .map(toPost);

/**
 * Sort posts newest-first.
 * Primary key  : date string (ISO date or ISO datetime — lexicographic DESC).
 * Secondary key: slug DESC — acts as a stable tiebreaker because the
 *   generator appends an hour-based suffix (e.g. "-1508") when deduplicating,
 *   so a later post in the same day will sort correctly after the earlier one.
 * Tertiary key : title ASC — final stable fallback for truly identical dates.
 *
 * Guard: posts with a missing or invalid date are treated as "1970-01-01"
 * so they sink to the bottom rather than causing NaN comparisons.
 */
const safeDateKey = (date: string): string => {
  if (!date || typeof date !== "string") return "1970-01-01";
  const d = new Date(date);
  return Number.isNaN(d.getTime()) ? "1970-01-01" : date;
};

export const sortedPosts = (): Post[] =>
  [...posts].sort((a, b) => {
    const da = safeDateKey(a.date);
    const db = safeDateKey(b.date);
    if (da !== db) return da < db ? 1 : -1;          // newest date first
    if (a.slug !== b.slug) return a.slug < b.slug ? 1 : -1; // later slug first
    return a.title < b.title ? -1 : 1;               // alphabetical title fallback
  });

/** Categories actually present in the content, for the filter bar. */
export const categories: PostCategory[] = Array.from(
  new Set(posts.map((p) => p.category)),
).sort();

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
