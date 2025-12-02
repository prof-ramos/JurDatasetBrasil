import streamlit as st
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar scripts
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from scripts.config import PROJECT_ROOT

st.set_page_config(
    page_title="JurDatasetBrasil Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚖️ JurDatasetBrasil Dashboard")

st.markdown("""
### Bem-vindo ao Painel de Controle

Este dashboard permite visualizar o progresso, explorar as leis e testar o pipeline RAG do **JurDatasetBrasil**.

#### Navegação
- **📊 Overview**: Estatísticas gerais do dataset.
- **📜 Leis**: Explorador de leis e artigos importados.
- **🔍 RAG Explorer**: Teste de busca semântica e geração de respostas.

---
*Versão 2.0 - Dez/2025*
""")

st.sidebar.success("Selecione uma página acima.")
