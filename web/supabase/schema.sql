-- Supabase SQL Editor で一度実行する初期スキーマ

-- ユーザープロフィール (Stripe 連携情報を保持)
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  email text,
  stripe_customer_id text unique,
  subscription_status text not null default 'free', -- 'free' | 'active' | 'canceled'
  created_at timestamptz not null default now()
);

-- 思い出の記録
create table if not exists public.memories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  raw_text text not null,          -- ユーザーが入力した生テキスト
  people text[] not null default '{}', -- 一緒にいた人 (LLM が抽出)
  place text,                      -- 場所 (LLM が抽出)
  occurred_on date,                -- いつ (LLM が抽出)
  summary text,                    -- 一言要約 (LLM が生成)
  created_at timestamptz not null default now()
);

create index if not exists memories_user_id_created_at_idx
  on public.memories (user_id, created_at desc);

-- RLS: 本人の行だけ読み書き可能
alter table public.profiles enable row level security;
alter table public.memories enable row level security;

create policy "profiles: own row" on public.profiles
  for all using (auth.uid() = id) with check (auth.uid() = id);

create policy "memories: own rows" on public.memories
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- サインアップ時に profiles 行を自動作成
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, email) values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
