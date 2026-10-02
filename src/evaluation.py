import json
from src.retrieval import build_hybride_retriever


def load_eval(path):
    with path.open('r',encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


def cibles(q):
    """Ensemble des (source, page) qui comptent comme bonne réponse."""
    return {(a["source"], p) for a in q["attendus"] for p in a["pages"]}

def rang_premier_hit(retriever, q, k=5):
    """Rang (1..k) du premier doc sur une bonne page, None si raté."""
    docs = retriever.invoke(q["question"])[:k]
    bonnes = cibles(q)
    for rang, d in enumerate(docs, start=1):
        if (d.metadata["source"], d.metadata["page"]) in bonnes:
            return rang
    return None

def evaluer(retriever, questions, k=5):
    details = []
    for q in questions:
        rang = rang_premier_hit(retriever, q, k)
        details.append({"id": q["id"], "type": q["type"], "rang": rang})
    hit = sum(d["rang"] is not None for d in details) / len(questions)
    mrr = sum(1 / d["rang"] for d in details if d["rang"]) / len(questions)
    return hit, mrr, details

def afficher(nom, hit, mrr, rates, k):
    print(f"{nom:14} hit@{k}={hit:.1%}  MRR={mrr:.2f}  ratés={rates}")

def comparer_poids(liste_poids, bm25_retriever, chroma_retriever, questions, k=5):
    rates_par_nom = {}

    # 1) bm25 et chroma : une seule fois
    for nom, r in {"bm25": bm25_retriever, "chroma": chroma_retriever}.items():
        hit, mrr, details = evaluer(r, questions, k=k)
        rates_par_nom[nom] = {d["id"] for d in details if d["rang"] is None}
        afficher(nom, hit, mrr, sorted(rates_par_nom[nom]), k)

    # 2) un hybride reconstruit pour chaque poids
    for w in liste_poids:
        h = build_hybride_retriever([bm25_retriever, chroma_retriever],
                                    weights=[w, 1 - w])
        hit, mrr, details = evaluer(h, questions, k=k)
        nom = f"hyb {w:.1f}/{1-w:.1f}"
        rates_par_nom[nom] = {d["id"] for d in details if d["rang"] is None}
        afficher(nom, hit, mrr, sorted(rates_par_nom[nom]), k)

    # 3) ratés par tout le monde
    communs = set.intersection(*rates_par_nom.values())
    types = {q["id"]: q["type"] for q in questions}
    print("\nRates par tous :", [(i, types[i]) for i in sorted(communs)] or "aucun")
