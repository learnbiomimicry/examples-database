-- Explora V1 data model (build brief, days 1 to 2).
-- Additive only: new tables, no change to existing tables or columns.
-- The mechanism is the centre: case studies, organisms, functions, papers,
-- patents and opportunities all hang off a mechanism.
-- RLS is on for every table with no public policies yet, so only the
-- service role can read or write. Add read policies when the site needs them.

-- Functions: NASA PeTaL biomimicry taxonomy (three levels).
create table public.functions (
  id          uuid primary key default gen_random_uuid(),
  slug        text not null unique,
  name        text not null,
  level       smallint not null check (level between 1 and 3),
  parent_id   uuid references public.functions(id),
  source      text not null default 'nasa-petal',
  created_at  timestamptz not null default now()
);
comment on table public.functions is 'Function taxonomy. Adopted from NASA PeTaL (public domain, The Unlicense). Credit: NASA Glenn Research Center, PeTaL project.';

-- Organisms.
create table public.organisms (
  id               uuid primary key default gen_random_uuid(),
  slug             text not null unique,
  scientific_name  text,
  common_name      text,
  habitat          text,
  photo_url        text,
  photo_credit     text,
  photo_licence    text,
  gbif_key         bigint,
  gbif_url         text,
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);

-- Mechanisms.
create table public.mechanisms (
  id                       uuid primary key default gen_random_uuid(),
  slug                     text not null unique,
  name                     text not null,
  summary                  text,
  how_it_works             jsonb,           -- ["step 1", "step 2", "step 3"]
  visual_svg               text,
  -- Life-friendly score: five criteria, 1 to 6 each, total out of 30.
  lf_biomimicry_link       numeric check (lf_biomimicry_link between 1 and 6),
  lf_ease_of_application   numeric check (lf_ease_of_application between 1 and 6),
  lf_wide_applicability    numeric check (lf_wide_applicability between 1 and 6),
  lf_life_friendly_fit     numeric check (lf_life_friendly_fit between 1 and 6),
  lf_benefit_to_humanity   numeric check (lf_benefit_to_humanity between 1 and 6),
  lf_total                 numeric generated always as (
    lf_biomimicry_link + lf_ease_of_application + lf_wide_applicability
    + lf_life_friendly_fit + lf_benefit_to_humanity) stored,
  -- Confidence score: how sure we are it works.
  confidence_level         text check (confidence_level in ('High','Medium','Low')),
  confidence_points        integer,
  confidence_reasons       jsonb,           -- ["reason", ...]
  passes_agree             boolean,
  -- Opportunity status: set by rules from the patent layer (day 3).
  opportunity_status       text check (opportunity_status in ('Open','Free to use','Proven')),
  opportunity_note         text,
  published                boolean not null default false,
  created_at               timestamptz not null default now(),
  updated_at               timestamptz not null default now()
);

create table public.mechanism_functions (
  mechanism_id uuid not null references public.mechanisms(id) on delete cascade,
  function_id  uuid not null references public.functions(id),
  primary key (mechanism_id, function_id)
);

create table public.mechanism_organisms (
  mechanism_id uuid not null references public.mechanisms(id) on delete cascade,
  organism_id  uuid not null references public.organisms(id),
  primary key (mechanism_id, organism_id)
);

-- Link from existing case studies (biomimicry-examples) to mechanisms.
create table public.case_study_mechanisms (
  case_study_id uuid not null references public."biomimicry-examples"(id) on delete cascade,
  mechanism_id  uuid not null references public.mechanisms(id) on delete cascade,
  primary key (case_study_id, mechanism_id)
);

-- AI enrichment: each independent pass stored raw, plus the agreed result.
create table public.enrichment_passes (
  id              uuid primary key default gen_random_uuid(),
  case_study_id   uuid not null references public."biomimicry-examples"(id) on delete cascade,
  pass_no         smallint not null check (pass_no in (1,2)),
  prompt_version  text not null,
  model           text not null,
  status          text not null check (status in ('ok','refused','error')),
  output          jsonb,
  error           text,
  created_at      timestamptz not null default now(),
  unique (case_study_id, pass_no, prompt_version)
);

create table public.case_study_enrichment (
  case_study_id         uuid primary key references public."biomimicry-examples"(id) on delete cascade,
  prompt_version        text not null,
  mechanism_id          uuid references public.mechanisms(id),
  maturity              text check (maturity in ('lab','pilot','on market','concept')),
  passes_agree          boolean,
  agreement             jsonb,   -- per field: organism, functions, mechanism, scores
  lf_biomimicry_link       numeric,
  lf_ease_of_application   numeric,
  lf_wide_applicability    numeric,
  lf_life_friendly_fit     numeric,
  lf_benefit_to_humanity   numeric,
  lf_total                 numeric,
  lf_vs_existing           jsonb,  -- difference from the existing hand scores
  confidence_level      text check (confidence_level in ('High','Medium','Low')),
  confidence_points     integer,
  confidence_reasons    jsonb,
  updated_at            timestamptz not null default now()
);

