import json
import re

from src.bm25 import sans_accents
from src.config import K_CONTEXT
from src.generation import answer
from src.retrieval import build_hybride_retriever



## Chargement des questions

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









#### Evaluation hit@5
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

    # 3) rates par tout le monde
    communs = set.intersection(*rates_par_nom.values())
    types = {q["id"]: q["type"] for q in questions}
    print("\nRates par tous :", [(i, types[i]) for i in sorted(communs)] or "aucun")


#### Evaluation llm



def normaliser(text):
    text = sans_accents(text).lower()
    text = re.sub(r'\s','',text)
    text = re.sub(r'(?<=\d)[.,](?=\d)', '',text)
    return text

def is_correct(reponse, cles):
    """ Verifie si une cle reponse est dans la reponse llm, 'a|b' accepte a OU b"""
    rep = normaliser(reponse)
    return all(any(normaliser(alt) in rep for alt in c.split("|")) for c in cles)


def is_cited(sources, q):
    """True si au moins une source citee dans page attendue."""
    bonnes = cibles(q)
    return any((s["source"], s["page"]) in bonnes for s in sources)


REFUS = ("je ne trouve pas", "cannot find", "could not find", "can't find")


def is_refus(reponse):
    """True si le llm dit ne pas trouver"""
    rep = reponse.lower()
    return any(r in rep for r in REFUS)


def evaluer_generation(retriever, llm, questions, k=K_CONTEXT):
    """Pose chaque question au pipeline complet et note la réponse."""
    resultats = []
    for i, q in enumerate(questions, start=1):
        r = answer(q["question"], retriever, llm, k)
        res = {
            "id": q["id"],
            "type": q["type"],
            "question": q["question"],
            "reponse": r["reponse"],
            "sources": [(s["source"], s["page"]) for s in r["sources"]],
            "correct": is_correct(r["reponse"], q["cles"]),
            "cite": is_cited(r["sources"], q),
            "refus": is_refus(r["reponse"]),
        }
        resultats.append(res)
        etat = "Correct" if res["correct"] else ("Refus" if res["refus"] else "Faux")
        print(f"[{i:2}/{len(questions)}] {q['id']} {etat:7} cite={res['cite']}")
    return resultats


def resume_generation(resultats):
    """Pourcentages globaux + liste des questions fausses."""
    n = len(resultats)
    exact = sum(r["correct"] for r in resultats) / n
    cite = sum(r["cite"] for r in resultats) / n
    refus = sum(r["refus"] for r in resultats) / n
    fausses = [r["id"] for r in resultats if not r["correct"] and not r["refus"]]
    print(f"exactitude={exact:.1%}  citation={cite:.1%}  refus={refus:.1%}")
    print(f"réponses fausses (sans refus) : {fausses or 'aucune'}")
    return {"exactitude": exact, "citation": cite, "refus": refus, "fausses": fausses}


def save_resultats(resultats, path):
    """Sauvegarde une ligne json par question, pour relire les réponses plus tard."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in resultats:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")










