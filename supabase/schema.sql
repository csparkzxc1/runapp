-- macaron Phase 0 schema
-- Run in Supabase Dashboard → SQL Editor.
-- Also enable Anonymous sign-ins: Auth → Providers → Anonymous → ON

-- ────────────────────────────────────────────────────────────
-- Enums
-- ────────────────────────────────────────────────────────────
do $$ begin
  create type tier_level as enum (
    'tent', 'cabin', 'yard_house', 'villa', 'apartment', 'mansion'
  );
exception
  when duplicate_object then null;
end $$;

-- ────────────────────────────────────────────────────────────
-- profiles
-- ────────────────────────────────────────────────────────────
create table if not exists public.profiles (
  id uuid references auth.users on delete cascade primary key,
  display_name text,
  macaron_balance integer default 0 not null check (macaron_balance >= 0),
  lifetime_steps bigint default 0 not null,
  current_tier tier_level default 'tent' not null,
  created_at timestamp default now() not null,
  updated_at timestamp default now() not null
);

-- ────────────────────────────────────────────────────────────
-- daily_activity (one row per user per day, upserted)
-- ────────────────────────────────────────────────────────────
create table if not exists public.daily_activity (
  id bigserial primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  activity_date date not null,
  steps integer default 0 not null,
  flights_climbed integer default 0 not null,
  distance_meters double precision default 0 not null,
  macaron_earned integer default 0 not null,
  milestones_granted text[] default '{}' not null,
  ads_watched integer default 0 not null,
  attendance_claimed boolean default false not null,
  source text not null default 'healthkit',
  created_at timestamp default now() not null,
  updated_at timestamp default now() not null,
  unique (user_id, activity_date)
);

create index if not exists daily_activity_user_date_idx
  on public.daily_activity (user_id, activity_date desc);

-- ────────────────────────────────────────────────────────────
-- RLS
-- ────────────────────────────────────────────────────────────
alter table public.profiles enable row level security;
alter table public.daily_activity enable row level security;

drop policy if exists "own profile" on public.profiles;
create policy "own profile" on public.profiles
  for all using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists "own activity" on public.daily_activity;
create policy "own activity" on public.daily_activity
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- ────────────────────────────────────────────────────────────
-- Auto-create profile on signup (including anonymous)
-- ────────────────────────────────────────────────────────────
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, display_name)
  values (
    new.id,
    coalesce(new.email, 'anon_' || substring(new.id::text, 1, 8))
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
