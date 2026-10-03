import re

import streamlit as st

from src.generation import answer
from src.pipeline import build_pipeline

st.set_page_config(page_title="Assistant rapports financiers 2025", layout="wide")

RAPPORTS = [
    ("BNP Paribas", "Document d'enregistrement universel 2025", "FR", 936,
     "https://invest.bnpparibas/recherche/rapports/documents/rapports-financiers-et-sociaux"),
    ("Crédit Agricole S.A.", "Comptes consolidés 2025", "FR", 272,
     "https://www.credit-agricole.com/finance/publications-financieres"),
    ("UBS", "Annual Report 2025", "EN", 380,
     "https://www.ubs.com/global/en/investor-relations/financial-information/annual-reporting.html"),
]

EXEMPLES = [
    "Did the goal of 2025 were accomplished ?",
    "Qui est le directeur général (Group CEO) d'UBS ?",
    "Quel dividende UBS propose-t-il pour l'exercice 2025 ?",
    "Quel est le ratio CET1 ?",
    "Quels sont les objectifs 2026 de BNP Paribas ?",
    "Quel est le chiffre d'affaires de la Société Générale ?",
]

CITATION = re.compile(r"[\[【](\d+)(?:†[^\]】]*)?[\]】]")


def nettoyer_citations(texte):
    """【1†L4-L6】 / 【1】 -> [1]"""
    return CITATION.sub(lambda m: f"[{m.group(1)}]", texte)


@st.cache_resource(show_spinner="Chargement des index et du modèle…")
def charger():
    return build_pipeline()


def choisir_exemple(texte):
    """Clic sur un exemple : remplit la question et lance la recherche."""
    st.session_state.question = texte
    st.session_state.lancer = True

def effacer():
    """Vide la question ; la réponse disparaît avec la réexécution."""
    st.session_state.question = ""

# ---------- barre latérale : contexte ----------
with st.sidebar:
    st.header("Rapports analysés")
    for banque, titre, langue, pages, lien in RAPPORTS:
        st.markdown(f"**[{banque}]({lien})** - {titre} ({langue}, {pages} p.)")

    st.header("Fonctionnement")
    st.markdown(
        "1. La question est comparée aux ~5 800 passages des rapports "
        "(recherche par sens **et** par mots-clés).\n"
        "2. Les 5 passages les plus pertinents sont donnés à un LLM.\n"
        "3. Le LLM répond **uniquement** à partir de ces passages et cite les pages. "
        "S'il ne trouve pas, il le dit."
    )

    st.caption("[github.com/kwiikwik/rapFin_assistant](https://github.com/kwiikwik/rapFin_assistant)")

# ---------- page principale ----------
st.title("Assistant de lecture des rapports financiers 2025")
st.write(
    "Posez une question en français ou en anglais sur les rapports annuels 2025 de "
    "**BNP Paribas**, **Crédit Agricole S.A.** et **UBS**. "
    "La réponse cite les pages du rapport utilisées."
)

retriever, llm = charger()

st.caption("Exemples :")
colonnes = st.columns(3)
for i, ex in enumerate(EXEMPLES):
    colonnes[i % 3].button(ex, key=f"ex{i}", on_click=choisir_exemple, args=(ex,),
                           use_container_width=True)

with st.form("formulaire"):
    question = st.text_input("Question", key="question")
    col1, col2 = st.columns([1, 8])
    envoyer = col1.form_submit_button("Demander")
    col2.form_submit_button("Effacer", on_click=effacer)

lancer = envoyer or st.session_state.pop("lancer", False)

if lancer and question.strip():
    with st.spinner("Recherche en cours…"):
        ans = answer(question, retriever, llm)

    st.markdown(nettoyer_citations(ans["reponse"]))

    if ans["sources"]:
        st.subheader("Sources")
        for s in ans["sources"]:
            st.markdown(f"- [{s['n']}] {s['banque']}, {s['source']}, page {s['page']}")
