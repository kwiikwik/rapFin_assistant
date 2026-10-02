# v0

## Extraction de texte et nettoyages
Certains points a ameliorer, surtout au nettoyage
- Bannieres chapitres -> a retirer + associer le chap a metadata (.get_toc marche mais pas inclus)
- Balises html genre <sup> / <mark> -> a nettoyer avec regex
- sommaire -> filtrer, puis ajouter chapitre/section dans metadata pour reponse + precise ? a lier avec bannieres
- pages vides a filtrer -> min de mots
- certains caracteres non identifies (carre blanc) a supprimer
- tableaux -> meilleur nettoyage serait utile
- rapport CA : mots colles (espacement trop petit) -> BM25 aveugle sur ces passages. Changer d'outil d'extraction (pdfplumber) pour regler l'espacement ?

## Chunks
- titre de section (###) separe du texte -> rattacher le titre au chunk d'apres
- phrases coupees entre pages -> decouper le doc entier en gardant la page de debut
- certains chunks tres petits (titres seuls, ex. "BILAN ACTIF") -> fusionner avec le chunk suivant
- tableaux coupes, on perd l'en-tete (annees par ex) -> repeter l'en-tete dans chaque partie
- tableaux, on perd le contexte -> ajouter la phrase d'intro au chunk ? ne pas couper le tableau (max 8192 tokens, mais pertinence d'un aussi grand vecteur ?)
    ou metadata 'table_id' : apres la recherche, recuperer tous les chunks du meme table_id, le llm se charge du reste
- notes de bas de tableau (bnp) -> les associer aux chunks du tableau

## Embeddings / Chroma
- question reformulee (jargon) -> scores tres serres ("solvabilite" vs "CET1")
- leger avantage a la meme langue (question FR -> chunk FR un peu mieux note que EN)
- scores serres entre resultats -> reranking ?
- questions sur une banque precise -> resultats melanges -> filtre metadata 'banque' (menu dans l'interface ou mots-cles)
- base sur Google Drive : construire sur disque local Colab, puis zip base cree

## BM25
- favorise les chunks qui repetent les mots -> trouve des chunks SUR le sujet, pas ceux qui repondent (certaines page decrivent/introduisent une pbmatique mais n'y repondent pas donc fausse importance d'un token)
- faux positifs sur mots banals ("niveau" -> Niveau 1/2/3 CA)
- ne traduit pas : question FR != chunks EN (UBS), sauf sigles communs
- pas de racinisation en v0 -> tester (attention FR/EN)
- pas de filtre metadata integre -> a ajouter dans BM25Retriever


## Eval hit@5

```
bm25           hit@5=50.0%  MRR=0.41  ratés=['q03', 'q04', 'q07', 'q08', 'q10', 'q11', 'q12', 'q17', 'q18', 'q20', 'q21', 'q23']
chroma         hit@5=83.3%  MRR=0.64  ratés=['q04', 'q11', 'q12', 'q21']
hyb 0.5/0.5    hit@5=79.2%  MRR=0.56  ratés=['q04', 'q07', 'q11', 'q12', 'q21']
hyb 0.3/0.7    hit@5=83.3%  MRR=0.65  ratés=['q04', 'q11', 'q12', 'q21']
hyb 0.2/0.8    hit@5=83.3%  MRR=0.65  ratés=['q04', 'q11', 'q12', 'q21']

Ratés par tous : [('q04', 'tableau'), ('q11', 'reformulee'), ('q12', 'tableau'), ('q21', 'multilingue')]

```
- chroma > hybride 0.5/0.5 → bruit BM25
- 0.3/0.7 = chroma, pas de gain BM25
- rates communs q04 q11 q12 q21 → chiffres dans tableaux




















