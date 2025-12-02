# =============================================================================
# JurDatasetBrasil - Docker Makefile
# =============================================================================
# Simplifica comandos Docker comuns para desenvolvimento e produção
#
# Uso:
#   make help           - Mostrar todos os comandos disponíveis
#   make dev            - Iniciar ambiente de desenvolvimento
#   make build          - Build das imagens
#   make test           - Rodar testes
#   make security-scan  - Scan de vulnerabilidades

.PHONY: help
help: ## Mostrar esta mensagem de ajuda
	@echo "JurDatasetBrasil - Docker Commands"
	@echo "=================================="
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

.PHONY: dev
dev: ## Iniciar ambiente de desenvolvimento (API + DB)
	docker compose --profile dev up --build api db

.PHONY: dev-full
dev-full: ## Iniciar ambiente completo (API + DB + Dashboard + Worker)
	docker compose --profile dev --profile ui --profile worker up --build

.PHONY: dashboard
dashboard: ## Iniciar somente o dashboard Streamlit
	docker compose --profile ui up --build dashboard

.PHONY: worker
worker: ## Iniciar worker do pipeline
	docker compose --profile worker up --build worker

.PHONY: shell
shell: ## Abrir shell no container da API
	docker compose --profile dev run --rm api bash

.PHONY: logs
logs: ## Ver logs de todos os serviços
	docker compose logs -f

##@ Build & Production

.PHONY: build
build: ## Build de todas as imagens
	docker compose build --no-cache

.PHONY: build-prod
build-prod: ## Build da imagem de produção
	docker build -t jurdatasetbrasil:prod --target runtime --build-arg INSTALL_DEV=false .

.PHONY: prod
prod: ## Rodar em modo produção
	docker compose --profile prod up -d api-prod

##@ Testing & Quality

.PHONY: test
test: ## Rodar testes
	docker compose --profile dev run --rm api pytest tests/ -v

.PHONY: lint
lint: ## Rodar linters (ruff + black)
	docker compose --profile dev run --rm api ruff check .
	docker compose --profile dev run --rm api black --check .

.PHONY: format
format: ## Formatar código com black
	docker compose --profile dev run --rm api black .

##@ Security

.PHONY: security-scan
security-scan: build-prod ## Scan de vulnerabilidades com Trivy
	@echo "Scanning image for vulnerabilities..."
	@if command -v trivy &> /dev/null; then \
		trivy image --severity HIGH,CRITICAL jurdatasetbrasil:prod; \
	else \
		echo "⚠️  Trivy not installed. Install: brew install trivy (Mac) or apt install trivy (Linux)"; \
		echo "   Alternatively, use: docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image jurdatasetbrasil:prod"; \
	fi

.PHONY: security-scan-docker
security-scan-docker: build-prod ## Scan usando Trivy via Docker
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy:latest image --severity HIGH,CRITICAL jurdatasetbrasil:prod

##@ Database

.PHONY: db-shell
db-shell: ## Conectar ao PostgreSQL via psql
	docker compose --profile dev exec db psql -U postgres -d jurdataset

.PHONY: db-migrate
db-migrate: ## Executar migrations SQL
	docker compose --profile dev exec api python scripts/setup_database.sql

.PHONY: db-backup
db-backup: ## Backup do banco de dados
	@mkdir -p backups
	docker compose --profile dev exec db pg_dump -U postgres jurdataset > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✓ Backup salvo em backups/"

##@ Cleanup

.PHONY: clean
clean: ## Parar e remover containers
	docker compose down

.PHONY: clean-all
clean-all: ## Parar, remover containers e volumes
	docker compose down -v

.PHONY: prune
prune: ## Remover imagens, containers e volumes não utilizados
	docker system prune -af --volumes

##@ Pipeline

.PHONY: pipeline-step1
pipeline-step1: ## Executar passo 1 do pipeline (Conversão para Markdown)
	docker compose --profile worker run --rm worker python scripts/01_convert_to_markdown.py

.PHONY: pipeline-step2
pipeline-step2: ## Executar passo 2 do pipeline (Criação de chunks)
	docker compose --profile worker run --rm worker python scripts/02_create_chunks.py

.PHONY: pipeline-step3
pipeline-step3: ## Executar passo 3 do pipeline (Geração de exemplos)
	docker compose --profile worker run --rm worker python scripts/03_generate_examples.py

.PHONY: pipeline-step4
pipeline-step4: ## Executar passo 4 do pipeline (Validação de qualidade)
	docker compose --profile worker run --rm worker python scripts/04_validate_quality.py

.PHONY: pipeline-step5
pipeline-step5: ## Executar passo 5 do pipeline (Export para JSONL)
	docker compose --profile worker run --rm worker python scripts/05_export_to_jsonl.py

.PHONY: pipeline-full
pipeline-full: ## Executar pipeline completo
	docker compose --profile worker run --rm worker python scripts/run_pipeline.py

##@ Monitoring

.PHONY: stats
stats: ## Mostrar estatísticas dos containers
	docker stats

.PHONY: health
health: ## Verificar health dos serviços
	@echo "Checking service health..."
	@docker compose ps
	@echo "\nAPI Health:"
	@curl -s http://localhost:8000/health | jq . || echo "⚠️  API not responding"

##@ Info

.PHONY: env-check
env-check: ## Verificar variáveis de ambiente necessárias
	@echo "Checking required environment variables..."
	@test -f .env && echo "✓ .env file exists" || echo "⚠️  .env file missing - copy .env.example"
	@grep -q "SUPABASE_URL" .env && echo "✓ SUPABASE_URL set" || echo "⚠️  SUPABASE_URL missing"
	@grep -q "OPENROUTER_API_KEY" .env && echo "✓ OPENROUTER_API_KEY set" || echo "⚠️  OPENROUTER_API_KEY missing"

.PHONY: size
size: ## Mostrar tamanho das imagens Docker
	@docker images | grep jurdatasetbrasil || echo "No images found. Run 'make build' first."

# Default target
.DEFAULT_GOAL := help
