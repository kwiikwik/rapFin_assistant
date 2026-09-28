# Assistant de lecture, rapport de finances

## Idee du projet

A partir de rapports de financiers annuels de banques, l'assistant aide a repondre au questions de l'utilisateur en donnant la reponse et en justifiant avec la page du rapport financier.

Ce projet a pour but d'utiliser et de se familiariser avec les RAG et LLM.

Les rapports de banquest utilises sont disponibles sur les sites des banques, ici seront utilises celle de [BNP Paribas](https://invest.bnpparibas/recherche/rapports/documents/rapports-financiers-et-sociaux), [Credit Agricole](https://www.credit-agricole.com/finance/publications-financieres) et [UBS](https://www.ubs.com/global/en/investor-relations/financial-information/annual-reporting.html).

## Etapes du projets



1. Extraction du texte des pages du rapport (faire attention au mot separe en fin de ligne), nettoyage simple (strip et espace). Pour chaque page, retourner `('id_doc','page','texte')`.
2.a Tokenisation du texte (sub-word) on visera (~500 tokens) (set chroma).
2.b Set BM25.
A voir : utiliser LangChain directement ou ecrire les programmes a la main ?
3. Embedding (chercher un multilangue car UBS en anglais) + stockage dans Chroma.
4. Recherche BM25 + Chroma, fusion hybride.
5. Ecrire ~20 questions/reponses (utiliser Claude ou Gemini) et evaluer le hit@5. (Utiliser LangChain pour tout ca).

6. Ecrire prompt et utiliser LLM (MistralAPI ?)

7. Creation interface avec Streamlit.
