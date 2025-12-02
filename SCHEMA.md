# Esquema de Dados — JurDatasetBrasil

Este documento descreve um schema unificado em Postgres/Supabase (com extensão `pgvector`) que atende simultaneamente a três casos:
- **Treino de LLMs** no formato instruction/input/output.
- **RAG clássico** para busca em leis, súmulas ou comentários.
- **RAG por casos semelhantes**, reutilizando embeddings dos próprios exemplos de QA.

A ideia é manter um único modelo lógico, evitando múltiplos bancos separados para cada finalidade.

## Visão geral por camadas
1. **Fontes normativas**: leis, artigos, parágrafos, súmulas ou comentários.
2. **Chunks textuais**: pedaços de ~1–2k tokens com embedding para busca semântica.
3. **Exemplos do dataset**: pares instruction/input/output vinculados a chunks de origem e com embedding próprio.
4. **Versão / Dataset / Split**: rastreabilidade de versões (ex.: `v1`, `v1.1`, `train`, `validation`).

## Tabelas principais
### 1. `laws` (ou `norms`)
Fonte oficial da norma.

```sql
create table public.laws (
  id            uuid primary key default gen_random_uuid(),
  law_number    text not null,       -- ex: '9.784/1999'
  law_type      text not null,       -- 'lei', 'cf', 'cpc', 'clt', etc.
  title         text,
  year          int,
  jurisdiction  text default 'BR',
  source_url    text,
  is_active     boolean default true,
  created_at    timestamptz default now()
);
create index on public.laws (law_number);
```

### 2. `articles`
Estrutura interna da lei (artigos, parágrafos, incisos).

```sql
create table public.articles (
  id            uuid primary key default gen_random_uuid(),
  law_id        uuid not null references public.laws(id) on delete cascade,
  article_ref   text not null, -- ex: 'Art. 2º', 'Art. 37, §6º'
  full_text     text not null,
  structure_json jsonb,        -- opcional: incisos, alíneas, etc.
  created_at    timestamptz default now()
);
create index on public.articles (law_id);
create index on public.articles (article_ref);
```

### 3. `chunks` (camada central do RAG)
Pedaços usados para busca semântica. O RAG opera sobre `content` + `embedding`.

```sql
-- create extension if not exists vector; -- ativar pgvector

create table public.chunks (
  id              uuid primary key default gen_random_uuid(),
  law_id          uuid references public.laws(id),
  article_id      uuid references public.articles(id),
  source_type     text not null,    -- 'lei', 'sumula', 'comentario', etc.
  chunk_index     int not null,     -- ordem dentro da fonte
  content         text not null,    -- texto desse chunk
  tokens          int,              -- opcional
  metadata        jsonb,            -- ex: {"tema":"processo", "nivel":"avancado"}
  embedding       vector(1536),     -- ajustar para a dimensão do encoder
  created_at      timestamptz default now()
);

create index on public.chunks
  using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create index on public.chunks (law_id);
create index on public.chunks (article_id);
```

**Por que usar `chunks` e não `articles` diretamente?**
Artigos podem ser longos; pedaços menores aumentam a precisão do modelo na recuperação de contexto.

### 4. `datasets` (versão / split)
Controla versões e divisões de dataset, alinhado ao JSONL de treino.

```sql
create table public.datasets (
  id           uuid primary key default gen_random_uuid(),
  name         text not null,  -- ex: 'JurDatasetBrasil-Admin-v1'
  version      text not null,  -- 'v1', 'v1.1', 'v2'
  split        text not null,  -- 'train', 'validation', 'test'
  description  text,
  created_at   timestamptz default now(),
  unique(name, version, split)
);
```

### 5. `examples` (instruction/input/output)
Espelha o JSONL de treino e permite RAG por similaridade entre questões.

```sql
create table public.examples (
  id              uuid primary key default gen_random_uuid(),
  dataset_id      uuid not null references public.datasets(id) on delete cascade,

  instruction     text not null,
  input           text,
  output          text not null,

  task_type       text,     -- 'questao_objetiva', 'discursiva', 'resumo', etc.
  difficulty      text,     -- 'facil','medio','dificil'
  exam_board      text,     -- 'CESPE','FGV','OAB'
  exam_year       int,
  tags            text[],   -- ['administrativo','ato_administrativo']

  embedding       vector(1536),

  law_id          uuid references public.laws(id),
  article_id      uuid references public.articles(id),
  chunk_ids       uuid[],   -- chunks usados para gerar o exemplo

  created_at      timestamptz default now()
);

create index on public.examples (dataset_id);
create index on public.examples using ivfflat (embedding vector_cosine_ops) with (lists = 100);
create index on public.examples using gin (tags);
```

### Por que este schema resolve os três usos?
- `chunks` → RAG tradicional (busca na letra da lei ou súmula).
- `examples` → RAG de casos semelhantes (few-shot ou sugestão de respostas parecidas).
- Relações com `laws`/`articles` dão rastreabilidade completa para auditoria e atualização.

## Mapeando o JSONL do dataset
Exemplo típico de JSONL:

```jsonc
{
  "instruction": "Explique o conceito de ato administrativo vinculado...",
  "input": "",
  "output": "Ato administrativo vinculado é aquele em que...",
  "metadata": {
    "law_number": "9.784/1999",
    "article_ref": "Art. 2º, parágrafo único, I",
    "area": "Direito Administrativo",
    "difficulty": "medio",
    "exam_board": "CESPE",
    "exam_year": 2023,
    "source_chunks": ["chunk-uuid-1", "chunk-uuid-2"]
  }
}
```

Mapeamento:
- Vai para `examples` (instruction/input/output).
- `metadata.law_number` → `laws.law_number`.
- `metadata.article_ref` → `articles.article_ref`.
- `metadata.source_chunks` → `examples.chunk_ids`.

## Exemplos de consultas RAG
### Buscar chunks mais relevantes
```sql
select
  c.id,
  c.content,
  c.metadata,
  l.law_number,
  a.article_ref
from public.chunks c
left join public.laws l on c.law_id = l.id
left join public.articles a on c.article_id = a.id
where
  c.source_type = 'lei'
  and c.metadata->>'area' = 'Direito Administrativo'
order by
  c.embedding <-> :query_embedding
limit 5;
```

### Buscar exemplos semelhantes para few-shot
```sql
select
  e.id,
  e.instruction,
  e.input,
  e.output,
  e.task_type,
  e.difficulty,
  e.exam_board,
  e.exam_year
from public.examples e
where
  e.dataset_id = :dataset_id
order by
  e.embedding <-> :query_embedding
limit 3;
```

## Opções alternativas
- **Minimalista**: tabela única `documents` com `doc_type`, `content`, `metadata`, `embedding`.
- **Hardcore acadêmica**: expandir com `judgments`, `cases` ou `benchmarks` se surgirem necessidades de pesquisa avançada.

## Recomendações de adoção
1. Começar com as tabelas `laws`, `articles`, `chunks`, `datasets`, `examples` e scripts em `scripts/` para popular a base.
2. Gerar embeddings tanto para `chunks` (RAG tradicional) quanto para `examples` (similaridade de casos).
3. Reaproveitar o schema conforme novas matérias forem adicionadas, apenas inserindo novas linhas e versões.
