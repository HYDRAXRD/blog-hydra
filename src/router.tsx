import { QueryClient } from "@tanstack/react-query";
import { createRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

export const getRouter = () => {
  const queryClient = new QueryClient();

  const router = createRouter({
    routeTree,
    context: { queryClient },
    scrollRestoration: true,
    defaultPreloadStaleTime: 0,
    // Prevents Cloudflare 404s caused by trailing-slash mismatches.
    // /blog/ -> /blog, /blog/slug/ -> /blog/slug
    trailingSlash: "never",
  });

  return router;
};
