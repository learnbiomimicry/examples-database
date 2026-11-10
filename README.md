# Biomimicry Examples Database

The public, filterable library of biomimicry examples at **examples.learnbiomimicry.com**, run by Learn Biomimicry.

It is a static Astro site. At build time it reads the published rows of the `biomimicry-examples` table in the Explora V.1.0 Supabase project and writes a real HTML page for:

- every example: `/<slug>/`
- every industry, interest, country and level with 2 or more examples: `/industry/materials/`, `/country/united-kingdom/`, `/level/form/`
- the filterable home page: `/` (filters are kept in the URL, so filtered views can be shared)

It also writes `sitemap-index.xml` and `robots.txt`.

## Run it locally

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # writes dist/
```

If Supabase can't be reached, the build falls back to `data/examples.snapshot.json`.

## Deploy on Cloudflare Pages

1. Cloudflare dashboard → Workers & Pages → Create → Pages → Connect to Git → pick this repository.
2. Framework preset: **Astro**. Build command: `npm run build`. Output directory: `dist`.
3. Environment variables (Production and Preview):
   - `NODE_VERSION` = `22`
   - `SUPABASE_URL` = `https://johscicbgjmvxbwlzyat.supabase.co`
   - `SUPABASE_ANON_KEY` = the project's publishable key
4. Save and deploy. Every push to `main` deploys; every other branch gets a preview link.
5. Custom domains → add `examples.learnbiomimicry.com`. If the learnbiomimicry.com zone is on Cloudflare this is one click. If DNS is at Namecheap, add a CNAME `examples` → `<project>.pages.dev`.

## Keep it fresh when examples change

The site only changes when it rebuilds. To rebuild automatically:

1. Cloudflare Pages → Settings → Builds → Deploy hooks → create one and copy the URL.
2. Supabase → Database → Webhooks → new webhook on `biomimicry-examples` (insert, update, delete) → HTTP POST to the deploy hook URL.

## Where to change things

| What | File |
| --- | --- |
| Links and call-to-action wording | `src/lib/config.js` |
| Industry and interest names, country clean-up | `src/lib/data.js` |
| Example page layout | `src/pages/[slug].astro` |
| Filter landing pages | `src/pages/[facet]/[value].astro` |
| Home page and filters | `src/pages/index.astro` |
| Header, footer, brand styles | `src/layouts/Base.astro` |
