from src.pipeline import build_pipeline
from src.generation import answer
import streamlit as st







st.set_page_config(page_title="Assistant de lecture des rapports financiers 2025", layout="wide")
st.title("Assistant de lecture des rapports financiers 2025")

@st.cache_resource
def charger():
    return build_pipeline()

retriever,llm = charger()

with st.form("question"):
    question = st.text_input("Question")
    envoyer = st.form_submit_button("Demander")

if envoyer and len(question.strip())>0:
    with st.spinner("Recherche en cours"):
        ans = answer(question, retriever, llm)

    st.markdown(ans['reponse'])
    if ans['sources']:
        st.subheader('Sources:')
        for source in ans['sources']:
            st.markdown(f"[{source['n']}] {source['banque']}, {source['source']}, page {source['page']}")
