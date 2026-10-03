import urllib.request

from src.config import DATA, CHROMA_DIR, REPORT_URLS, DEVICE
from src.extraction import dump_data
from src.chunks import dump_chunk, read_pages, splitter
from src.chroma import build_chroma, get_embeddings

RAW = DATA / "raw"
INTERIM = DATA / "interim"
CHUNKS = DATA / "processed" / "chunks.jsonl"


def download_reports(urls=REPORT_URLS, out_dir=RAW):
    """Telecharge les PDF absents de out_dir et verifie que ce sont bien des PDF."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for nom, url in urls.items():
        chemin = out_dir / nom
        if chemin.exists():
            print(f"  {nom} deja present")
            continue
        print(f"  téléchargement de {nom}…")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as rep:
            contenu = rep.read()
        if not contenu.startswith(b"%PDF"):
            raise ValueError(f"{nom} : le lien ne renvoie pas un PDF ({url}). Telecharger a la main dans {out_dir}.")
        chemin.write_bytes(contenu)
        print(f"  {nom} telecharge ({len(contenu) / 1e6:.1f} Mo)")


def main(device=DEVICE):
    for dossier in (RAW, INTERIM, CHUNKS.parent):
        dossier.mkdir(parents=True, exist_ok=True)

    print("1/4 Telechargement des PDF")
    download_reports()

    print("2/4 Extraction des PDF")
    dump_data(RAW, INTERIM)

    print("3/4 Decoupage en chunks")
    dump_chunk(INTERIM, CHUNKS, splitter)

    if CHROMA_DIR.exists():
        print(f"4/4 Index deja présent ({CHROMA_DIR}) : supprimer ce dossier pour le reconstruire.")
        return
    print("4/4 Indexation Chroma (~1 h 30 sur CPU, ~15 min sur GPU T4 Colab)")
    build_chroma(read_pages(CHUNKS), embedding_function=get_embeddings(device=device))


if __name__ == "__main__":
    main()
