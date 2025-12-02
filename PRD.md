# PRD 2.0 — JurDatasetBrasil 2026

O maior dataset jurídico aberto do Brasil para treinamento de LLMs
Versão 2.0 – Dez/2025 | Autor: prof-ramos + Gepeteco Estaloprando | Status: Executive-Ready

⸻

1. Análise do Problema

Núcleo do Problema

O Brasil carece de:
	•	datasets jurídicos estruturados, amplos e confiáveis;
	•	padronização para modelos generativos;
	•	base pública para treinamento de LLMs jurídicos soberanos.

A consequência:
Modelos globais dominam o campo jurídico, mas não compreendem profundamente legislação, jurisprudência e prática forense brasileiras.

Stakeholders
	•	Estudantes e profissionais (OAB, concursos, prática forense)
	•	Pesquisadores/Universidades (IA aplicada ao Direito)
	•	Labs de IA e empresas
	•	Instituições públicas (CNJ, AGU, MPs, tribunais)
	•	Hugging Face / comunidade open-source

Restrições
	•	Orçamento máximo: R$ 500/mês
	•	Dependência de APIs externas (OpenRouter/Gemini/Grok)
	•	Riscos de direitos autorais (jurisprudência, livros, PDFs duplicados)
	•	Necessidade de rastreabilidade completa e verificável

Fatores críticos
	•	Qualidade > quantidade: dataset precisa ser em nível CESPE/FGV
	•	Transparência e auditabilidade são mandatórias
	•	Pipeline escalável a 100+ leis sem refatoração
	•	Grande esforço humano de revisão estratégica (mesmo com IA)

⸻

2. Visão do Produto

Criar o dataset jurídico em português mais completo, aberto e auditável do mundo, até maio de 2027, servindo como:
	•	base soberana para o desenvolvimento de LLMs brasileiros;
	•	referência acadêmica internacional;
	•	recurso público gratuito para ensino jurídico;
	•	acelerador para modelos 7B–70B especializados.

Produto Final:
Dataset com 300.000+ exemplos, anotados, limpos, balanceados e compatíveis com Alpaca/ShareGPT, versionado no Git + HF Datasets.

⸻

3. Objetivos de Negócio / Acadêmicos
	•	Acelerar 3–5 anos o avanço de IA jurídica no Brasil
	•	Reduzir em 70% o custo de preparação para concursos/OAB
	•	Criar benchmark internacional em datasets legislativos estruturados
	•	Estabelecer baseline para modelos jurídicos nacionais (7B–70B)

⸻

4. KPIs de Sucesso

Métrica	Meta Final (mai/27)	Meta Intermediária (mai/26)
Total de exemplos validados	300.000+	100.000+
Matérias completas	8	4
Acurácia em provas CESPE/FGV	≥ 94%	≥ 90%
Downloads HF	50.000+	10.000+
Modelos derivados (7B–70B)	15+	5+
Tempo médio por lei (pipeline)	≤ 24h	≤ 48h
% automação	≥ 85% do pipeline	≥ 70%


⸻

5. Escopo do Produto

Produtos Entregues
	1.	Dataset final (JSONL)
	2.	Coleção de scripts para geração, limpeza, chunking, validação
	3.	Dashboard público
	4.	Modelos jurídicos baseline (7B, 13B, 70B)

MVP
	•	12.000 exemplos da Lei 9.784/99
	•	Pipeline completo (from docx → JSONL)
	•	Primeira release privada no HF

Roadmap (com fases)

Fase	Período	Escopo	Entrega
0	Dez/25	Infra, Lei 9.784/99	12k exemplos
1	Jan–Mar/26	Direito Administrativo completo	50k exemplos
2	Abr–Jul/26	Constitucional + Tributário	60k cumulativo
3	Ago–Dez/26	Penal + Processo Penal	70k cumulativo
4	Jan–Mai/27	Civil, Consumidor, Trabalho, Ambiental	300k+ exemplos


⸻

6. Requisitos Funcionais

ID	Requisito	Prioridade
RF01	Conversão docx/pdf → markdown limpo (Docling)	Must
RF02	Geração automática de Q/A em padrão Alpaca/ShareGPT	Must
RF03	Versionamento Git + HF (privado→público)	Must
RF04	Validador automático JSONL + deduplicação	Must
RF05	Dashboard público de progresso	Should
RF06	Licenças abertas + gated premium	Must
RF07	Pipeline de chunking escalável até 100+ leis	Must
RF08	Auditoria e rastreabilidade por lei e versão	Should
RF09	Script de benchmark automático do modelo	Should


