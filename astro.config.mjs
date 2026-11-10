import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// Static site: every example and every filter page is plain HTML at build time.
export default defineConfig({
  site: "https://examples.learnbiomimicry.com",
  trailingSlash: "always",
  build: { format: "directory" },
  integrations: [sitemap()],
});
