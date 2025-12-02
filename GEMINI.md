# GEMINI Context: JurDatasetBrasil

Este arquivo fornece um resumo do projeto, convenções e comandos para guiar as interações do Gemini.

## 1. Visão Geral do Projeto

**JurDatasetBrasil** é um projeto de engenharia de dados focado na criação do maior dataset jurídico aberto do Brasil. O objetivo é processar documentos brutos (leis, súmulas, etc.) e transformá-los em um formato estruturado para dois propósitos principais:

1.  **RAG (Retrieval-Augmented Generation):** Criar uma base de conhecimento com embeddings para que LLMs possam consultar a legislação e encontrar trechos relevantes para responder a perguntas.
2.  **Fine-Tuning:** Gerar um dataset de alta qualidade no formato instrução/resposta (padrão Alpaca/ShareGPT) para treinar e especializar LLMs em domínio jurídico.

A arquitetura é construída em torno de um pipeline Python que interage com um banco de dados **Supabase (Postgres + pgvector)**, utiliza APIs de **LLMs (via OpenRouter)** e **modelos de embedding (sentence-transformers)**.

## 2. Arquitetura e Componentes

O projeto é dividido em quatro componentes principais:

1.  **Pipeline de Dados (`scripts/`):** Um conjunto de scripts Python que orquestra a transformação dos dados em 5 etapas sequenciais.
2.  **Banco de Dados (Supabase):** Um schema Postgres unificado (definido em `SCHEMA.md` e `scripts/setup_database.sql`) que armazena as fontes legais, os chunks de texto com embeddings e os exemplos de treinamento gerados, garantindo rastreabilidade completa.
3.  **Dashboard (`dashboard/`):** Uma aplicação **Streamlit** para visualização e exploração dos dados no banco.
4.  **API (`api/`):** Uma API **FastAPI** (provavelmente para servir o modelo ou dados no futuro).

### Fluxo de Dados do Pipeline

O pipeline é orquestrado por `scripts/run_pipeline.py` e segue estes passos:

-   **Passo 1 (`01_convert_to_markdown.py`):** Converte documentos brutos (`.docx`, `.pdf`) da pasta `0-RawDocs/` para o formato Markdown em `1-MarkdownClean/`.
-   **Passo 2 (`02_create_chunks.py`):** Divide os arquivos Markdown em chunks menores, gera embeddings para cada chunk e os armazena na tabela `chunks` do Supabase.
-   **Passo 3 (`03_generate_examples.py`):** Usa um LLM (via OpenRouter) para ler os chunks e gerar exemplos de pergunta e resposta (instrução/output), que são salvos na tabela `examples`.
-   **Passo 4 (`04_validate_quality.py`):** Executa rotinas de validação de qualidade nos exemplos gerados (ex: remoção de duplicatas, verificação de formato).
-   **Passo 5 (`05_export_to_jsonl.py`):** Exporta os exemplos validados do banco de dados para um arquivo `.jsonl` na pasta `3-FinalDataset/`.

## 3. Comandos e Execução

**Requisitos de Sistema:**
- Python 3.11 ou superior (CPython recomendado)
- pip e venv instalados (use `python -m venv .venv`)

Sempre verifique se o ambiente virtual está ativado antes de executar qualquer comando.

-   **Ativar Ambiente Virtual:**

    **Linux/Mac:**
    ```bash
    source .venv/bin/activate
    ```

    **Windows:**
    ```bash
    .venv\Scripts\activate
    ```

-   **Instalar/Atualizar Dependências:**
    ```bash
    uv pip install -r requirements.txt
    ```

-   **Executar o Pipeline de Dados:**
    ```bash
    # Executar o pipeline completo
    python scripts/run_pipeline.py

    # Executar um passo específico (ex: passo 3)
    python scripts/run_pipeline.py --step 3

    # Iniciar a partir de um passo específico
    python scripts/run_pipeline.py --start-from 2
    ```

-   **Iniciar o Dashboard:**
    ```bash
    streamlit run dashboard/app.py
    ```

-   **Linting e Formatação:**
    ```bash
    # Verificar erros com Ruff
    ruff check .

    # Formatar o código com Black
    black .
    ```

## 4. Convenções de Desenvolvimento

-   **Gerenciamento de Segredos:** Todas as chaves de API (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `OPENROUTER_API_KEY`) devem ser armazenadas em um arquivo `.env` na raiz do projeto.

    **Configuração do .env:**
    ```bash
    cp .env.example .env
    # Edite .env com seus valores reais
    ```

    **Nota:** Nunca commite .env ao git (.gitignore já configurado). Use .env.example como template.
-   **Banco de Dados:** O schema é a fonte da verdade e está documentado em `SCHEMA.md`. As interações com o banco são centralizadas no módulo `scripts/database.py`.
-   **Dependências:** O projeto utiliza `uv` para gerenciar as dependências listadas em `requirements.txt`.
-   **Rastreabilidade:** É fundamental manter a conexão entre os dados gerados e suas fontes. O schema foi desenhado para isso, com chaves estrangeiras como `examples.chunk_ids` e `chunks.law_id`.
-   **Configuração:** As configurações do pipeline (caminhos de arquivos, parâmetros de modelos) são gerenciadas em `scripts/config.py`.

## 5. Troubleshooting e Erros Comuns

- **ModuleNotFoundError ao executar pipeline:** Verifique ativação do venv (`source .venv/bin/activate` ou Windows equiv.), rode `uv pip install -r requirements.txt`
- **Erro conexão Supabase:** Confirme credenciais .env, execute `psql $SUPABASE_URL -f scripts/setup_database.sql`, verifique pgvector extension
- **Embeddings/LLM errors (OpenRouter):** Verifique OPENROUTER_API_KEY, quota modelo, adicione retry/backoff em config.py
- **Falha em passo pipeline:** Rode específico `python scripts/run_pipeline.py --step 3`, habilite logging verbose com `--verbose`
- **Schema dados mismatch:** Re-execute setup_database.sql, verifique `SCHEMA.md`, inspecione tabelas com `psql` queries
