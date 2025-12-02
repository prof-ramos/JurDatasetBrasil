# JurDatasetBrasil - Docker Toolkit

Este guia cobre a imagem multi-stage (produção e dev), Compose para workflows locais e dicas de otimização/segurança.

## 🚀 Quick Start

```bash
# 1. Configurar ambiente
cp .env.example .env  # Edite com suas credenciais

# 2. Iniciar desenvolvimento
make dev  # ou: docker compose --profile dev up --build api db

# 3. Acessar
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## Pré-requisitos
- Docker 24+ e Docker Compose v2 (`docker compose`)
- Make (opcional, mas recomendado)
- Copie `.env.example` para `.env` e preencha credenciais (Supabase, OpenRouter, DB)

## Imagens
- `Dockerfile` usa Python 3.11-slim, venv em `/opt/venv` e usuário não-root `app`.
- Targets:
  - `runtime` (padrão): instala `requirements.txt`, pensado para produção.
  - `dev`: deriva do runtime com `--reload`; use com `INSTALL_DEV=true` para dependências de pipeline/LLM.
- Dados grandes estão no `.dockerignore` (0-RawDocs, 1-MarkdownClean, etc.); monte via volumes.

### Exemplos de build
```bash
# Produção (imagem menor)
docker build -t jurdataset-api:prod --target runtime --build-arg INSTALL_DEV=false .

# Dev/pipeline (dependências completas + reload)
docker build -t jurdataset-api:dev --target dev --build-arg INSTALL_DEV=true .

# Multi-plataforma (ex: CI)
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/org/jurdataset-api:prod --target runtime .
```

## Compose
`docker-compose.yml` oferece perfis para dev (`api`, `dashboard`, `worker`, `db`) e prod (`api-prod`).

### Desenvolvimento rápido
```bash
cp .env.example .env  # ajuste credenciais
docker compose --profile dev up --build api db
```
- API: http://localhost:8000 (auto-reload).
- Postgres (pgvector): porta 5432, credenciais de `.env`.
- Dashboard (Streamlit): `docker compose --profile ui up dashboard` → http://localhost:8501.
- Pipeline: `docker compose --profile worker run --rm worker python scripts/run_pipeline.py --step 1`.

### Produção local
```bash
# Requer DATABASE_URL apontando para o banco real
docker compose --profile prod up --build -d api-prod
```
- Sem bind mounts; limite de CPU/memória definido em `deploy`.
- Healthcheck consulta `/health`.

### Serviços/variáveis chave
- `DATABASE_URL` tem precedência; fallback para POSTGRES_* (dev usa `db` como host).
- `API_PORT`/`DASHBOARD_PORT` controlam os binds locais.
- Volumes: `pgdata` (banco) e `pipeline-cache` (caches do pipeline).

## Segurança e performance
- Usuário não-root (`app`) no runtime.
- Base minimalista (`python:3.11-slim`) e camadas separadas de build/runtime.
- Recomendado: `docker scan` ou `trivy image jurdataset-api:prod` antes de publicar.
- Passe segredos somente por `.env`/CI secrets; nunca bake em build args.
- Para builds mais rápidos: `DOCKER_BUILDKIT=1` e cache (`--mount=type=cache,target=/root/.cache/pip` já habilitado).

## CI/CD (sugestão)
- Pipeline:
  1. `docker buildx build --target runtime -t ghcr.io/org/jurdataset-api:${GITHUB_SHA} .`
  2. `docker push ghcr.io/org/jurdataset-api:${GITHUB_SHA}`
  3. Deploy no orquestrador (K8s/Swarm) com `imagePullPolicy: IfNotPresent` e `envFrom` secrets.
- Inclua step opcional de scan e rodar `docker compose --profile prod up -d api-prod` em staging smoke.

## Makefile - Comandos Simplificados

O projeto inclui um `Makefile` com comandos úteis:

### Desenvolvimento
```bash
make dev              # Iniciar API + DB
make dev-full         # Iniciar tudo (API + DB + Dashboard + Worker)
make dashboard        # Somente dashboard Streamlit
make worker           # Somente worker do pipeline
make shell            # Abrir shell no container
make logs             # Ver logs em tempo real
```

### Build e Produção
```bash
make build            # Build todas as imagens
make build-prod       # Build imagem de produção otimizada
make prod             # Rodar em modo produção
```

### Testes e Qualidade
```bash
make test             # Rodar testes com pytest
make lint             # Verificar código (ruff + black)
make format           # Formatar código automaticamente
```

### Segurança
```bash
make security-scan          # Scan de vulnerabilidades (requer Trivy)
make security-scan-docker   # Scan usando Trivy via Docker
```

### Pipeline
```bash
make pipeline-step1   # Passo 1: Conversão para Markdown
make pipeline-step2   # Passo 2: Criação de chunks
make pipeline-step3   # Passo 3: Geração de exemplos
make pipeline-full    # Pipeline completo
```

### Database
```bash
make db-shell         # Conectar ao PostgreSQL
make db-migrate       # Executar migrations
make db-backup        # Fazer backup do banco
```

### Utilitários
```bash
make clean            # Parar e remover containers
make clean-all        # Limpar tudo (incluindo volumes)
make stats            # Estatísticas dos containers
make health           # Verificar saúde dos serviços
make env-check        # Validar variáveis de ambiente
make help             # Listar todos os comandos
```

## GitHub Actions - CI/CD Automatizado

O projeto inclui workflow de CI/CD (`.github/workflows/docker-build-scan.yml`) que:

1. **Build automático** em push para main/develop
2. **Security scan** com Trivy (vulnerabilidades CRITICAL/HIGH)
3. **Upload de resultados** para GitHub Security tab
4. **Push para GHCR** (GitHub Container Registry) em main
5. **Verificação de tamanho** da imagem

### Configuração do Registry

Para usar o GHCR, configure um Personal Access Token:

```bash
# 1. Criar token em: https://github.com/settings/tokens
#    Scopes necessários: write:packages, read:packages

# 2. Login local
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# 3. Pull imagens do CI
docker pull ghcr.io/prof-ramos/jurdatasetbrasil:latest
```

## Troubleshooting rápido
- `ModuleNotFoundError`: confirme se usou `INSTALL_DEV=true` quando precisa de dependências do pipeline.
- `psycopg2` erro de conexão: verifique `DATABASE_URL` e se o serviço `db` está de pé (`docker compose ps`).
- Hot reload não reflete: confirme o bind `. :/app` no perfil dev e que está rodando o target `dev`.
- **Build lento**: Use `DOCKER_BUILDKIT=1` e cache habilitado (já configurado).
- **Vulnerabilidades detectadas**: Execute `make security-scan` e atualize dependências em `requirements.txt`.
