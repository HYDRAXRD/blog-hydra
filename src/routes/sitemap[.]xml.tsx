import { createAPIFileRoute } from "@tanstack/react-start/api";
import { sortedPosts } from "@/data/posts";
import { SITE_URL } from "@/lib/siteConfig";

export const APIRoute = createAPIFileRoute("/sitemap.xml")({
  GET: () => {
    const posts = sortedPosts();

    type SitemapEntry = {
      url: string;
      priority: string;
      changefreq: string;
      lastmod?: string;
    };

    const staticPages: SitemapEntry[] = [
      { url: `${SITE_URL}/`, priority: "1.0", changefreq: "daily" },
      { url: `${SITE_URL}/blog`, priority: "0.9", changefreq: "hourly" },
    ];

    const postPages = posts.map((p) => ({
      url: `${SITE_URL}/blog/${p.slug}`,
      lastmod: p.date,
      priority: "0.8",
      changefreq: "weekly",
    }));

    const allPages = [...staticPages, ...postPages];

    const xml = [
      `<?xml version="1.0" encoding="UTF-8"?>`,
      `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">`,
      ...allPages.map(
        (p) =>
          `  <url>\n    <loc>${p.url}</loc>${p.lastmod ? `\n    <lastmod>${p.lastmod}</lastmod>` : ""}\n    <changefreq>${p.changefreq}</changefreq>\n    <priority>${p.priority}</priority>\n  </url>`
      ),
      `</urlset>`,
    ].join("\n");

    return new Response(xml, {
      headers: {
        "Content-Type": "application/xml; charset=utf-8",
        "Cache-Control": "public, max-age=3600",
      },
    });
  },
});
