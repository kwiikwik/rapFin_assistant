from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import numpy as np
from src.config import EMBED_MODEL, COLLECTION_NAME, CHROMA_DIR

def get_embeddings():
    return HuggingFaceEmbeddings(model_name = EMBED_MODEL,
                                 encode_kwargs = {"normalize_embeddings": True})


def load_chroma(collection_name=COLLECTION_NAME, out_dir=CHROMA_DIR):
    collect = Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings() ,
        persist_directory = str(out_dir),
        collection_configuration = {"hnsw": {"space" : "cosine"}}
    )
    return collect


def build_chroma(chunks, taille_lot=500):
    collect = load_chroma()

    print(f'{len(chunks)} chunks a indexer dans {CHROMA_DIR}')
    for i in range(0,len(chunks), taille_lot):
        chunks_petit = chunks[i:i+taille_lot]
        collect.add_documents(documents=chunks_petit, ids=[c.metadata['chunk_id'] for c in chunks_petit])
        print(f'{i+len(chunks_petit)}/{len(chunks)} chunks ont ete ajoutes dans index Chroma.')
    return collect

