# Brief: move the examples database to explora.network

> **Superseded on 24 Nov 2026.** The examples site does not move to explora.network; it stays at examples.learnbiomimicry.com (see `docs/STRATEGY.md`). Nature's solutions get their own static site at explora.learnbiomimicry.com.
> **Still holds:** the static site and real HTML, published rows only, the free-reads sign-up (section 6), and the two-way links between examples and solutions (section 5).
> **No longer applies:** the explora.network URL map, the domain switch and (re)directs (section 7), and `/team-sprint/`. The B2B page is now the company pilot page on examples.learnbiomimicry.com.

**For:** Claude Code, working in the `learnbiomimicry/examples-database` repo
**Owner:** Alistair Daynes, Learn Biomimicry
**Date:** 19 November 2026
**Serves:** Explora V2.0 Strategy, sections "Where Explora lives" and "Core strategy on one page"
**Read with:** `docs/STRATEGY.md`, `docs/function-first-brief.md` and `docs/website-copy.md`

Lines marked **[confirm]** need an answer from Alistair before that step starts. Only the Team Sprint copy is still open.

---

## 1. The goal in one line

Make explora.network the single public home of the open database, with case studies and nature's solutions linked to each other. Learn Biomimicry keeps the courses, blog and eBook.

## 2. Decisions already made

- Learn Biomimicry is where people learn; Explora is where they apply it.
- Brand on the site: **"Explora, by Learn Biomimicry"**.
- One Supabase project stays the single source of truth. The site keeps building from published rows only.
- The site stays fully static: every page is real HTML, with no server and no client-side data fetching for content.
- Copy rules for anything on the site: never use the em dash; bracket the "re" in a word, like "(re)connect", only where the word still reads correctly without it; no all-caps; no abbreviations; plain English.
- Agents and crawlers always read freely. The free-reads limit is for people browsing only.

## 3. Where things are today

| Thing | Today |
| --- | --- |
| Examples site | Astro, static, Cloudflare Pages, `examples.learnbiomimicry.com`, about 181 published examples |
| Example data | Supabase project "Explora V.1.0" (`johscicbgjmvxbwlzyat`), table `biomimicry-examples` |
| Nature's solutions | Supabase table `mechanisms`: 1,047 rows (185 from case studies, 862 from papers), 325 published (see 5a). Linked tables: `mechanism_functions`, `functions` (130, NASA PeTaL taxonomy), `mechanism_organisms`, `organisms`, `mechanism_evidence`, `evidence` |
| explora.network | The Lovable app, including the Opportunity Map at `/get-started`. Domain registered at Namecheap; DNS on Cloudflare |
| Links and CTAs | `src/lib/config.js`; site URL also in `astro.config.mjs` and `public/robots.txt` |

## 4. Target URL map

| URL on explora.network | What it shows | Comes from |
| --- | --- | --- |
| `/` | "How might nature help us…?" plus the "I need to…" function doors | `docs/function-first-brief.md` |
| `/solutions/<slug>/` | One nature's solution | Explora demo pages |
| `/examples/<slug>/` | One case study | Today's `/<slug>/` |
| `/examples/industry/<value>/` and other facets | Filter landing pages (2 or more examples only) | Today's `/<facet>/<value>/` |
| `/use-cases/<slug>/` | Four-step use cases, e.g. self-cleaning solar panels | New |
| `/team-sprint/` | The B2B offer | New **[confirm copy]** |
| `/connector/` | How to use Explora in Claude | Today's demo `claude.html` |

**The Lovable app:** move it to `app.explora.network` (agreed), so the static site can take the root domain. The Opportunity Map link becomes `https://app.explora.network/get-started` until it is rebuilt.

## 5. Link case studies and solutions both ways

- Each example page lists the nature's solutions it shows ("Nature's solutions in this example").
- Each solution page lists its examples as evidence ("Where this has been used").
- The link table already exists: `case_study_mechanisms (case_study_id, mechanism_id)`, with all 185 case studies linked. Solutions from papers link to evidence through `mechanism_evidence` instead.
- No orphans: every published solution links to at least one example, and the build reports any that don't.

