# JurDatasetBrasil

Repositório para construção do maior dataset jurídico aberto do Brasil para treinamento e avaliação de LLMs. Aqui ficam o PRD, a estrutura de pastas para ingestão de documentos e o esquema de dados sugerido para armazenar tanto fontes normativas quanto exemplos de treinamento.

## 🤗 Hugging Face Space

**Demo interativo:** [SherlockRamos/JurDatasetBrasil-Explorer](https://huggingface.co/spaces/SherlockRamos/JurDatasetBrasil-Explorer)

Explore o dataset através de uma interface Gradio com busca, estatísticas e visualização de exemplos.

### 🚀 Deploy seu próprio Space

```bash
# 1. Criar Space no HF
hf repo create SEU-USERNAME/JurDatasetBrasil-Explorer --repo-type space --space-sdk gradio

# 2. Preparar e enviar arquivos
mkdir temp_space && cd temp_space
cp ../huggingface/app.py app.py && cp ../.space.yml . && cp ../requirements-huggingface.txt requirements.txt
git init && git checkout -b main && git add . && git commit -m "🚀 Deploy"
git remote add space https://huggingface.co/spaces/SEU-USERNAME/JurDatasetBrasil-Explorer
git push space main
```

**Documentação completa:** [docs/HUGGINGFACE.md](docs/HUGGINGFACE.md)

## Objetivos do projeto
- Consolidar legislação, súmulas e comentários em formato auditável.
- Gerar datasets em padrão Alpaca/ShareGPT com rastreabilidade completa.
- Suportar uso de RAG clássico (busca em normas) e RAG por casos semelhantes (few-shot a partir de exemplos reais).

## Estrutura do repositório
- `0-RawDocs/`: documentos originais (PDF/DOCX) antes da limpeza.
- [`PRD.md`](PRD.md): PRD 2.0 em português com visão estratégica, roadmap e análise de riscos.
- [`SCHEMA.md`](SCHEMA.md): proposta de schema Postgres/Supabase com pgvector para unificar armazenamento de normas, chunks e exemplos.

## Docker e ambientes
- Guia rápido: [`docs/DOCKER.md`](docs/DOCKER.md) cobre imagens multi-stage, Compose (dev/prod) e recomendações de segurança/performance.

## Esquema de dados recomendado
O schema descrito em [`SCHEMA.md`](SCHEMA.md) organiza o projeto em quatro camadas:
1. **Fontes normativas** (`laws`, `articles`)
2. **Chunks textuais** com embeddings para RAG clássico (`chunks`)
3. **Exemplos de treinamento** com instrução/input/output e embeddings para similaridade de casos (`examples`)
4. **Versionamento de datasets** (`datasets`)

Esse arranjo permite usar um único banco lógico tanto para treino de modelos quanto para buscas semânticas, reduzindo retrabalho e preservando rastreabilidade entre exemplos e suas fontes legais.
