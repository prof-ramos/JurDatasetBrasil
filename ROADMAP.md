# Roadmap: JurDatasetBrasil 2026

Este documento define o plano de execução para a criação do maior dataset jurídico aberto do Brasil, conforme o [PRD 2.0](PRD.md). As tarefas estão organizadas por fases temporais, permitindo o acompanhamento do progresso e a garantia de qualidade.

> **Objetivo Final:** 300.000+ exemplos validados até Maio/2027.

---

## 🏗️ Fase 0: Infraestrutura e MVP (Dez/2025)
**Meta:** Infraestrutura operacional e Dataset MVP da Lei 9.784/99 (12k exemplos).

### Infraestrutura & Setup
- [ ] Configurar ambiente de desenvolvimento (Python, Docker, Pre-commit hooks)
- [ ] Configurar chaves de API e variáveis de ambiente (`.env`)
- [ ] Criar estrutura de diretórios (`0-RawDocs`, `1-MarkdownClean`, etc.)
- [ ] Configurar repositório no Hugging Face (Privado)

### Pipeline de Ingestão (RF01)
- [ ] Implementar script de conversão Docling (PDF/Docx → Markdown)
- [ ] Implementar limpeza e normalização de Markdown
- [ ] Implementar extrator de estrutura (Lei, Artigo, Parágrafo)

### Pipeline de Processamento (RF07)
- [ ] Implementar Chunking (1-2k tokens)
- [ ] Implementar geração de Embeddings (pgvector)
- [ ] Criar esquema do banco de dados (Tabelas: laws, articles, chunks)

### Geração e Qualidade (RF02, RF04)
- [ ] Desenvolver prompts para geração de Q/A (Grok/Gemini)
- [ ] Implementar script de geração sintética
- [ ] Implementar validador de schema JSONL
- [ ] Implementar deduplicação de exemplos

### Entrega MVP (Lei 9.784/99)
- [ ] Ingestão da Lei 9.784/99
- [ ] Geração de 12.000 exemplos
- [ ] Validação preliminar e correção de erros
- [ ] Upload da versão v0.1 para Hugging Face (Privado) (RF03)
- [ ] Criar Dashboard simples de progresso (RF05)

---

## 🚀 Fase 1: Direito Administrativo e Expansão (Jan–Mar/2026)
**Meta:** 50.000 exemplos totais. Cobertura completa de Direito Administrativo.

### Expansão do Dataset
- [ ] Ingestão: Lei 8.112/90 (Regime Jurídico dos Servidores)
- [ ] Ingestão: Lei 8.429/92 (Improbidade Administrativa)
- [ ] Ingestão: Lei 13.655/18 (LINDB)
- [ ] Ingestão: Lei 14.133/21 (Licitações) e decretos regulamentadores
- [ ] Geração e validação de 38k novos exemplos

### Melhorias do Sistema
- [ ] Otimizar pipeline para escalar para 100+ leis (RF07)
- [ ] Implementar Rastreabilidade completa (Lei → Chunk → Exemplo) (RF08)
- [ ] Fine-tuning do modelo baseline `JurLM-Admin-8B`
- [ ] Publicação do modelo no Hugging Face

---

## ⚖️ Fase 2: Constitucional e Tributário (Abr–Jul/2026)
**Meta:** 60.000 exemplos acumulados (+10k). Início de matérias complexas.

### Novas Matérias
- [ ] Ingestão: Constituição Federal (CF/88)
- [ ] Ingestão: Código Tributário Nacional (CTN) e leis complementares
- [ ] Refinamento de prompts para Direito Constitucional (foco em princípios)

### Funcionalidades Avançadas
- [ ] Implementar "Law Diff" (Detecção de alterações legislativas)
- [ ] Implementar Benchmark Automático (RF09)
- [ ] Testes de regressão por lei

---

## 🔒 Fase 3: Penal e Processo Penal (Ago–Dez/2026)
**Meta:** 70.000 exemplos acumulados (+10k). Matérias de alta sensibilidade.

### Novas Matérias
- [ ] Ingestão: Código Penal (CP)
- [ ] Ingestão: Código de Processo Penal (CPP)
- [ ] Ingestão: Leis Penais Especiais (Drogas, Maria da Penha, etc.)

### Qualidade e Governança
- [ ] Refinamento de prompts para casos complexos e tipificação penal
- [ ] Auditoria de viés e segurança nos exemplos gerados
- [ ] Expansão do Dashboard (Métricas detalhadas de qualidade)

---

## 🌐 Fase 4: Consolidação e Escala (Jan–Mai/2027)
**Meta:** 300.000+ exemplos. Cobertura de 8 matérias principais.

### Escala Massiva
- [ ] Ingestão: Código Civil (CC)
- [ ] Ingestão: Código de Processo Civil (CPC)
- [ ] Ingestão: Código de Defesa do Consumidor (CDC)
- [ ] Ingestão: Consolidação das Leis do Trabalho (CLT)
- [ ] Ingestão: Legislação Ambiental

### Finalização e Lançamento
- [ ] Validação final de acurácia (Meta: ≥ 94% em CESPE/FGV)
- [ ] Release Pública Final do Dataset (CC-BY-4.0) (RF06)
- [ ] Documentação técnica completa e relatórios de auditoria
- [ ] Divulgação para a comunidade (Papers, Blog posts)

---

## 🔮 Futuro e Perspectivas (Pós-V2.0)
- [ ] **JurBenchmark:** Criação de um benchmark unificado de raciocínio jurídico.
- [ ] **Auditoria Multi-modelo:** Sistema de consenso entre Grok, Gemini e Llama.
- [ ] **Dataset Híbrido:** Inclusão de jurisprudência e peças processuais reais.
- [ ] **Modelos Soberanos:** Treinamento de modelos de 70B parâmetros especializados.
