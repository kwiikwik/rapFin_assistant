from pathlib import Path
from itertools import islice
from langchain_pymupdf4llm import PyMuPDF4LLMLoader

"""
Prend en entree le path d'un pdf ( dans format "banque_annee.pdf") et retourne une liste composee des pages du pdf en format 
Document dont les metadata sont adaptees au format voulu
"""
def load_report(path):
    cle, annee = path.stem.rsplit('_',1)
    banque, langue = BANQUES[cle][0],BANQUES[cle][1]
    loader = PyMuPDF4LLMLoader(path,mode = "page")
    liste_page = []
    for p in loader.lazy_load():
        p.metadata = {
            "source": path.name,
            "banque": banque,
            "annee": int(annee),
            "langue": langue, 
            "page": p.metadata['page']+1
        }
        liste_page.append(p)
    return liste_page


"""
Retourne liste composee de toutes les pages de tous les rapports du dossier root_path
"""
def load_reports(root_path):
    all_pages = []
    for pdf in sorted(root_path.glob('*.pdf')):
        pages = load_report(pdf)
        all_pages.extend(pages)
        print(f'{len(pages)} pages du document {pdf.name} ont ete lues.')
    return all_pages
