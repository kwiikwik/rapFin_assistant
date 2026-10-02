from src.config import DATA, CHROMA_DIR
from src.extraction import dump_data
from src.chunks import dump_chunk, read_pages, splitter
from src.chroma import build_chroma, get_embeddings

RAW = DATA / "raw"
INTERIM = DATA / "interim"
CHUNKS = DATA / "processed" / "chunks.jsonl"
DEVICE="cpu"


def main(device=DEVICE):
    INTERIM.mkdir(parents=True, exist_ok=True)
    CHUNKS.parent.mkdir(parents=True, exist_ok=True)

    print("1/3 Extraction des PDF")
    dump_data(RAW, INTERIM)

    print("2/3 Decoupage en chunks")
    dump_chunk(INTERIM, CHUNKS, splitter)

    if CHROMA_DIR.exists():
        print(f"3/3 Index deja present ({CHROMA_DIR}) : supprimer ce dossier pour le reconstruire.")
        return
    print("3/3 Indexation Chroma (~1 h 30 sur CPU, ~15 min sur GPU (T4 Collab))")
    build_chroma(read_pages(CHUNKS), embedding_function=get_embeddings(device=device))


if __name__ == "__main__":
    main()