-- Evidence: papers (NASA PeTaL first; OpenAlex later). DOIs, titles and
-- labels only. Never abstracts: publishers own those.
create table public.evidence (
  id             uuid primary key default gen_random_uuid(),
  source         text not null,                 -- 'nasa-petal', 'openalex'
  source_id      text,                          -- e.g. OpenAlex work id
  doi            text,
  title          text,
  url            text,
  function_labels text[],                       -- PeTaL level 3 (or 2) labels
  species        text[],
  credit         text,
  licence        text,
  created_at     timestamptz not null default now(),
  unique (source, doi)
);
comment on table public.evidence is 'Paper evidence. NASA PeTaL labels from github.com/nasa-petal/data-collection-and-prep (golden.json, The Unlicense). Credit: NASA PeTaL project. No abstracts stored.';

create table public.evidence_functions (
  evidence_id uuid not null references public.evidence(id) on delete cascade,
  function_id uuid not null references public.functions(id),
  primary key (evidence_id, function_id)
);

create table public.mechanism_evidence (
  mechanism_id uuid not null references public.mechanisms(id) on delete cascade,
  evidence_id  uuid not null references public.evidence(id) on delete cascade,
  match_reason text,             -- how the link was made
  primary key (mechanism_id, evidence_id)
);

-- Patents (filled on day 3).
create table public.patents (
  id            uuid primary key default gen_random_uuid(),
  number        text not null unique,
  title         text,
  owner         text,
  filing_date   date,
  status        text check (status in ('active','expired','lapsed','pending','unknown')),
  jurisdiction  text,
  family_id     text,
  link          text,
  source        text,           -- 'lens', 'epo', 'uspto'
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

create table public.mechanism_patents (
  mechanism_id uuid not null references public.mechanisms(id) on delete cascade,
  patent_id    uuid not null references public.patents(id) on delete cascade,
  passes_agree boolean,
  confidence   text check (confidence in ('High','Medium','Low')),
  primary key (mechanism_id, patent_id)
);

-- Opportunities.
create table public.opportunities (
  id             uuid primary key default gen_random_uuid(),
  mechanism_id   uuid not null references public.mechanisms(id) on delete cascade,
  gap_type       text,
  why_open       text,
  who_might_care text,
  next_step      text,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

-- Problem finder: problems and their root cause chains.
create table public.problems (
  id               uuid primary key default gen_random_uuid(),
  user_id          uuid references auth.users(id) on delete cascade,
  title            text not null,
  who_has_it       text,
  how_often        text,
  how_painful      text,
  evidence         text,
  need_answer      text check (need_answer in ('Strong','Some','Weak')),   -- Do people badly need this?
  fit_answer       text check (fit_answer in ('Strong','Some','Weak')),    -- Are you the right person?
  nature_answer    text check (nature_answer in ('Strong','Some','Weak')), -- Can nature help?
  created_at       timestamptz not null default now(),
  updated_at       timestamptz not null default now()
);

create table public.root_causes (
  id           uuid primary key default gen_random_uuid(),
  problem_id   uuid not null references public.problems(id) on delete cascade,
  step_no      smallint not null,
  why_text     text not null,
  function_id  uuid references public.functions(id),  -- set on the last step
  created_at   timestamptz not null default now(),
  unique (problem_id, step_no)
);

-- Indexes for foreign keys used in joins.
create index on public.functions (parent_id);
create index on public.mechanism_functions (function_id);
create index on public.mechanism_organisms (organism_id);
create index on public.case_study_mechanisms (mechanism_id);
create index on public.enrichment_passes (case_study_id);
create index on public.case_study_enrichment (mechanism_id);
create index on public.evidence_functions (function_id);
create index on public.mechanism_evidence (evidence_id);
create index on public.mechanism_patents (patent_id);
create index on public.opportunities (mechanism_id);
create index on public.problems (user_id);
create index on public.root_causes (function_id);
create index on public.evidence using gin (species);

alter table public.functions             enable row level security;
alter table public.organisms             enable row level security;
alter table public.mechanisms            enable row level security;
alter table public.mechanism_functions   enable row level security;
alter table public.mechanism_organisms   enable row level security;
alter table public.case_study_mechanisms enable row level security;
alter table public.enrichment_passes     enable row level security;
alter table public.case_study_enrichment enable row level security;
alter table public.evidence              enable row level security;
alter table public.evidence_functions    enable row level security;
alter table public.mechanism_evidence    enable row level security;
alter table public.patents               enable row level security;
alter table public.mechanism_patents     enable row level security;
alter table public.opportunities         enable row level security;
alter table public.problems              enable row level security;
alter table public.root_causes           enable row level security;
