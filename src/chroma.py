from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from src.config import EMBED_MODEL, COLLECTION_NAME, CHROMA_DIR


def get_embeddings(model_name=EMBED_MODEL, device="cpu"):
    """Charge le modèle d'embedding (à n'appeler qu'au moment où on en a besoin)."""
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True},
    )


def load_chroma(collection_name=COLLECTION_NAME, chroma_dir=CHROMA_DIR, embedding_function=None):
    """Ouvre la collection Chroma (la crée si elle n'existe pas)."""
    if embedding_function is None:
        embedding_function = get_embeddings()
    collect = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_function,
        persist_directory=str(chroma_dir),
        collection_configuration={"hnsw": {"space": "cosine"}},
    )
    return collect


def build_chroma(chunks, collection_name=COLLECTION_NAME, chroma_dir=CHROMA_DIR,
                 embedding_function=None, taille_lot=500):
    """Indexe les chunks dans Chroma, par lots."""
    collect = load_chroma(collection_name, chroma_dir, embedding_function)

    print(f'{len(chunks)} chunks a indexer dans {chroma_dir} (collection {collection_name})')
    for i in range(0, len(chunks), taille_lot):
        chunks_petit = chunks[i:i+taille_lot]
        collect.add_documents(documents=chunks_petit,
                              ids=[c.metadata['chunk_id'] for c in chunks_petit])
        print(f'{i+len(chunks_petit)}/{len(chunks)} chunks ont ete ajoutes dans index Chroma.')
    return collect
