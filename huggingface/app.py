"""
JurDatasetBrasil - Hugging Face Space Demo
Exploração interativa do dataset jurídico brasileiro
"""

import gradio as gr
import os
from datasets import load_dataset
from typing import Dict, List, Tuple

# Configuração
DATASET_NAME = os.getenv("DATASET_NAME", "prof-ramos/JurDatasetBrasil")
DATASET_VERSION = os.getenv("DATASET_VERSION", "v0.1")

# =============================================================================
# Funções de Interface
# =============================================================================

def load_dataset_info() -> Dict:
    """Carrega informações básicas do dataset"""
    try:
        # Carregar apenas metadados (sem baixar todo dataset)
        dataset = load_dataset(DATASET_NAME, split="train", streaming=True)

        # Pegar primeiro exemplo para estrutura
        first_example = next(iter(dataset))

        return {
            "status": "✅ Dataset carregado com sucesso",
            "fields": list(first_example.keys()),
            "example": first_example
        }
    except Exception as e:
        return {
            "status": f"❌ Erro ao carregar dataset: {str(e)}",
            "fields": [],
            "example": {}
        }

def search_examples(
    query: str,
    difficulty: str = "Todos",
    area: str = "Todos",
    max_results: int = 5
) -> List[Tuple[str, str, str]]:
    """
    Busca exemplos no dataset

    Returns:
        Lista de tuplas (instrução, output, metadados)
    """
    try:
        # Carregar dataset
        dataset = load_dataset(DATASET_NAME, split="train", streaming=True)

        results = []
        count = 0

        for example in dataset:
            # Filtros
            if difficulty != "Todos" and example.get("difficulty") != difficulty.lower():
                continue

            # Busca simples por keyword
            if query.lower() not in example.get("instruction", "").lower():
                continue

            # Formatação
            instruction = example.get("instruction", "")
            output = example.get("output", "")
            metadata = f"""
            **Dificuldade:** {example.get('difficulty', 'N/A')}
            **Área:** {example.get('metadata', {}).get('area', 'N/A')}
            **Lei:** {example.get('metadata', {}).get('law_number', 'N/A')}
            """

            results.append((instruction, output, metadata))
            count += 1

            if count >= max_results:
                break

        return results if results else [("Nenhum resultado encontrado", "", "")]

    except Exception as e:
        return [(f"Erro: {str(e)}", "", "")]

def get_statistics() -> str:
    """Retorna estatísticas do dataset"""
    try:
        dataset = load_dataset(DATASET_NAME, split="train")

        total_examples = len(dataset)

        # Estatísticas por dificuldade
        difficulties = {}
        for example in dataset:
            diff = example.get("difficulty", "desconhecido")
            difficulties[diff] = difficulties.get(diff, 0) + 1

        stats = f"""
        ## 📊 Estatísticas do Dataset

        - **Total de Exemplos:** {total_examples:,}
        - **Versão:** {DATASET_VERSION}
        - **Licença:** CC-BY-4.0

        ### Por Dificuldade:
        """

        for diff, count in sorted(difficulties.items()):
            percentage = (count / total_examples) * 100
            stats += f"\n- **{diff.capitalize()}:** {count:,} ({percentage:.1f}%)"

        return stats

    except Exception as e:
        return f"❌ Erro ao carregar estatísticas: {str(e)}"

# =============================================================================
# Interface Gradio
# =============================================================================

