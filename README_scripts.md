# JurDatasetBrasil - Scripts de Processamento

Este diretório contém o pipeline completo para processamento de documentos jurídicos, geração de dataset e integração com LLMs.

## Estrutura do Pipeline

O pipeline é composto por 5 passos sequenciais:

1.  **Conversão (`01_convert_to_markdown.py`)**
    *   Converte arquivos DOCX/PDF da pasta `0-RawDocs` para Markdown limpo em `1-MarkdownClean`.
    *   Usa `Docling` para preservar estrutura.

2.  **Chunking (`02_create_chunks.py`)**
    *   Lê os arquivos Markdown.
    *   Divide em chunks semânticos (respeitando parágrafos e sentenças).
    *   Gera embeddings (OpenAI ou Local).
    *   Salva no Supabase (tabela `chunks`).

3.  **Geração de Exemplos (`03_generate_examples.py`)**
    *   Consulta chunks do Supabase.
    *   Usa LLM (via OpenRouter) para criar pares de instrução/resposta (Q&A).
    *   Salva no Supabase (tabela `examples`).

4.  **Validação (`04_validate_quality.py`)**
    *   Verifica qualidade dos exemplos (tamanho, estrutura).
    *   Remove duplicatas semânticas usando busca vetorial.
    *   Valida corretude usando LLM (opcional).

5.  **Exportação (`05_export_to_jsonl.py`)**
    *   Exporta exemplos validados para JSONL.
    *   Formato compatível com fine-tuning (ShareGPT/Alpaca).

## Configuração

1.  Certifique-se de ter o arquivo `.env` configurado (baseado em `.env.example`).
2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Como Executar

### Pipeline Completo
Para rodar todos os passos sequencialmente:

```bash
python scripts/run_pipeline.py
```

### Passos Individuais
Para rodar apenas um passo específico (ex: passo 3):

```bash
python scripts/run_pipeline.py --step 3
```

### Retomar Execução
Para começar a partir de um passo (ex: do passo 3 em diante):

```bash
python scripts/run_pipeline.py --start-from 3
```

## Utilitários

*   `scripts/config.py`: Configurações centralizadas.
*   `scripts/database.py`: Cliente Supabase e operações de banco.
*   `scripts/utils/text_processor.py`: Limpeza e chunking de texto.
*   `scripts/utils/embedding_generator.py`: Geração de embeddings (OpenAI/Local).
