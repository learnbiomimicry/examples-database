# Notes for Claude

- Owner: Alistair Daynes, Learn Biomimicry. He signs off anything public.
- Copy rules for anything written on the site: never use the em dash; write "re-" words with the RE in brackets, e.g. "(re)connect".
- Brand: Explora layout and motion with the Learn Biomimicry look. See BRAND.md for colours, fonts and motion rules.
- Data source: Supabase project "Explora V.1.0" (johscicbgjmvxbwlzyat), table `biomimicry-examples`, published rows only. Images live in the public `example-images` storage bucket; bare filenames are resolved in `src/lib/data.js`.
- The site is fully static. Don't add a server or client-side data fetching; SEO depends on every page being real HTML.
- Keep filter landing pages to facets with at least 2 examples (thin pages hurt SEO).
- Two calls to action on every page: the Field Guide eBook (learners) and the Biomimicry Opportunity Map on explora.network (R&D teams).
- Workflow: work on a branch, check the Cloudflare Pages preview link, then merge to `main`.
