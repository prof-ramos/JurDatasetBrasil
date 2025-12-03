# 3-FinalDataset

Este diretório contém os datasets finais prontos para treinamento de LLMs.

## Estrutura

Arquivos no formato JSONL (JSON Lines) seguindo os padrões:
- **Alpaca Format**: `instruction`, `input`, `output`
- **ShareGPT Format**: conversações multi-turn

## Exemplo de Entrada

```jsonl
{
  "instruction": "Explique o conceito de ato administrativo vinculado segundo a Lei 9.784/99",
  "input": "",
  "output": "Ato administrativo vinculado é aquele em que...",
  "metadata": {
    "law_number": "9.784/1999",
    "article_ref": "Art. 2º, parágrafo único, I",
    "area": "Direito Administrativo",
    "difficulty": "medio",
    "exam_board": "CESPE",
    "exam_year": 2023,
    "source_chunks": ["chunk-uuid-1", "chunk-uuid-2"]
  }
}
```

## Splits

Os datasets são divididos em:
- `train/` - 80% dos exemplos para treinamento
- `validation/` - 10% para validação durante treinamento
- `test/` - 10% para avaliação final

## Versionamento

Cada versão do dataset é versionada e enviada ao Hugging Face com:
- Hash SHA-256 para integridade
- Changelog de alterações
- Métricas de qualidade

## Pipeline

Este diretório é a **Etapa 3** do pipeline de processamento:
```
2-Chunks → [Geração Q/A] → 3-FinalDataset → [Validação] → 4-Benchmarks
```

## Scripts Relacionados

- `scripts/03_generate_examples.py` - Geração sintética com LLMs
- `scripts/04_validate_quality.py` - Validação de qualidade
- `scripts/05_export_to_jsonl.py` - Exportação para JSONL
- `scripts/deploy_to_hf.py` - Deploy para Hugging Face
