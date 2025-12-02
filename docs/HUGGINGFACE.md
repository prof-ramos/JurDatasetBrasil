# 🤗 Hugging Face Integration Guide

Guia completo para deploy e integração do JurDatasetBrasil com Hugging Face Hub e Spaces.

---

## 📋 Índice

1. [Setup Inicial](#setup-inicial)
2. [Deploy do Space](#deploy-do-space)
3. [Upload do Dataset](#upload-do-dataset)
4. [CI/CD Automático](#cicd-automático)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Setup Inicial

### 1. Criar Conta no Hugging Face

1. Acesse [huggingface.co](https://huggingface.co)
2. Crie uma conta gratuita
3. Vá em **Settings → Access Tokens**
4. Crie um token com permissões `write`

### 2. Configurar Token Localmente

```bash
# Instalar Hugging Face CLI
pip install huggingface-hub

# Login
huggingface-cli login
# Cole seu token quando solicitado
```

### 3. Adicionar Token ao GitHub

1. Vá em **Settings → Secrets and variables → Actions**
2. Crie um secret chamado `HF_TOKEN`
3. Cole seu token do Hugging Face

---

## 🌐 Deploy do Space

### Opção 1: Deploy Manual

```bash
# 1. Criar Space no HF
# Acesse: https://huggingface.co/new-space
# Nome: JurDatasetBrasil-Explorer
# SDK: Gradio
# Hardware: CPU basic

# 2. Clone o Space localmente
git clone https://huggingface.co/spaces/prof-ramos/JurDatasetBrasil-Explorer
cd JurDatasetBrasil-Explorer

# 3. Copiar arquivos
cp ../huggingface/app.py app.py
cp ../.space.yml .
cp ../requirements-huggingface.txt requirements.txt
cp ../huggingface/README.md README.md

# 4. Commit e push
git add .
git commit -m "Initial commit"
git push
```

### Opção 2: Deploy Automático via GitHub Actions

O projeto já inclui workflow automático (`.github/workflows/sync-huggingface.yml`):

**Triggers automáticos:**
- Push para `main` que modifica arquivos em `huggingface/`
- Push para `main` que modifica `3-FinalDataset/`

**Trigger manual:**
```bash
# Via GitHub UI: Actions → Sync to Hugging Face → Run workflow
```

---

## 📊 Upload do Dataset

### Upload Manual

```bash
# 1. Preparar dataset (exportar para JSONL)
python scripts/05_export_to_jsonl.py

# 2. Verificar arquivos
ls -lh 3-FinalDataset/*.jsonl

# 3. Upload
python huggingface/upload_dataset.py
```

**Variáveis de ambiente:**
```bash
export HF_TOKEN="hf_..."
export HF_REPO_ID="prof-ramos/JurDatasetBrasil"
python huggingface/upload_dataset.py
```

### Upload Automático via GitHub Actions

```bash
# Trigger manual do workflow
gh workflow run sync-huggingface.yml \
  -f upload_dataset=true \
  -f sync_space=true
```

---

## 🔄 CI/CD Automático

### Workflow: `sync-huggingface.yml`

O workflow possui 3 jobs:

#### 1. **sync-space**
- Roda em: push para `main` ou trigger manual
- Sincroniza código do Space
- Copia: `app.py`, `.space.yml`, `requirements.txt`, `README.md`

#### 2. **upload-dataset**
- Roda em: trigger manual com flag `upload_dataset=true`
- Valida arquivos JSONL em `3-FinalDataset/`
- Faz upload para HF Hub
- Cria tag de release

#### 3. **notify**
- Roda após completion dos outros jobs
- Gera resumo no GitHub Actions

### Exemplo de Uso

```bash
# 1. Gerar dataset
python scripts/run_pipeline.py

# 2. Commit e push
git add 3-FinalDataset/
git commit -m "feat: adicionar novos exemplos do dataset"
git push origin main

# 3. Trigger upload manual (se necessário)
gh workflow run sync-huggingface.yml -f upload_dataset=true
```

---

## 🐳 Docker para HF Spaces

O projeto inclui `Dockerfile.huggingface` otimizado:

### Features

- ✅ Base: `python:3.11-slim`
- ✅ Usuário não-root (requerido pelo HF)
- ✅ Cache de modelos em `/app/.cache`
- ✅ Suporte a GPU (opcional)
- ✅ Healthcheck integrado

### Build Local

```bash
# Build
docker build -f Dockerfile.huggingface -t jurdataset-hf:latest .

# Run
docker run -p 7860:7860 \
  -e HF_TOKEN=$HF_TOKEN \
  -e DATASET_NAME=prof-ramos/JurDatasetBrasil \
  jurdataset-hf:latest

# Acessar
open http://localhost:7860
```

---

## 📦 Estrutura de Arquivos HF

```
JurDatasetBrasil/
├── huggingface/
│   ├── app.py                    # Gradio app principal
│   ├── upload_dataset.py         # Script de upload
│   └── README.md                 # Dataset card (HF Hub)
├── .space.yml                    # Config do Space
├── Dockerfile.huggingface        # Docker otimizado
├── requirements-huggingface.txt  # Deps adicionais
└── .github/workflows/
    └── sync-huggingface.yml      # CI/CD workflow
```

---

## 🎨 Customização do Space

### Modificar Interface

Edite `huggingface/app.py`:

```python
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # Adicione tabs, components, etc.
    with gr.Tab("🔍 Nova Funcionalidade"):
        # Seu código aqui
        pass
```

### Adicionar Hardware GPU

1. No HF Space Settings
2. Hardware → Upgrade to GPU
3. Opções: T4 ($0.60/h), A10G ($3.15/h), A100 ($4.13/h)

### Variáveis de Ambiente

Adicione em Settings → Variables:

```bash
DATASET_NAME=prof-ramos/JurDatasetBrasil
DATASET_VERSION=v0.1
ENABLE_ANALYTICS=true
```

---

## 🔍 Monitoramento

### Logs do Space

```bash
# Via CLI
huggingface-cli logs prof-ramos/JurDatasetBrasil-Explorer

# Via UI
# Acesse: https://huggingface.co/spaces/prof-ramos/JurDatasetBrasil-Explorer
# Clique em "Logs" tab
```

### Analytics do Dataset

```bash
# Estatísticas de download
huggingface-cli stats prof-ramos/JurDatasetBrasil
```

---

## 🐛 Troubleshooting

### Problema: Space não inicia

**Solução:**
```bash
# 1. Verificar logs
huggingface-cli logs prof-ramos/JurDatasetBrasil-Explorer

# 2. Verificar requirements
cat requirements-huggingface.txt

# 3. Testar localmente
docker build -f Dockerfile.huggingface -t test .
docker run -p 7860:7860 test
```

### Problema: Dataset não aparece

**Solução:**
```bash
# 1. Verificar se upload foi bem-sucedido
huggingface-cli list prof-ramos

# 2. Verificar permissões
# Dataset deve estar público ou você deve estar logado

# 3. Forçar refresh do cache
from datasets import load_dataset
dataset = load_dataset("prof-ramos/JurDatasetBrasil", download_mode="force_redownload")
```

### Problema: Token inválido

**Solução:**
```bash
# 1. Gerar novo token
# https://huggingface.co/settings/tokens

# 2. Atualizar GitHub Secret
# Settings → Secrets → Edit HF_TOKEN

# 3. Relogar localmente
huggingface-cli logout
huggingface-cli login
```

### Problema: Build timeout

**Solução:**
```bash
# Reduzir dependências em requirements-huggingface.txt
# Remover pacotes não usados
# Usar versões específicas (não >=)
```

---

## 📚 Recursos Adicionais

### Documentação Oficial

- [HF Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [HF Datasets Docs](https://huggingface.co/docs/datasets)
- [Gradio Docs](https://gradio.app/docs/)

### Templates

- [Gradio Space Template](https://huggingface.co/spaces/gradio/blocks-gallery)
- [Dataset Card Template](https://huggingface.co/docs/hub/datasets-cards)

### Exemplos

- [Dataset Browser](https://huggingface.co/spaces/huggingface/dataset-viewer)
- [Model Cards](https://huggingface.co/models?sort=trending)

---

## 🎯 Checklist de Deploy

Antes de fazer deploy em produção:

- [ ] Token HF configurado no GitHub Secrets
- [ ] Dataset exportado para JSONL (`3-FinalDataset/`)
- [ ] README.md do dataset atualizado
- [ ] Space testado localmente
- [ ] CI/CD workflow testado
- [ ] Permissões do dataset configuradas (público/privado)
- [ ] Analytics habilitado (opcional)
- [ ] Custom domain configurado (opcional)

---

## 🚀 Quick Deploy Checklist

```bash
# 1. Setup inicial (uma vez)
huggingface-cli login
gh secret set HF_TOKEN

# 2. Preparar dataset
python scripts/run_pipeline.py
python scripts/05_export_to_jsonl.py

# 3. Upload dataset
python huggingface/upload_dataset.py

# 4. Deploy Space (automático via push)
git add huggingface/
git commit -m "feat: atualizar HF Space"
git push origin main

# 5. Verificar
open https://huggingface.co/spaces/prof-ramos/JurDatasetBrasil-Explorer
```

---

**Pronto para produção!** 🎉

Se encontrar problemas, abra uma [issue no GitHub](https://github.com/prof-ramos/JurDatasetBrasil/issues).
