# 4-Benchmarks

Este diretório contém benchmarks para validação da qualidade dos exemplos gerados.

## Objetivo

Validar a acurácia dos modelos treinados usando questões reais de concursos públicos brasileiros:
- **CESPE/CEBRASPE** - Principais bancas de concursos
- **FGV** - Fundação Getúlio Vargas
- **FCC** - Fundação Carlos Chagas
- **VUNESP** - Fundação para o Vestibular da Unesp

## Meta de Qualidade

**≥ 94% de acurácia** em questões de nível médio a difícil.

## Estrutura

```
4-Benchmarks/
├── cespe/
│   ├── administrativo/
│   ├── constitucional/
│   └── ...
├── fgv/
├── fcc/
└── reports/
    └── accuracy_reports.json
```

## Formato das Questões

```jsonl
{
  "question_id": "cespe-2023-001",
  "exam_board": "CESPE",
  "year": 2023,
  "area": "Direito Administrativo",
  "difficulty": "medio",
  "question": "Segundo a Lei 9.784/99...",
  "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
  "correct_answer": "B",
  "explanation": "Conforme o Art. 2º..."
}
```

## Pipeline

Este diretório é a **Etapa 4** do pipeline de validação:
```
3-FinalDataset → [Treinamento] → Modelo → [Benchmark] → 4-Benchmarks
```

## Scripts Relacionados

- `scripts/benchmark_model.py` (a criar) - Avaliação automática
- `scripts/collect_exam_questions.py` (a criar) - Coleta de questões
