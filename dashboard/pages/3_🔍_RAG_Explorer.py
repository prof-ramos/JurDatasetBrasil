import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

@st.cache_resource
def init_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_resource
def init_model():
    return SentenceTransformer(EMBEDDING_MODEL_NAME)

supabase = init_supabase()
model = init_model()

st.title("🔍 RAG Explorer")

query = st.text_input("Digite sua busca jurídica:", placeholder="Ex: O que é ato administrativo vinculado?")

if query and supabase and model:
    with st.spinner("Gerando embedding e buscando..."):
        # Gerar embedding
        query_embedding = model.encode(query).tolist()

        # Buscar Chunks (RPC call seria ideal, mas vamos usar match_embeddings se configurado, ou simular)
        # Nota: Supabase-py não tem suporte direto fácil a match_documents sem configurar a function no DB.
        # Vamos assumir que a function match_chunks existe ou usar query direta se possível (pgvector-python).
        # Como criamos o index ivfflat, podemos tentar usar rpc se criarmos a function.

        # Por enquanto, vamos avisar que precisa da function RPC
        st.warning("Para busca vetorial funcionar, precisamos criar a função RPC 'match_chunks' no Supabase.")

        # Placeholder para resultados
        st.info(f"Embedding gerado com dimensão: {len(query_embedding)}")

        # TODO: Implementar chamada RPC real
        # response = supabase.rpc('match_chunks', {'query_embedding': query_embedding, 'match_threshold': 0.7, 'match_count': 5}).execute()

else:
    if not query:
        st.info("Digite algo para buscar.")
    if not supabase:
        st.error("Erro Supabase.")
