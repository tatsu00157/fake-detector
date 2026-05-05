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
