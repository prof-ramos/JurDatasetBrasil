# 5-Models

Este diretório contém os modelos fine-tuned gerados a partir dos datasets.

## Objetivo

Armazenar e versionar modelos especializados em direito brasileiro:
- **JurLM-Admin-8B** - Modelo especializado em Direito Administrativo
- **JurLM-Const-8B** - Direito Constitucional
- **JurLM-Penal-8B** - Direito Penal
- **JurLM-Full-70B** - Modelo completo com todas as áreas

## Estrutura

```
5-Models/
├── JurLM-Admin-8B/
│   ├── v0.1/
│   │   ├── model.safetensors
│   │   ├── config.json
│   │   ├── tokenizer.json
│   │   └── training_metrics.json
│   └── v0.2/
├── checkpoints/
└── training_logs/
```

## Configuração de Treinamento

Parâmetros típicos:
- **Base Model**: Llama 3.1 8B ou Mistral 7B
- **LoRA Rank**: 64-128
- **Batch Size**: 4-8 (com gradient accumulation)
- **Learning Rate**: 1e-4 a 5e-5
- **Epochs**: 3-5
- **Context Length**: 4096 tokens

## Métricas de Avaliação

Cada modelo inclui:
- Accuracy em benchmarks CESPE/FGV
- Perplexity nos conjuntos de validação
- Tempo de inferência
- Uso de memória

## Distribuição

Modelos são publicados no Hugging Face sob licença compatível (Apache 2.0 ou MIT).

## Pipeline

Este diretório é a **Etapa 5** do pipeline:
```
3-FinalDataset → [Fine-tuning] → 5-Models → [Avaliação] → Publicação HF
```

## Scripts Relacionados

- `scripts/train_model.py` (a criar) - Script de treinamento
- `scripts/evaluate_model.py` (a criar) - Avaliação de métricas
- `scripts/deploy_to_hf.py` - Deploy para Hugging Face
