create table if not exists analyses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  filename text,
  ats_score numeric,
  keyword_match numeric,
  missing_keywords jsonb default '[]'::jsonb,
  created_at timestamptz default now(),
  analysis_result jsonb
);
alter table analyses enable row level security;
