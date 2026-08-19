import { defineConfig } from "@lovable.dev/vite-tanstack-config";

export default defineConfig({
  base: "/blog/",
  plugins: [],
  tanstackStart: {
    server: { entry: "server" },
  },
  nitro: {
    preset: "cloudflare-module",
  },
});