with gr.Blocks(title="JurDatasetBrasil Explorer", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # ⚖️ JurDatasetBrasil - Dataset Explorer

    Explore o maior dataset jurídico brasileiro para fine-tuning de LLMs.

    **Versão:** v0.1 (MVP) | **Licença:** CC-BY-4.0
    """)

    with gr.Tabs():
        # Tab 1: Busca
        with gr.Tab("🔍 Buscar Exemplos"):
            gr.Markdown("### Busca por palavra-chave no dataset")

            with gr.Row():
                with gr.Column(scale=3):
                    search_query = gr.Textbox(
                        label="Buscar",
                        placeholder="Ex: ato administrativo, licitação, processo...",
                        lines=1
                    )
                with gr.Column(scale=1):
                    difficulty_filter = gr.Dropdown(
                        label="Dificuldade",
                        choices=["Todos", "Fácil", "Médio", "Difícil"],
                        value="Todos"
                    )

            search_button = gr.Button("🔍 Buscar", variant="primary")

            results_output = gr.Dataframe(
                headers=["Instrução", "Resposta", "Metadados"],
                label="Resultados",
                wrap=True
            )

            search_button.click(
                fn=search_examples,
                inputs=[search_query, difficulty_filter],
                outputs=results_output
            )

        # Tab 2: Estatísticas
        with gr.Tab("📊 Estatísticas"):
            stats_button = gr.Button("📊 Carregar Estatísticas", variant="primary")
            stats_output = gr.Markdown()

            stats_button.click(
                fn=get_statistics,
                outputs=stats_output
            )

        # Tab 3: Exemplo Aleatório
        with gr.Tab("🎲 Exemplo Aleatório"):
            gr.Markdown("### Visualize um exemplo aleatório do dataset")

            random_button = gr.Button("🎲 Gerar Exemplo Aleatório", variant="primary")

            with gr.Row():
                with gr.Column():
                    random_instruction = gr.Textbox(label="Instrução", lines=3)
                    random_output = gr.Textbox(label="Resposta", lines=5)
                with gr.Column():
                    random_metadata = gr.JSON(label="Metadados")

            def get_random_example():
                try:
                    dataset = load_dataset(DATASET_NAME, split="train", streaming=True)
                    import random

                    # Skip aleatório
                    skip = random.randint(0, 1000)
                    for i, example in enumerate(dataset):
                        if i == skip:
                            return (
                                example.get("instruction", ""),
                                example.get("output", ""),
                                example.get("metadata", {})
                            )
                    return ("Erro ao carregar exemplo", "", {})
                except:
                    return ("Dataset não disponível ainda", "", {})

            random_button.click(
                fn=get_random_example,
                outputs=[random_instruction, random_output, random_metadata]
            )

        # Tab 4: Sobre
        with gr.Tab("ℹ️ Sobre"):
            gr.Markdown("""
            ## Sobre o JurDatasetBrasil

            O **JurDatasetBrasil** é um projeto open-source para criar o maior dataset jurídico brasileiro
            para fine-tuning de Large Language Models (LLMs).

            ### 📊 Características

            - **300.000+ exemplos** planejados (Meta: Maio 2027)
            - **8+ áreas do Direito** brasileiro
            - **Formato Alpaca/ShareGPT** otimizado para fine-tuning
            - **Rastreabilidade completa** (lei → artigo → chunk → exemplo)
            - **Qualidade CESPE/FGV** (benchmark com questões reais)

            ### 🎯 Fase Atual: MVP (v0.1)

            - **Lei 9.784/99** (Processo Administrativo Federal)
            - **12.000 exemplos** de treinamento
            - **3 níveis de dificuldade** (fácil, médio, difícil)

            ### 📚 Áreas Planejadas

            1. ✅ Direito Administrativo (MVP)
            2. 🔄 Direito Constitucional
            3. 🔄 Direito Tributário
            4. 🔄 Direito Penal
            5. 🔄 Direito Civil
            6. 🔄 Direito do Trabalho
            7. 🔄 Direito do Consumidor
            8. 🔄 Direito Ambiental

            ### 🤝 Como Contribuir

            - **GitHub:** [prof-ramos/JurDatasetBrasil](https://github.com/prof-ramos/JurDatasetBrasil)
            - **Issues:** Reporte problemas ou sugira melhorias
            - **Pull Requests:** Contribua com código ou exemplos

            ### 📄 Licença

            - **Dataset:** CC-BY-4.0 (Creative Commons Attribution)
            - **Código:** MIT License

            ### 🔗 Links

            - [Documentação](https://github.com/prof-ramos/JurDatasetBrasil/blob/main/README.md)
            - [Paper/PRD](https://github.com/prof-ramos/JurDatasetBrasil/blob/main/PRD.md)
            - [Roadmap](https://github.com/prof-ramos/JurDatasetBrasil/blob/main/ROADMAP.md)
            """)

# Launch
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
