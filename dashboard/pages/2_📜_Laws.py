import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@st.cache_resource
def init_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.title("📜 Explorador de Leis")

if supabase:
    # Listar Leis
    laws_response = supabase.table("laws").select("id, law_number, title, year").execute()
    laws = laws_response.data

    if laws:
        law_options = {f"{l['law_number']} - {l['title']}": l['id'] for l in laws}
        selected_law_label = st.selectbox("Selecione uma Lei", options=list(law_options.keys()))
        selected_law_id = law_options[selected_law_label]

        if selected_law_id:
            # Detalhes da Lei
            st.subheader("Artigos")
            articles_response = supabase.table("articles").select("article_ref, full_text").eq("law_id", selected_law_id).order("article_ref").execute()
            articles = articles_response.data

            for art in articles:
                with st.expander(art['article_ref']):
                    st.write(art['full_text'])
    else:
        st.info("Nenhuma lei encontrada no banco de dados.")
else:
    st.error("Erro de conexão com Supabase.")