## 5a. Publishing nature's solutions (done 19 Nov 2026)

325 nature's solutions are published: all 185 from case studies and 140 from papers with Medium confidence. The 719 Low-confidence ones from papers stay unpublished until verified. Duplicates were merged into one entry each; the extra copies stay unpublished with a note in `opportunity_note`. Anyone can now read published entries and their organisms, evidence and functions; writing stays closed.

## 6. The free-reads sign-up

- People can read 3 solution or example pages free. On the 4th, a sign-up panel asks for name, email and field.
- The page underneath is still the full HTML. The panel is a layer added in the browser, so crawlers and agents are never blocked.
- Count reads in the browser (localStorage, wrapped in try/catch). No cookies are needed for this.
- This already exists: the `signup` edge function saves to `public.signups` and sends the person through the Zap "Explora sign-up to Kajabi eBook form", which submits the Kajabi Free eBook form (2147692554). Keep using it; add any new page types to its `SOURCES` list.
- The field question must stay required: it routes leads into the right email sequence.
- Never show the panel to known bots, and never on `/connector/` or `/team-sprint/`.

## 7. Moving the domain without losing search ranking

1. Build and check everything on a Cloudflare Pages preview link first.
2. Point `explora.network` at the static site; move the Lovable app to `app.explora.network`.
3. Update `astro.config.mjs` (`site`), `src/lib/config.js` (`SITE.url`, CTA links) and `public/robots.txt` (sitemap URL).
4. Add 301 (re)directs from every old URL to its new one, path for path: `examples.learnbiomimicry.com/<slug>/` → `explora.network/examples/<slug>/`, and the same for facet pages. DNS is on Cloudflare, so use a Cloudflare redirect rule on the learnbiomimicry.com zone (or keep the old Pages project live with a `_redirects` file).
5. Set canonical URLs to explora.network on every page, and publish a new sitemap.
6. In Google Search Console, verify explora.network, submit the sitemap, and use the Change of Address tool from the examples subdomain if it's available for that property.
7. Update links on learnbiomimicry.com (navigation, blog posts, eBook emails) to the new URLs.
8. Keep the old Pages project until the (re)directs have been checked for every old URL.

## 8. Brand on the site

- Header: "Explora" with "by Learn Biomimicry" beside or under it. Footer links back to learnbiomimicry.com.
- Look and feel: follow `BRAND.md` (Learn Biomimicry colours and fonts, Explora layouts and motion).
- Two calls to action on every page, as now: the Field Guide eBook (learners) and the Opportunity Map or Team Sprint (R&D teams).
- The "Find a problem worth solving, naturally" call to action, as set out in the function-first brief.

## 9. Out of scope for this move

- The contribution flow (proposals, checks, verification). It gets its own brief.
- The patent and opportunity layer.
- A logged-in workspace. Claude is the workspace for now.

## 10. Done when

- [ ] explora.network serves the static site; the Lovable app works at `app.explora.network`
- [ ] Every old examples URL lands on its new page with a single 301
- [ ] Example and solution pages link to each other both ways, with no orphans
- [ ] The free-reads panel works for people and never blocks crawlers or agents
- [ ] Sign-ups land in Supabase and the right Kajabi sequence
- [ ] Canonicals, sitemap and Search Console are updated
- [ ] Links on learnbiomimicry.com point to the new URLs
- [ ] No em dashes anywhere in site copy

## 11. Order of work

1. URL map and page templates for `/solutions/` and `/examples/` (on a branch, preview link only)
2. Two-way links between examples and solutions
3. Home page with the function doors (from the function-first brief)
4. Free-reads panel and lead capture
5. Domain switch, (re)directs, canonicals and Search Console
6. Update links on learnbiomimicry.com

## 12. Prompt to start the session

> Read `docs/STRATEGY.md`, `docs/function-first-brief.md` and `docs/migration-brief.md`. We're moving the examples site to explora.network and joining it with the nature's solutions. Start in plan mode: list the open [confirm] questions, the files you'll change, and any Supabase changes. Then wait for my go-ahead. Work on a branch and give me the Cloudflare preview link before anything touches a live domain.
