import re
import unicodedata
from typing import Callable

import numpy as np
from nltk.corpus import stopwords
from pydantic import ConfigDict
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun

import nltk
nltk.download("stopwords", quiet=True)



def sans_accents(texte):
    """Retire accents d'un texte"""
    texte = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in texte if not unicodedata.combining(c))

MOTS_VIDES = {sans_accents(m) for m in stopwords.words("french") + stopwords.words("english")}


def tokenize(texte):
    """Apres nettoyage d'un texte, renvoie une liste de token """ 
    texte = re.sub(r"(?<=\d)[ \u00a0\u202f](?=\d{3}\b)", "", texte)    # retire espace dans nombres genre 12 225 millions
    texte = sans_accents(texte.lower())                                # minuscules, sans accents
    texte = re.sub(r"(?<=\d),(?=\d)", ".", texte)                      # remplace , dans nombre decimales en . (conv fr/eng)
    mots = re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", texte)                # cree liste des mots, chiffres, décimales
    return [m for m in mots if len(m) > 1 and m not in MOTS_VIDES]     # sans mots vides ni lettres seules

def build_bm25_index(chunks, tokenizer):
    """Renvoie un objet BM25Okapi a partir de liste de chunk (chunks) et le tokenizer voulu """
    corpus = [ tokenizer(c.page_content) for c in chunks]
    return BM25Okapi(corpus)

def bm25_search(question:str, chunks, tokenizer, index_bm25:BM25Okapi, k=5):
    """Renvoie liste des k chunks avec le plus grand scores apres une recherche bm25 a la question"""
    scores = index_bm25.get_scores(tokenizer(question))
    top_scores_index = np.argsort(-scores)[:k]
    return [chunks[i] for i in top_scores_index if scores[i]>0]


class BM25Retriever(BaseRetriever):
    """Retriever BM25 maison, compatible langchain (invoke, EnsembleRetriever…) car langchain-community deprecie."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    chunks: list[Document]
    index: BM25Okapi
    tokenizer: Callable[[str], list[str]]
    k: int = 5

    @classmethod
    def from_documents(cls, chunks, tokenizer, k=5):
        """Construit l'index BM25 à partir des chunks."""
        bm25_index = build_bm25_index(chunks, tokenizer)
        return cls(chunks=chunks,
                   index=bm25_index,
                   tokenizer=tokenizer,k=k
                  )

    def _get_relevant_documents(self, query: str, *,
                                run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
        return bm25_search(question=query,
                           chunks= self.chunks,
                           tokenizer= self.tokenizer,
                           index_bm25= self.index,
                           k=self.k
                          )

