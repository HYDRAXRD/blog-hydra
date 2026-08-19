import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  vite: {
    base: "/blog/", 
  },
  plugins: [],
  tanstackStart: {
    server: { entry: "server" },
  },
  nitro: {
    preset: "cloudflare-module",
    baseURL: "/blog", 
  },
});