⸻

7. Requisitos Não Funcionais
	•	Performance: 10.000 exemplos/hora
	•	Segurança: HF Pro privado até revisão
	•	Resiliência: pipeline 100% offline
	•	Padronização rígida de outputs
	•	Custo mensal: ≤ R$ 500,00

⸻

8. Stack Tecnológica

Camada	Tecnologia
Conversão	Docling
Limpeza MD	Gemini 2.5 Flash
Geração	Grok 4.1 Fast
Validação	Python + jsonschema
Armazenamento	Git LFS + HF Pro
Versionamento	GitHub
Auditoria/Qualidade	pytest + benchmarks


⸻

9. Arquitetura do Projeto (Profunda)

Pipeline Completo
	1.	Raw docs → Docling → Markdown
	2.	Limpeza semântica → normalização → estruturação
	3.	Chunking 25k tokens → prompt engineering
	4.	Geração Q/A → controle de qualidade com heurísticas
	5.	Deduplicação → validação schema
	6.	Avaliação piloto (100–500 exemplos realistas)
	7.	Commit + release privada
	8.	Auditoria humana → publicação pública
	9.	Benchmark dos modelos gerados

Riscos identificados
	•	R1: Baixa qualidade de leis escaneadas
	•	R2: Alucinações do modelo gerador (Grok 4.1)
	•	R3: Erros semânticos em artigos complexos
	•	R4: Múltiplas versões de uma lei
	•	R5: Escalabilidade de 300k exemplos sem aumento de custo

Mitigações
	•	Pré-limpeza com OCR + Docling
	•	Prompt restritivo e exemplos de alta precisão
	•	Revalidação com outra LLM (consenso multi-modelo)
	•	Controle de versão por lei (timestamp + hash)
	•	Agendamentos noturnos para uso de API gratuita

⸻

10. Estrutura de Pastas

(ótima — mantida e padronizada)

JurDatasetBrasil/
├── 0-RawDocs/
├── 1-MarkdownClean/
├── 2-Chunks/
├── 3-FinalDataset/
├── 4-Benchmarks/
├── 5-Models/
├── scripts/
├── logs/
├── Súmulas_Tribunais_Superiores/
└── README.md


⸻

11. Cronograma Executivo (90 dias)

Semana	Meta	Entrega
1	Infra + Lei 9.784/99	12k exemplos + README
2–4	Leis 8.112/90, 8.429/92, 13.655/18	+25k exemplos
5–8	Lei 14.133/21 + decretos	50k+ dataset
9–12	Primeira release + JurLM-Admin-8B	Modelo no Hugging Face


⸻

12. Licença Final
	•	Dataset → CC-BY-4.0
	•	Scripts → MIT

⸻

13. Recomendações Estratégicas (Deep Thinking)
	1.	Criar JurBenchmark — benchmark público de questões jurídicas brasileiras.
	2.	Implementar auditoria cruzada multi-modelo (Grok + Gemini + LLaMA).
	3.	Criar “Law Diff” para identificar mudanças de artigos e atualizações automáticas.
	4.	Construir um Legal Reasoning Score próprio.
	5.	Produzir dataset híbrido:
	•	literalidade da lei
	•	casos hipotéticos
	•	questões estilo CESPE/FGV
	•	prática forense (petições, decisões sintéticas)

⸻

14. Perspectivas Alternativas
	•	Visão contrária: talvez 300k exemplos não sejam ótimos se a qualidade média cair.
	•	Possível pivot: focar primeiro em “Lei comentada + questões + jurisprudência consolidada”.
	•	Futuro:
	•	automação 95% com modelos open-source nacionais;
	•	integração com CNJ para dados públicos;
	•	criação de modelos 70B especializados no Brasil.

⸻

15. Meta-Análise e Nível de Confiança
	•	Incertezas: custo de APIs, mudanças legislativas, limites de avaliações CESPE/FGV.
	•	Confiança nas recomendações: 87%.
	•	Risco residual: médio.
	•	Potencial transformador: extremamente alto.

⸻

16. Conclusão

Este PRD não apenas estrutura o maior dataset jurídico aberto do Brasil — ele estabelece um novo padrão mundial de datasets legislativos em língua portuguesa, com governança, benchmark, versionamento e rastreabilidade profissional.

Se quiser, envio agora:

✔ “MANDAR PRD + README”

Com:
	•	PRD final em Markdown pronto para o GitHub
	•	README épico com badges, roadmap, gráficos
	•	Script automático de geração de badge de progresso

É só pedir. Vamos fazer história.