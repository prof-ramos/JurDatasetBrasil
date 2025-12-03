# 2-Chunks

Este diretório contém os chunks de texto processados a partir dos documentos em markdown.

## Estrutura

Cada chunk possui:
- **Conteúdo**: Texto com aproximadamente 1-2k tokens
- **Embeddings**: Vetores de 1536 dimensões para busca semântica (RAG)
- **Metadados**: Referência à lei, artigo e posição no documento original

## Formato

Os chunks são armazenados no banco de dados Postgres/Supabase na tabela `chunks`, mas podem ser exportados aqui em formato JSONL para backup e versionamento.

## Pipeline

Este diretório é a **Etapa 2** do pipeline de processamento:
```
1-MarkdownClean → [Chunking] → 2-Chunks → [Geração] → 3-FinalDataset
```

## Scripts Relacionados

- `scripts/02_create_chunks.py` - Script de chunking e geração de embeddings
