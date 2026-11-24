-- Email sign-ups from Explora (Nature's Solutions) and, later, the examples site.
-- Supabase is the source of truth; each row is copied to Kajabi while it is the CRM.
create table if not exists public.signups (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  name text not null,
  interest text not null,
  source text not null default 'natures-solutions',
  viewed text[] not null default '{}',
  consent boolean not null default false,
  kajabi_status text not null default 'pending'
    check (kajabi_status in ('pending', 'sent', 'error', 'skipped')),
  kajabi_error text,
  kajabi_sent_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists signups_email_source_key
  on public.signups (lower(email), source);

-- Only the signup edge function (service role) reads or writes this table.
alter table public.signups enable row level security;
