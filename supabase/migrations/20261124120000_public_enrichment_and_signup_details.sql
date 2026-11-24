-- Nature's Solutions site (explora.learnbiomimicry.com) builds with the public key,
-- so it needs to read the scores for published solutions from published case studies.
create policy "Public read published enrichment" on public.case_study_enrichment
  for select to anon, authenticated using (
    exists (select 1 from public.mechanisms m where m.id = case_study_enrichment.mechanism_id and m.published)
    and exists (select 1 from public."biomimicry-examples" e where e.id = case_study_enrichment.case_study_id and e.published));

-- Extra fields from the company pilot form (company, role, challenge).
alter table public.signups add column if not exists details jsonb;
