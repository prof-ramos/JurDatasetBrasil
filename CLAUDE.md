# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language & Communication

**IMPORTANT:** All interactions with users, documentation, comments, commit messages, and project materials must be in Brazilian Portuguese (pt-BR). This is a Brazilian legal project, and maintaining Portuguese throughout ensures accessibility for the target audience and stakeholders.

## Project Overview

**JurDatasetBrasil** is an ambitious open-source project to create Brazil's largest legal dataset for training and evaluating LLMs. The project aims to deliver 300,000+ training examples in Alpaca/ShareGPT format, covering 8+ areas of Brazilian law, with complete traceability from legal sources to examples.

**Target completion:** May 2027 | **MVP:** 12,000 examples from Lei 9.784/99

## Core Architecture

The project uses a unified Postgres/Supabase schema with pgvector that serves three purposes simultaneously:
1. **LLM Training** - instruction/input/output format examples
2. **Classic RAG** - semantic search over legal texts (laws, articles)
3. **Case-based RAG** - few-shot learning via example similarity

### Data Flow Pipeline (6 Stages)

```
Raw Docs → Cleaning → Chunking → Generation → Quality → Publication
(0-RawDocs)  (1-MarkdownClean)  (2-Chunks)  (3-FinalDataset)  (4-Benchmarks)  (HF/Git)
```

**Stage details:**
- **0-RawDocs/**: Original PDF/DOCX files before processing
- **1-MarkdownClean/**: Cleaned markdown via Docling
- **2-Chunks/**: Text chunks (~1-2k tokens) with embeddings for RAG
- **3-FinalDataset/**: JSONL files ready for training (Alpaca/ShareGPT format)
- **4-Benchmarks/**: Validation against CESPE/FGV exam questions
- **5-Models/**: Fine-tuned models (7B-70B)
- **logs/**: Pipeline execution logs
- **scripts/**: Automation scripts for ingest, chunking, validation

### Database Schema (SCHEMA.md)

Five core tables form the unified model:

1. **`laws`** - Normative sources (law_number, law_type, title, year, jurisdiction)
2. **`articles`** - Internal law structure (article_ref, full_text, structure_json)
3. **`chunks`** - RAG layer with embeddings (content, embedding vector(1536), metadata)
4. **`datasets`** - Version control (name, version, split: train/validation/test)
5. **`examples`** - Training examples (instruction, input, output, embedding, chunk_ids)

**Key relationships:**
- `examples.chunk_ids[]` → `chunks.id` (traceability)
- `examples.law_id` → `laws.id` (source attribution)
- `chunks.embedding` and `examples.embedding` enable dual RAG modes

## Project Constraints

- **Budget:** ≤ R$500/month for APIs and infrastructure
- **Privacy:** Use HF Pro for private releases until human review
- **Quality bar:** CESPE/FGV exam-level accuracy (target: ≥94%)
- **Rastreability:** Every example must trace back to source law/article/chunks
- **Performance:** 10,000 examples/hour processing target

## Key Technologies

- **Docling:** PDF/DOCX to clean markdown conversion
- **LLMs:** Gemini 2.5 Flash and Grok 4.1 Fast for synthetic Q/A generation
- **Storage:** Postgres/Supabase with pgvector extension
- **Embeddings:** 1536-dimension vectors (check encoder model)
- **Versioning:** Git + Hugging Face Datasets
- **Indexing:** IVFFLAT (lists=100) for vector search optimization

## Development Workflow

Since scripts/ is currently empty and no automation exists yet:

1. **Adding new laws:** Place raw documents in `0-RawDocs/`
2. **Markdown conversion:** Use Docling to generate files in `1-MarkdownClean/`
3. **Chunking:** Split into ~1-2k token chunks, save to `2-Chunks/`
4. **Example generation:** Use restrictive prompts with LLMs to create Q/A pairs
5. **Quality validation:** Deduplicate, validate JSON schema, cross-check with multiple LLMs
6. **Export to JSONL:** Save to `3-FinalDataset/` with metadata including:
   - `law_number`, `article_ref`, `source_chunks[]`
   - `difficulty`, `exam_board`, `exam_year`, `area`
   - `instruction`, `input`, `output`

## JSONL Format Example

```jsonl
{
  "instruction": "Explique o conceito de ato administrativo vinculado...",
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

## Quality Standards

- **Deduplication:** Detect and remove duplicate examples
- **Schema validation:** Strict JSONL schema enforcement
- **Multi-LLM validation:** Cross-check answers using Grok + Gemini
- **Pilot testing:** Validate 100-500 examples before full generation
- **Benchmark testing:** Test against real CESPE/FGV questions in `4-Benchmarks/`

## Roadmap Phases

- **F0 (Dec 2025):** Infrastructure + Lei 9.784/99 → 12k examples (MVP)
- **F1 (Jan-Mar 2026):** Complete Administrative Law → 50k examples
- **F2 (Apr-Jul 2026):** Constitutional + Tax Law → 60k cumulative
- **F3 (Aug-Dec 2026):** Criminal Law + Procedure → 70k cumulative
- **F4 (Jan-May 2027):** Civil, Consumer, Labor, Environmental → 300k+ examples

## Critical Design Decisions

**Why unified schema?** Single logical database for training, classic RAG, and case-similarity RAG reduces duplication and maintains traceability.

**Why chunk embeddings AND example embeddings?**
- `chunks.embedding` → retrieve relevant legal text
- `examples.embedding` → retrieve similar questions for few-shot learning

**Why IVFFLAT indexing?** Balance between search speed and accuracy at scale. Calibrate `lists` parameter based on dataset size.

**Why offline-first pipeline?** Security, cost control (batch processing in off-peak hours), and reproducibility.

## Known Risks & Mitigations

- **R1 - Poor OCR quality:** Use Docling + manual review for critical articles
- **R2 - LLM hallucinations:** Restrictive prompts + multi-LLM validation + pilot tests
- **R3 - Semantic errors:** Article-level revalidation + human sampling
- **R4 - Version conflicts:** SHA hashing + `datasets.version` + Law Diff automation
- **R5 - Embedding costs:** Optimize dimensions, use IVFFLAT pruning, batch scheduling
- **R6 - Scale to 300k:** Batch orchestration, parallelism, throughput monitoring

## License & Distribution

- **Dataset:** CC-BY-4.0 (open, with attribution)
- **Scripts:** MIT License
- **Distribution:** Private HF releases → Human audit → Public release
- **Dashboard:** Public progress tracking (laws, versions, splits, quality metrics)

## References

- Full requirements: `PRD.md` (sections 7-8)
- Database design: `SCHEMA.md` (tables + SQL examples)
- Project vision: `README.md`
- Architectural trade-offs: `PRD.md` (section 9, 12)
