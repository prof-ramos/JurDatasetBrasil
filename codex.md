# Ambiente Codex - JurDatasetBrasil

Este guia lista o que preencher na aba **Ambientes** do Codex (chatgpt.com/codex) para usar este repo.

## Variaveis de ambiente
- Obrigatorias para rodar Supabase e LLM: `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `OPENROUTER_API_KEY`.
- Demais variaveis ja possuem padrao em `scripts/config.py`, mas podem ser sobrescritas se precisar ajustar limites ou pastas.
- Cole o bloco abaixo no campo de variaveis do Codex e preencha os valores marcados:
```
SUPABASE_URL=<url do seu projeto Supabase>               # obrigatoria
SUPABASE_KEY=<anon key>                                  # obrigatoria para consultas
SUPABASE_SERVICE_ROLE_KEY=<service role key>             # obrigatoria para escrever

OPENROUTER_API_KEY=<chave OpenRouter>                    # obrigatoria para passo 3
# OPENAI_API_KEY=<chave OpenAI se trocar EMBEDDING_MODEL para openai/*>

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

CHUNK_SIZE=1500
CHUNK_OVERLAP=200
MAX_EXAMPLES_PER_CHUNK=3
GENERATION_BATCH_SIZE=10
TEMPERATURE=0.3
MIN_OUTPUT_LENGTH=50
MAX_OUTPUT_LENGTH=1000
SIMILARITY_THRESHOLD=0.85

RAW_DOCS_DIR=0-RawDocs
MARKDOWN_DIR=1-MarkdownClean
CHUNKS_DIR=2-Chunks
DATASET_DIR=3-FinalDataset
BENCHMARKS_DIR=4-Benchmarks
MODELS_DIR=5-Models
LOGS_DIR=logs

NUM_WORKERS=4
API_DELAY=1.0
ENV=development
DEBUG=True
```

## Cache de container
- Defina **Cache de Contêiner: Ativado**. Isso preserva `.venv`, downloads do Hugging Face (sentence-transformers) e caches do Docling entre sessoes, evitando reinstalacao pesada.

## Script de configuracao
- Nao ha setup automatico no repo. Configure como **manual** e use o comando abaixo no campo de setup do ambiente (executa no diretorio raiz):
```
pip install -r requirements.txt
```
- Se preferir isolar dependencias, crie um venv antes (`python -m venv .venv && source .venv/bin/activate`), mas nao e obrigatorio.

## Script de manutencao
- Para checar qualidade e manter o dataset limpo, rode periodicamente o passo 4 do pipeline:
```
python scripts/run_pipeline.py --step 4
```
- Para reexportar os exemplos validados, use:
```
python scripts/05_export_to_jsonl.py
```
