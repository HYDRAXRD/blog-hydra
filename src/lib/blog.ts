/**
 * HYDRA Blog Engine
 * Automatically loads all posts from src/data/posts/*.json
 * To publish a new post: just create a new .json file in that folder.
 */

export interface BlogPost {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  category: string;
  author: string;
  date: string;
  readingTime: number;
  featured: boolean;
  coverImage: string;
  tags: string[];
}

// Vite glob import — auto-detects ALL JSON files in the posts folder
const postModules = import.meta.glob('../data/posts/*.json', {
  eager: true,
}) as Record<string, { default: BlogPost }>;

function loadAllPosts(): BlogPost[] {
  return Object.values(postModules)
    .map((mod) => mod.default)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}

export const allPosts: BlogPost[] = loadAllPosts();

export const featuredPost: BlogPost | undefined = allPosts.find((p) => p.featured);

export const latestPosts: BlogPost[] = allPosts.filter((p) => !p.featured);

export function getPostBySlug(slug: string): BlogPost | undefined {
  return allPosts.find((p) => p.slug === slug);
}

export function getPostsByCategory(category: string): BlogPost[] {
  if (category === 'All Posts') return allPosts;
  return allPosts.filter((p) => p.category === category);
}

export const categories = [
  'All Posts',
  'News',
  'Ecosystem',
  'Community',
  'Game Updates',
  'Guides',
  'Announcements',
];

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function estimateReadingTime(content: string): number {
  const words = content.trim().split(/\s+/).length;
  return Math.max(1, Math.ceil(words / 200));
}
