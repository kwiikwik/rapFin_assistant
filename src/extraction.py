from pathlib import Path
import re
import pymupdf
import pymupdf4llm
from langchain_core.documents import Document
import json
from config import BANQUES


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


def load_reports(root_path):
    all_pages = []
    for pdf in sorted(root_path.glob('*.pdf')):
        pages = load_report(pdf)
        all_pages.extend(pages)
        print(f'{len(pages)} pages du document {pdf.name} ont ete lues.')
    return all_pages


def save_pages(liste_docs,path):
    """Sauvegarde dans fichiers JSON les documents """
    with path.open('w', encoding="utf-8") as f:
        for doc in liste_docs:
            d = {"page_content": doc.page_content,
                 "metadata": doc.metadata}
            f.write(json.dumps(d) + '\n')


def dump_data(in_path,out_path):
    for pdf in sorted(in_path.glob('*.pdf')):
        # Rajouter verif si deja dans out_path
        print(pdf)
        if pdf.stem not in [f.stem for f in sorted(out_path.glob('*.jsonl'))]:
            doc = load_report(pdf)
            name = pdf.with_suffix('.jsonl').name
            save_pages(doc, out_path / name )
