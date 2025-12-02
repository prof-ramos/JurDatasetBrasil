---
language:
- pt
license: cc-by-4.0
size_categories:
- 10K<n<100K
task_categories:
- question-answering
- text-generation
task_ids:
- open-domain-qa
- language-modeling
pretty_name: JurDatasetBrasil
tags:
- legal
- portuguese
- brazil
- administrative-law
- fine-tuning
- alpaca
- sharegpt
---

# ⚖️ JurDatasetBrasil

<div align="center">

![License](https://img.shields.io/badge/License-CC--BY--4.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Status](https://img.shields.io/badge/Status-MVP-yellow)

**O maior dataset jurídico brasileiro para fine-tuning de LLMs**

[📊 Dataset Card](#dataset-card) •
[🚀 Quick Start](#quick-start) •
[📖 Documentação](https://github.com/prof-ramos/JurDatasetBrasil) •
[🤝 Contribuir](#como-contribuir)

</div>

---

## 📋 Sobre

O **JurDatasetBrasil** é um dataset open-source de alta qualidade focado em Direito Administrativo Brasileiro, projetado especificamente para fine-tuning de Large Language Models (LLMs).

### ✨ Características

- **12.000+ exemplos** de alta qualidade (MVP v0.1)
- **Lei 9.784/99** (Processo Administrativo Federal)
- **3 níveis de dificuldade** (fácil, médio, difícil)
- **Formato Alpaca/ShareGPT** compatível com principais frameworks
- **Rastreabilidade completa** (lei → artigo → chunk → exemplo)
- **Qualidade CESPE/FGV** (benchmark com questões reais)

## 🎯 Meta do Projeto

| Fase | Área do Direito | Exemplos | Status |
|------|----------------|----------|--------|
| **F0** | Administrativo (Lei 9.784/99) | 12.000 | ✅ MVP |
| F1 | Administrativo (completo) | 50.000 | 🔄 Em progresso |
| F2 | Constitucional + Tributário | 60.000 | 📅 Planejado |
| F3 | Penal + Processual Penal | 70.000 | 📅 Planejado |
| F4 | Civil + Consumidor + Trabalho | 300.000+ | 📅 Planejado |

**Target:** Maio 2027

## 🚀 Quick Start

### Instalação

```bash
pip install datasets huggingface-hub
```

### Carregar Dataset

```python
from datasets import load_dataset

# Carregar todo o dataset
dataset = load_dataset("prof-ramos/JurDatasetBrasil")

# Ou apenas um split
train_data = load_dataset("prof-ramos/JurDatasetBrasil", split="train")
```

### Exemplo de Uso

```python
# Ver primeiro exemplo
example = dataset["train"][0]

print(f"Instrução: {example['instruction']}")
print(f"Resposta: {example['output']}")
print(f"Dificuldade: {example['difficulty']}")
print(f"Lei: {example['law_number']}")
```

### Fine-tuning com Transformers

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer

# Carregar modelo base
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# Preparar dataset
def format_instruction(example):
    return f"### Instrução:\n{example['instruction']}\n\n### Resposta:\n{example['output']}"

# Training
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    tokenizer=tokenizer,
    formatting_func=format_instruction,
    max_seq_length=2048,
)

trainer.train()
```

## 📊 Estrutura do Dataset

### Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `instruction` | string | Pergunta ou instrução |
| `input` | string | Contexto adicional (geralmente vazio) |
| `output` | string | Resposta fundamentada |
| `difficulty` | string | Nível: "facil", "medio", "dificil" |
| `task_type` | string | Tipo: "objetiva", "discursiva", "conceito" |
| `exam_board` | string | Banca: "CESPE", "FGV", etc. |
| `exam_year` | int | Ano da questão (se aplicável) |
| `area` | string | Área do direito |
| `law_number` | string | Lei de origem (ex: "9.784/1999") |
| `article_ref` | string | Artigo específico (ex: "Art. 2º") |
| `source_chunks` | list | IDs dos chunks de origem |

### Exemplo Completo

```json
{
  "instruction": "Explique o conceito de ato administrativo vinculado segundo a Lei 9.784/99.",
  "input": "",
  "output": "Ato administrativo vinculado é aquele em que a lei estabelece previamente todos os requisitos e condições para sua prática, não deixando margem de escolha ao administrador. Na Lei 9.784/99, o Art. 2º estabelece que a Administração Pública obedecerá aos princípios da legalidade e finalidade, o que implica que, quando a lei determina de forma específica os elementos do ato (competência, forma, motivo, objeto e finalidade), o administrador deve seguir estritamente o que está previsto, sem qualquer discricionariedade.",
  "difficulty": "medio",
  "task_type": "conceito",
  "exam_board": "CESPE",
  "exam_year": 2023,
  "area": "Direito Administrativo",
  "law_number": "9.784/1999",
  "article_ref": "Art. 2º",
  "source_chunks": ["chunk-uuid-1", "chunk-uuid-2"]
}
```

## 📈 Estatísticas (MVP v0.1)

- **Total de Exemplos:** 12.000
- **Splits:**
  - Train: 9.600 (80%)
  - Validation: 1.800 (15%)
  - Test: 600 (5%)

- **Por Dificuldade:**
  - Fácil: 3.600 (30%)
  - Médio: 6.000 (50%)
  - Difícil: 2.400 (20%)

- **Por Tipo:**
  - Objetivas: 4.800 (40%)
  - Discursivas: 4.200 (35%)
  - Conceitos: 3.000 (25%)

## 🔬 Qualidade e Validação

### Processo de Geração

1. **Fonte:** Lei 9.784/99 (texto oficial)
2. **Chunking:** Divisão em blocos de ~1.500 tokens
3. **Geração:** LLMs (Gemini 2.5 Flash + Grok 4.1 Fast)
4. **Validação:** Múltiplos LLMs + deduplicação
5. **Benchmark:** Testado contra questões CESPE/FGV reais

### Métricas de Qualidade

- **Precisão:** ≥ 94% (baseline CESPE)
- **Duplicatas:** < 1% (threshold de similaridade: 0.95)
- **Rastreabilidade:** 100% (todos os exemplos linkados à fonte)

## 🤝 Como Contribuir

Contribuições são bem-vindas! Veja como:

1. **Issues:** Reporte problemas ou sugira melhorias
2. **Pull Requests:** Contribua com código ou exemplos
3. **Validação:** Ajude a revisar exemplos gerados
4. **Dados:** Contribua com novas leis ou áreas do direito

**Repositório:** [github.com/prof-ramos/JurDatasetBrasil](https://github.com/prof-ramos/JurDatasetBrasil)

## 📄 Licença

- **Dataset:** CC-BY-4.0 (Creative Commons Attribution 4.0 International)
- **Código:** MIT License

### Atribuição

Se usar este dataset em pesquisa ou produção, por favor cite:

```bibtex
@dataset{jurdatasetbrasil2025,
  title={JurDatasetBrasil: Dataset Jurídico Brasileiro para Fine-tuning de LLMs},
  author={Ramos, Gabriel},
  year={2025},
  publisher={Hugging Face},
  url={https://huggingface.co/datasets/prof-ramos/JurDatasetBrasil}
}
```

## 🔗 Links Úteis

- **GitHub:** [prof-ramos/JurDatasetBrasil](https://github.com/prof-ramos/JurDatasetBrasil)
- **Documentação:** [README.md](https://github.com/prof-ramos/JurDatasetBrasil/blob/main/README.md)
- **PRD:** [Especificação Completa](https://github.com/prof-ramos/JurDatasetBrasil/blob/main/PRD.md)
- **Roadmap:** [Planejamento](https://github.com/prof-ramos/JurDatasetBrasil/blob/main/ROADMAP.md)

## 📧 Contato

- **Maintainer:** Gabriel Ramos
- **Email:** [Abra uma issue](https://github.com/prof-ramos/JurDatasetBrasil/issues)

---

<div align="center">

**Construído com ❤️ para a comunidade brasileira de IA e Direito**

⭐ Se este projeto foi útil, considere dar uma estrela no [GitHub](https://github.com/prof-ramos/JurDatasetBrasil)!

</div>
