# Notes for Claude

- Owner: Alistair Daynes, Learn Biomimicry. He signs off anything public.
- Copy rules for anything written on the site: never use the em dash; write "re-" words with the RE in brackets, e.g. "(re)connect".
- Brand: Explora layout and motion with the Learn Biomimicry look. See BRAND.md for colours, fonts and motion rules.
- Data source: Supabase project "Explora V.1.0" (johscicbgjmvxbwlzyat), table `biomimicry-examples`, published rows only. Images live in the public `example-images` storage bucket; bare filenames are resolved in `src/lib/data.js`.
- The site is fully static. Don't add a server or client-side data fetching; SEO depends on every page being real HTML. One exception: `functions/api/unlock.js`, a Cloudflare Pages Function that only sets the `lb_access` cookie for the email gate. It serves no page content.
- Email gate: 3 free case studies, then name + email (`src/components/Gate.astro`). The full content stays in the HTML so search engines and AI agents read everything (the open tier in the Explora V2.0 strategy). It shares the Nature's Solutions route: the Supabase `signup` edge function (`source: "examples"`) saves to `public.signups`, then Zapier submits Kajabi's Free eBook form. Kajabi's Public API is not on our plan. Keep fields, interest keys and copy in step with the Explora gate.
- Keep filter landing pages to facets with at least 2 examples (thin pages hurt SEO).
- Calls to action (beta, Nov 2026): one main action per page, the Biomimicry Practitioner Programme, and one quieter second option, the Short Course Set. Never add a third button-weight choice. A programmes band (Short Course Set, Practitioner, Educator) sits above the footer on every page. Explora appears only in the footer.
- Dates, links and prices live in `src/lib/config.js` (OFFERS, EVENTS, BETA). Date-aware messages use `win()` / `steps()` from `src/lib/timely.js` and switch on their own; preview any date with `?now=2027-01-15`.
- More copy rules: no all caps (including labels and buttons), no abbreviations, British spelling, "Programme" not "Program".
- Analytics: GA4 (G-91160H2ZSM). Give every new call to action a `data-track="<page>-<block>"` label; Base.astro sends a `cta_click` event with location and destination.
- Newsletter links carry `?from=livingloop`, which unlocks the email limit for that browser.
- Workflow: work on a branch, check the Cloudflare Pages preview link, then merge to `main`.
