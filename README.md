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

## Email gate

Visitors read 3 case studies in full, then a card asks them to join free: name, email, their field and an email-consent tick. Every case study then stays open on that device. The full text is always in the HTML, so search engines and AI agents are never gated.

It shares one route with the Nature's Solutions gate in Explora:

1. The browser posts to the Supabase edge function `signup` (in the Explora repo) with `source: "examples"`.
2. The function saves the person in `public.signups`, then sends them to a Zapier webhook.
3. The Zap submits Kajabi's "Free eBook Funnel - Lead Capture" form, so the existing automations send the eBook sequence for their field and add the interest tags.

Files here:

- `src/components/Gate.astro`: the card, the counting and the form, in the browser.
- `functions/api/unlock.js`: a Cloudflare Pages Function that only sets a two-year `lb_access` cookie on `.learnbiomimicry.com`. Safari clears script-set storage after 7 days without a visit; it keeps this cookie, and other Learn Biomimicry subdomains can read it.
- "Already joined?" unlocks a new device with just an email. Links in Kajabi emails can add `?access=lb` to any examples URL to unlock that device without the form.
- The interest keys in `src/lib/config.js` must match the `INTERESTS` map in the `signup` function.
