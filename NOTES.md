# v0

## Extraction de texte et nettoyages 
Certains points a ameliorer, surtout au nettoyage
- Bannieres chapitres -> a retirer + associer le chap a metadata ( .get_toc marche met pour ca pas inclus)
- Balises html genre <sup>/ <mark> -> a nettoyer avec regex
- sommaire -> filtrer et associer ensuite ajouter chapitre/section dans metadata pour reponse + precise ? a lier avec bannieres
- pages vides a filtrer -> min de mot a associer 
- certains caractere non identifies (carre blanc) a supprimer
- tableaux -> meilleur nettoyage serait utiles


## Chunks 
- titre de section commencant par ### separee du texte -> rattacher par force debut de section au chunks d'apres
- phrases coupees entre pages -> ???
- certains chunks tres petits -> a fusionner
- tableaux sont coupes, on perd l'en tete (annees par ex) -> ajouter l'en tete a la main dans autres parties coupees
- tableaux on perd le contexte du tableau -> ajouter phrase precedent le tableau au chunks comme avec l'en tete ? ne pas couper le tableau vu que token_max = 8192 (mais pertinence d'un aussi grand vecteur ??) 
    ou associer metadata 'table_id' aux chunks, mais dans embedding vecto pas de metadata, donc apres reponse verifier si reponse a table_id demander chroma de donner tous les chunks avec cette table_id, llm se chargera du reste.
- notes de bas de tableau (bnp) -> les associer au chunks correspondants ?




