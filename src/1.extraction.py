from pathlib import Path
import re
import pymupdf
import pymupdf4llm
from langchain_core.documents import Document

def load_report(path):
    """
    Prend en entree le path d'un pdf ( dans format "banque_annee.pdf") et retourne une liste composee des pages du pdf format Document dont les metadata sont adaptees au format voulu
    """
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

def extract(page):
    """Genere (class,text) d'une boite pour une page """
    for ligne in page["page_boxes"]:
        debut,fin = ligne['pos']
        yield ligne['class'], page['text'][debut:fin]


def clean_text(texte,langue):
    """Nettoie texte en retirant balise html apres conversion md, et les soulignes/gras/italique de md et bug genre fi gures"""
    texte = re.sub(r"<br\s*/?>", " ", texte)
    texte = re.sub(r"</?u>|\*{1,3}|(?<!\w)_+|_+(?!\w)", "", texte)
    if langue == "en":
        texte = re.sub(r"(fi|fl) (?=[a-z])", r"\1", texte)
    return re.sub(r"\n{3,}", "\n\n", texte).strip()



def load_report(path):
    """ Renvoie une liste des pages du pdf dans path sous type Document (type loader LangChain) """
    liste_pages = []
    cle_banque, annee = path.stem.rsplit('_',1)
    banque, langue = BANQUES[cle_banque]
    def garder(classe):
        if classe in ('picture', 'page-footer'):
            return False
        return True
    pdf = pymupdf4llm.to_markdown(path, page_chunks=True,show_progress=True)
    for page in pdf:
        texte_page = "\n".join(texte_ligne for classe,texte_ligne in extract(page) if garder(classe))
        doc = Document(
            page_content = clean_text(texte_page,langue),
            metadata = {
                "source": path.name ,
                "banque": banque,
                "annee": int(annee),
                "langue": langue,
                "page": page['metadata']['page_number']
            })
        liste_pages.append(doc)
    return liste_pages
        
