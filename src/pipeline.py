from dotenv import load_dotenv
from src.config import ROOT,DATA,K_RETRIEVER,COLLECTION_NAME,CHROMA_DIR,WEIGHTS_RRF,LLM_RPS,LLM_MODEL
from src.chunks import read_pages
from src.bm25 import BM25Retriever,tokenize
from src.chroma import load_chroma
from src.retrieval import build_hybride_retriever
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq


def build_pipeline():
    ## verifie que les chunks et embeddings existent bien.
    chunks_path = DATA / "processed/chunks.jsonl"
    if not chunks_path.exists() or not CHROMA_DIR.exists():
        raise FileNotFoundError("Index absent : lancer d'abord l'ingestion (ingest.py).")
    ## load fichier .env contenant GROQ_API_KEY
    load_dotenv(ROOT / ".env")
    ## lecture des chunks
    chunks = read_pages(chunks_path)
    ## bm25 retriever
    bm25_retriever = BM25Retriever.from_documents(chunks,tokenize,k=K_RETRIEVER)
    ## chroma retriever
    chroma_retriever = load_chroma(collection_name=COLLECTION_NAME,
                                 chroma_dir= CHROMA_DIR).as_retriever(search_kwargs={"k":K_RETRIEVER})
    ## hybride retriever
    hybride_retriever = build_hybride_retriever([bm25_retriever,chroma_retriever],weights=WEIGHTS_RRF)
    ## llm
    limiter = InMemoryRateLimiter(requests_per_second=LLM_RPS)
    llm = ChatGroq(model=LLM_MODEL, temperature=0,
               reasoning_effort="low",
               rate_limiter=limiter, max_retries=2)
    return hybride_retriever,llm
