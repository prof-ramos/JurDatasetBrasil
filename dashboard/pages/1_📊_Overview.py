import streamlit as st
from supabase import create_client, Client
import os
import sys
from pathlib import Path
import plotly.express as px
import pandas as pd

# Adiciona o diretório raiz ao path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Carrega variáveis de ambiente (se necessário, mas o streamlit carrega do .env se estiver na raiz ou via secrets)
from dotenv import load_dotenv
load_dotenv()

# Configuração Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@st.cache_resource
def init_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Credenciais do Supabase não encontradas. Verifique o arquivo .env.")
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.title("📊 Visão Geral do Dataset")

if supabase:
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        try:
            laws_count = supabase.table("laws").select("*", count="exact", head=True).execute().count
            st.metric("Leis Cadastradas", laws_count)
        except Exception as e:
            st.metric("Leis Cadastradas", "Erro")
            st.error(f"Erro ao buscar leis: {e}")

    with col2:
        try:
            articles_count = supabase.table("articles").select("*", count="exact", head=True).execute().count
            st.metric("Artigos Processados", articles_count)
        except:
            st.metric("Artigos Processados", "-")

    with col3:
        try:
            chunks_count = supabase.table("chunks").select("*", count="exact", head=True).execute().count
            st.metric("Chunks Vetorizados", chunks_count)
        except:
            st.metric("Chunks Vetorizados", "-")

    with col4:
        try:
            examples_count = supabase.table("examples").select("*", count="exact", head=True).execute().count
            st.metric("Exemplos Gerados", examples_count)
        except:
            st.metric("Exemplos Gerados", "-")

    st.divider()

    # Gráficos (Placeholder por enquanto, pois não temos dados)
    st.subheader("Distribuição por Matéria")
    st.info("Aguardando ingestão de dados para gerar gráficos.")

else:
    st.warning("Conexão com Supabase não estabelecida.")
