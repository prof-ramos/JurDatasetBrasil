# PRD 2.0 — JurDatasetBrasil 2026

> O maior dataset jurídico aberto do Brasil para treinamento de LLMs.
> Versão 2.0 – Dez/2025 | Autor: prof-ramos + Gepeteco Estaloprando | Status: Executive-Ready

## Sumário
- [1. Contexto e Problema](#1-contexto-e-problema)
- [2. Visão e Posicionamento](#2-visão-e-posicionamento)
- [3. Objetivos e KPIs](#3-objetivos-e-kpis)
- [4. Escopo e Entregáveis](#4-escopo-e-entregáveis)
- [5. Stakeholders e Personas](#5-stakeholders-e-personas)
- [6. Restrições e Hipóteses](#6-restrições-e-hipóteses)
- [7. Requisitos Funcionais](#7-requisitos-funcionais)
- [8. Requisitos Não Funcionais](#8-requisitos-não-funcionais)
- [9. Arquitetura e Pipeline](#9-arquitetura-e-pipeline)
- [10. Governança de Dados](#10-governança-de-dados)
- [11. Cronograma](#11-cronograma)
- [12. Riscos, Trade-offs e Mitigações](#12-riscos-trade-offs-e-mitigações)
- [13. Custos e Licenciamento](#13-custos-e-licenciamento)
- [14. Linha de Chegada e Critérios de Sucesso](#14-linha-de-chegada-e-critérios-de-sucesso)
- [15. Perspectivas e Próximos Passos](#15-perspectivas-e-próximos-passos)

---

## 1. Contexto e Problema
**Núcleo do problema.** O ecossistema brasileiro carece de datasets jurídicos estruturados, amplos e confiáveis, alinhados a formatos modernos de LLM. O resultado são modelos globais que não compreendem com profundidade legislação, jurisprudência e prática forense nacionais.

**Consequência primária.** Falta de soberania tecnológica em IA jurídica e dependência de APIs externas caras, com pouca auditabilidade.

**Fatores críticos (Efeito de segunda ordem).**
- Qualidade > quantidade: exemplos precisam ter nível CESPE/FGV.
- Transparência e rastreabilidade ponta-a-ponta são mandatórias.
- Pipeline deve escalar para 100+ leis sem refatorações.
- Revisão humana estratégica continua essencial mesmo com IA.

## 2. Visão e Posicionamento
**Declaração de visão.** Criar até maio/2027 o dataset jurídico em português mais completo, aberto e auditável do mundo, servindo como base soberana para LLMs nacionais, referência acadêmica e recurso público gratuito de ensino jurídico.

**Produto final (linha de chegada).** 300.000+ exemplos compatíveis com Alpaca/ShareGPT, balanceados, limpos e versionados em Git + Hugging Face Datasets, acompanhados de scripts de ingestão, validação e benchmark.

**Proposta de valor multidimensional.**
- **Acadêmico:** referência internacional em datasets legislativos estruturados.
- **Mercado:** acelera modelos 7B–70B especializados em Direito brasileiro.
- **Societal:** reduz custo de preparação para concursos/OAB e amplia acesso.

## 3. Objetivos e KPIs
| Métrica | Meta Intermediária (mai/26) | Meta Final (mai/27) |
| --- | --- | --- |
| Total de exemplos validados | ≥ 100.000 | ≥ 300.000 |
| Matérias completas | 4 | 8 |
| Acurácia em provas CESPE/FGV | ≥ 90% | ≥ 94% |
| Downloads no HF | ≥ 10.000 | ≥ 50.000 |
| Modelos derivados (7B–70B) | ≥ 5 | ≥ 15 |
| Tempo médio por lei (pipeline) | ≤ 48h | ≤ 24h |
| Automação do pipeline | ≥ 70% | ≥ 85% |

## 4. Escopo e Entregáveis
**Incluído.**
- Dataset final em JSONL padronizado (Alpaca/ShareGPT) com rastreabilidade.
- Scripts de geração, limpeza, chunking, deduplicação e validação.
- Dashboard público de progresso (versões, leis, splits) e alertas de qualidade.
- Modelos baseline (7B, 13B, 70B) fine-tunados no dataset.

**MVP.** 12.000 exemplos da Lei 9.784/99, pipeline completo docx → JSONL → validação, release privada no HF.

**Fora de escopo imediato.**
- Captura automatizada de jurisprudência completa (entrará como expansão). 
- Ferramentas de anotação humana customizadas (usar soluções existentes no curto prazo).

## 5. Stakeholders e Personas
- **Estudantes e profissionais** (OAB, concursos, prática forense).
- **Pesquisadores/Universidades** (IA aplicada ao Direito).
- **Labs e empresas de IA** (fine-tuning e produtos jurídicos).
- **Instituições públicas** (CNJ, AGU, MPs, tribunais).
- **Comunidade open-source** (Hugging Face, contribuidores).

## 6. Restrições e Hipóteses
- **Orçamento:** ≤ R$ 500/mês em APIs/infra. Execuções pesadas em janelas noturnas para tarifas reduzidas.
- **Dependências:** Docling para parsing, Gemini 2.5 Flash e Grok 4.1 Fast para geração, HF Pro para privacidade inicial.
- **Direitos autorais:** atenção a PDFs de terceiros e jurisprudência; priorizar fontes públicas oficiais.
- **Rastreabilidade obrigatória:** hashes e versões por lei/artigo/chunk.

## 7. Requisitos Funcionais
| ID | Requisito | Prioridade |
| --- | --- | --- |
| RF01 | Conversão docx/pdf → markdown limpo (Docling) | Must |
| RF02 | Geração automática de Q/A padrão Alpaca/ShareGPT | Must |
| RF03 | Versionamento Git + HF (privado → público) | Must |
| RF04 | Validador automático JSONL + deduplicação | Must |
| RF05 | Dashboard público de progresso | Should |
| RF06 | Licenças abertas + camada gated premium | Must |
| RF07 | Pipeline de chunking escalável para 100+ leis | Must |
| RF08 | Auditoria e rastreabilidade por lei/versão | Should |
| RF09 | Benchmark automático do modelo | Should |

## 8. Requisitos Não Funcionais
- Performance: 10.000 exemplos/hora (meta operacional).
- Segurança: releases privadas no HF Pro até revisão humana.
- Resiliência: pipeline 100% offline quando necessário.
- Padronização rígida de outputs (JSON schema + lint de markdown).
- Custo controlado: ≤ R$ 500/mês.

## 9. Arquitetura e Pipeline
**Arquitetura lógica (camadas).**
1. **Ingestão:** Raw docs → Docling → Markdown limpo.
2. **Normalização:** limpeza semântica, estruturação por artigo, metadados.
3. **Chunking:** divisão em ~1–2k tokens; embeddings (pgvector) para RAG clássico.
4. **Geração:** prompts restritivos + exemplos de alta precisão → Q/A sintético.
5. **Qualidade:** deduplicação, validação de schema, checagem cruzada multi-LLM.
6. **Publicação:** versionamento Git + HF; dashboards e relatórios.
7. **Benchmark:** avaliação piloto (100–500 exemplos) + testes regressivos por lei.

**Referência de schema.** O armazenamento unificado usa as tabelas `laws`, `articles`, `chunks`, `examples` e `datasets` descritas em [`SCHEMA.md`](SCHEMA.md), permitindo RAG tradicional (fontes normativas) e RAG por similaridade de casos.

**Trade-offs arquiteturais.**
- **Granularidade de chunk (1–2k tokens):** melhora precisão de RAG; aumenta volume de vetores. Mitigação: índices IVFFLAT calibrados e pruning por área temática.
- **Embedding em `examples`:** eleva custo de armazenamento, mas habilita few-shot automático e avaliação de similaridade pedagógica.
- **Pipelines offline:** mais seguros, porém exigem agendamento cuidadoso para custo/tempo; priorizar execuções batch.

## 10. Governança de Dados
- **Rastreabilidade:** cada exemplo mapeia `instruction/input/output` a `chunk_ids`, `article_id` e `law_id`.
- **Versão/split:** tabela `datasets` com `name`, `version`, `split` e descrição.
- **Qualidade:** métricas por lei (densidade de chunks, % de exemplos validados, cobertura por artigo).
- **Auditoria:** hashes de origem, changelog por lei, alertas para divergências de versão.

## 11. Cronograma
**Fases macro (2025–2027).**
- F0 (Dez/25): Infra e Lei 9.784/99 → 12k exemplos validados.
- F1 (Jan–Mar/26): Direito Administrativo completo → 50k exemplos.
- F2 (Abr–Jul/26): Constitucional + Tributário → 60k cumulativo.
- F3 (Ago–Dez/26): Penal + Processo Penal → 70k cumulativo.
- F4 (Jan–Mai/27): Civil, Consumidor, Trabalho, Ambiental → 300k+ exemplos.

**Plano executivo 90 dias.**
| Semana | Meta | Entrega |
| --- | --- | --- |
| 1 | Infra + Lei 9.784/99 | 12k exemplos + README revisado |
| 2–4 | Leis 8.112/90, 8.429/92, 13.655/18 | +25k exemplos |
| 5–8 | Lei 14.133/21 + decretos | 50k+ dataset |
| 9–12 | Release privada + JurLM-Admin-8B | Modelo no HF |

## 12. Riscos, Trade-offs e Mitigações
| ID | Risco / Trade-off | Impacto | Mitigação |
| --- | --- | --- | --- |
| R1 | Baixa qualidade de PDFs escaneados | Alto | OCR + Docling + revisão manual para artigos críticos |
| R2 | Alucinações em Q/A sintético | Alto | Prompt restritivo, validação cruzada (Grok + Gemini), testes piloto |
| R3 | Erros semânticos em artigos complexos | Médio | Revalidação automática por artigo e amostragem humana |
| R4 | Múltiplas versões de lei/artigo | Médio | Hash + `datasets.version`; diff automático (“Law Diff”) |
| R5 | Custo de embeddings/armazenamento | Médio | Calibrar dimensão/listas IVFFLAT, compressão, agendamento batch |
| R6 | Escalabilidade a 300k exemplos | Alto | Orquestração em batches, paralelismo e monitoramento de throughput |

## 13. Custos e Licenciamento
- **Custos operacionais:** budget mensal ≤ R$ 500 (APIs + storage). Otimizar janelas de execução e reuso de embeddings.
- **Licenças:** Dataset → CC-BY-4.0; Scripts → MIT. Releases públicas somente após auditoria.

## 14. Linha de Chegada e Critérios de Sucesso
- Dataset ≥ 300k exemplos validados, cobrindo 8 matérias centrais.
- Benchmarks com acurácia ≥ 94% em provas CESPE/FGV.
- Downloads ≥ 50k no HF; ≥ 15 modelos derivados open-source.
- Dashboard público com rastreabilidade completa (lei → chunks → exemplos → versões).

## 15. Perspectivas e Próximos Passos
1. **JurBenchmark:** benchmark público de questões jurídicas brasileiras com score unificado de legal reasoning.
2. **Auditoria multi-modelo:** consenso Grok + Gemini + LLaMA open-source.
3. **Law Diff:** detecção automática de alterações legislativas com atualização incremental de chunks e exemplos.
4. **Dataset híbrido:** literalidade da lei + casos hipotéticos + questões CESPE/FGV + prática forense sintética.
5. **Modelos soberanos:** roadmap para modelos 70B especializados no Brasil.

---

**Nível de confiança:** 87%. **Potencial transformador:** extremamente alto. Este PRD consolida governança, rastreabilidade e estratégia para escalar o JurDatasetBrasil a um padrão internacional.
