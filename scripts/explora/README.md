# Explora data scripts (build days 1 to 2, plus the paper pilot)

In everything learners see, a mechanism is called a **Nature's Solution**. The database table keeps the name `mechanisms`.

These scripts enrich every case study in Supabase. Supabase stays the one source of truth. They only add rows to the new Explora tables; they never change `biomimicry-examples`.

## Set up once

1. Add these to `.env` in the repo root (it is git-ignored):

   ```
   ANTHROPIC_API_KEY=...
   SUPABASE_URL=https://johscicbgjmvxbwlzyat.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=...
   ```

   The service role key is in Supabase: Project Settings, API keys. Keep it secret.

2. Install:

   ```bash
   python3 -m venv .venv && .venv/bin/pip install -r scripts/explora/requirements.txt
   ```

## Run, in this order

| Step | Command | What it does |
| --- | --- | --- |
| 1 | `supabase/migrations/20261116100000_explora_v1_data_model.sql` | New tables (already applied on 16 Nov 2026) |
| 2 | `.venv/bin/python scripts/explora/import_petal.py --load golden.json` | Loads 1,424 NASA PeTaL papers: DOI, title, function labels, species. No abstracts |
| 3 | `.venv/bin/python scripts/explora/enrich.py --limit 5` then without `--limit` | Two Claude passes per case study, then agreement |
| 4 | `.venv/bin/python scripts/explora/confidence.py` | Links papers to mechanisms, then sets High, Medium or Low with reasons |
| 5 | `.venv/bin/python scripts/explora/export_spotcheck.py 10` | Writes `explora-spotcheck.md` |
| 6 | `supabase/migrations/20261117090000_paper_solutions.sql` | Adds `mechanisms.origin`, `paper_passes`, `evidence.petal_doi` and `doi_check` (applied 17 Nov 2026) |
| 7 | `.venv/bin/python scripts/explora/fix_dois.py` | PeTaL's DOIs are shuffled against its titles. Finds the right DOI for each title in Crossref |
| 8 | `.venv/bin/python scripts/explora/extract_papers.py golden.json --limit 10` then without `--limit` | Reads each paper's abstract twice and saves a Nature's Solution when it describes one (`origin = 'paper'`, unpublished) |
| 9 | `.venv/bin/python scripts/explora/extract_papers.py golden.json --compare claude-fable-5-2 --sample 30` | One pass each from Opus and Fable on the same papers, for a side by side check |
| 10 | `.venv/bin/python scripts/explora/confidence.py` again | Scores the new research solutions too |
| 11 | `python3 scripts/explora/visuals/make_visuals.py --save` | Saves the hand-drawn SVG illustrations to `mechanisms.visual_svg` |
| 12 | `.venv/bin/python scripts/explora/demo_site.py --embed --artifact` | Builds the private demo in `demo/` |

`golden.json` comes from github.com/nasa-petal/data-collection-and-prep and the taxonomy from github.com/nasa-petal/PeTaL-labeller (both The Unlicense, public domain). Credit: NASA PeTaL project, NASA Glenn Research Center.

## How the parts work

- **Two passes.** Each case study is sent to Claude twice, as separate requests. Claude never sees the hand scores. The passes agree when the organism matches (same genus or common name), the functions overlap (same function or same PeTaL family), and a third short request judges the two mechanism descriptions to be the same. Score gaps are stored too.
- **Life-friendly score.** Five criteria, 1 to 6 each, out of 30. The stored score is the mean of the two passes. `lf_vs_existing` holds the gap from the hand scores.
- **Confidence.** Fixed rules in `confidence.py` (see the top of that file). A record is High only if the two passes agree. Patent points come on day 3.
- **Two layers.** Proven solutions come from a case study (a product exists). Researched solutions come straight from a paper; nobody has built them yet in our records, so they top out at Medium confidence.
- **PeTaL data quality.** In `golden.json` the title, abstract and species line up, but the DOI, URL and some function labels belong to other papers. Treat PeTaL's function labels as hints, not truth. Abstracts are read from the file and never stored.
- **Paper links.** A NASA PeTaL paper links to a mechanism when its species list names the mechanism's organism (or the same genus). `match_reason` says which.

Safe to stop and run again: stored passes are reused. A new `PROMPT_VERSION` in `enrich.py` starts fresh passes.

## Email sign-up gate (Nature's Solutions)

- Visitors read 3 solutions free. Opening a 4th new one shows a sign-up box (name, email, field, consent). Solutions already seen stay open. Counting lives in the browser (`localStorage`), so the pages stay fully static and every page keeps its full HTML for search engines.
- The form posts to the Supabase edge function `signup` (`supabase/functions/signup/index.ts`), which:
  1. saves the person in `public.signups` (the source of truth, migration `20261118090000_signups.sql`), then
  2. submits Kajabi's "Free eBook Funnel - Lead Capture" form (id 2147692554) with name, email and Area of Interest (`custom_52`). The existing Kajabi automations then send the eBook sequence for that interest and add the interest tags. No Kajabi automation was changed.
  3. adds the Kajabi tag "Lead - Explora" (id 2150461944) so Explora leads can be found.
- Kajabi keys live only in Supabase secrets: `KAJABI_CLIENT_ID` and `KAJABI_CLIENT_SECRET` (a Kajabi User API Key, Settings > Security). Without them, sign-ups are saved with `kajabi_status = 'pending'` and can be resent later.
- Check the list: `select name, email, interest, kajabi_status, kajabi_error, created_at from signups order by created_at desc;`
- When moving off Kajabi, change only `sendToKajabi` in the function; the list stays in Supabase.

**Update (18 Nov 2026):** Kajabi's Public API is not on our plan (token returns 403). The `signup` function now posts each sign-up to a Zapier webhook instead. The Zap "Explora sign-up to Kajabi eBook form" (https://zapier.com/workflow/01a1ee52-9fcc-7778-8743-d15c596819b5) submits the Free eBook form (2147692554) with name, email and Area of Interest. The KAJABI_CLIENT_ID / KAJABI_CLIENT_SECRET secrets are no longer used. The "Lead - Explora" tag is not added on this route; the `source` column in `signups` records where each person came from.
