-- Habilitar extensão pgvector
create extension if not exists vector;

-- Tabela de Leis
create table if not exists laws (
    id uuid primary key default gen_random_uuid(),
    law_number text not null,
    law_type text not null,
    title text,
    year integer,
    jurisdiction text default 'BR',
    source_url text,
    is_active boolean default true,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Tabela de Artigos
create table if not exists articles (
    id uuid primary key default gen_random_uuid(),
    law_id uuid references laws(id),
    article_ref text not null,
    full_text text not null,
    structure_json jsonb default '{}'::jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Tabela de Chunks (com vetor)
create table if not exists chunks (
    id uuid primary key default gen_random_uuid(),
    law_id uuid references laws(id),
    article_id uuid references articles(id),
    source_type text default 'lei',
    chunk_index integer,
    content text not null,
    tokens integer,
    metadata jsonb default '{}'::jsonb,
    embedding vector(384), -- Ajustar dimensão conforme modelo (384 para MiniLM-L6-v2)
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Tabela de Datasets
create table if not exists datasets (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    version text not null,
    split text not null,
    description text,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    unique(name, version, split)
);

-- Tabela de Exemplos (com vetor)
create table if not exists examples (
    id uuid primary key default gen_random_uuid(),
    dataset_id uuid references datasets(id),
    instruction text not null,
    input text default '',
    output text not null,
    task_type text,
    difficulty text,
    exam_board text,
    exam_year integer,
    tags text[],
    embedding vector(384), -- Ajustar dimensão conforme modelo
    law_id uuid references laws(id),
    article_id uuid references articles(id),
    chunk_ids uuid[],
    created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Tabela de Migrações
create table if not exists migrations (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    status text not null, -- 'started', 'completed', 'failed', 'rolled_back'
    started_at timestamp with time zone default timezone('utc'::text, now()),
    completed_at timestamp with time zone,
    details jsonb default '{}'::jsonb
);

-- Função RPC para buscar chunks similares
create or replace function match_chunks (
  query_embedding vector(384),
  match_threshold float,
  match_count int,
  filter jsonb default '{}'
) returns table (
  id uuid,
  content text,
  similarity float,
  metadata jsonb
)
language plpgsql
as $$
begin
  return query
  select
    chunks.id,
    chunks.content,
    1 - (chunks.embedding <=> query_embedding) as similarity,
    chunks.metadata
  from chunks
  where 1 - (chunks.embedding <=> query_embedding) > match_threshold
  order by chunks.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Função RPC para buscar exemplos similares
create or replace function match_examples (
  query_embedding vector(384),
  match_threshold float,
  match_count int
) returns table (
  id uuid,
  instruction text,
  output text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    examples.id,
    examples.instruction,
    examples.output,
    1 - (examples.embedding <=> query_embedding) as similarity
  from examples
  where 1 - (examples.embedding <=> query_embedding) > match_threshold
  order by examples.embedding <=> query_embedding
  limit match_count;
end;
$$;
