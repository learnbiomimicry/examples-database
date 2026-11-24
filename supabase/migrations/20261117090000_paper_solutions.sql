-- Pilot: Nature's Solutions read straight from NASA PeTaL papers.
-- Additive only. Abstracts are never stored; only Claude's own extraction.

alter table public.mechanisms
  add column if not exists origin text not null default 'case_study'
  check (origin in ('case_study', 'paper'));

create table if not exists public.paper_passes (
  id uuid primary key default gen_random_uuid(),
  evidence_id uuid not null references public.evidence(id) on delete cascade,
  pass_no int not null,
  prompt_version text not null,
  model text not null,
  status text not null check (status in ('ok', 'refused', 'error')),
  output jsonb,
  error text,
  created_at timestamptz not null default now(),
  unique (evidence_id, pass_no, prompt_version, model)
);
alter table public.paper_passes enable row level security;

-- PeTaL's golden.json has DOIs shuffled against titles. Keep PeTaL's value,
-- then store the DOI found by title in Crossref (see scripts/explora/fix_dois.py).
alter table public.evidence add column if not exists petal_doi text;
alter table public.evidence add column if not exists doi_check text;
update public.evidence set petal_doi = doi where petal_doi is null;
