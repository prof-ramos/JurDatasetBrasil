# ADR 0001 — Backend de Embeddings

- **Status**: Aceito
- **Data**: 2025-12-02
- **Contexto**: O pipeline precisa gerar embeddings para `chunks` e `examples`. Ha dois caminhos disponiveis no codigo (`scripts/utils/embedding_generator.py`): modelo local sentence-transformers ou APIs externas (OpenAI). O schema pgvector atual esta configurado para 384 dimensoes.
- **Decisao**: Usar **sentence-transformers/all-MiniLM-L6-v2** local como backend padrao (ENV `EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`, `EMBEDDING_DIMENSION=384`). Permitir troca para OpenAI ajustando ENV e a dimensao no banco.
- **Consequencias**:
  - ✅ Sem custo por token e sem dependencia de rede na etapa de chunking.
  - ✅ Cache de container acelera cargas subsequentes do modelo.
  - ⚠️ Se trocar para OpenAI (`openai/text-embedding-*`), e necessario:
    - Atualizar `EMBEDDING_MODEL`/`EMBEDDING_DIMENSION` no `.env`.
    - Migrar colunas `embedding vector(<nova_dim>)` e RPCs em `scripts/setup_database.sql`.
    - Regerar embeddings ja salvos para manter consistencia de dimensao.
- **Alternativas consideradas**:
  - OpenAI apenas (descartado por custo/latencia).
  - Modelo maior local (ex.: `all-mpnet-base-v2` com 768 dims) — adiado para quando houver GPU local ou necessidade de precisao maior.
