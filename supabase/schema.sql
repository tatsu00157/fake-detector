create table usage_logs (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade,
  date date not null,
  count int not null default 1,
  unique(user_id, date)
);

alter table usage_logs enable row level security;

create policy "Users can only see their own usage"
  on usage_logs for select
  using (auth.uid() = user_id);

create table subscriptions (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users(id) on delete cascade unique,
  stripe_customer_id text,
  stripe_subscription_id text,
  status text not null default 'inactive',
  current_period_end bigint,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table subscriptions enable row level security;

create policy "Users can only see their own subscription"
  on subscriptions for select
  using (auth.uid() = user_id);
