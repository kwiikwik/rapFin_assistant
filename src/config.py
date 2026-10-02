from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'




BANQUES = {
    "bnpparibas" : ('BNP Paribas', 'fr'),
    "ca": ('Credit Agricole', 'fr'),
    "caex": ('Credit Agricole', 'fr'),
    "ubs": ('UBS','en')
}


### chunk.py parameters

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
SEPARATORS = ['\n\n', # defaut
              '\n',   # defaut
              '. ',
              '; ',
              ', ',
              ' ',    #defaut
              '']     #defaut

### indexing.py parameters

EMBED_MODEL = "BAAI/bge-m3"

CHROMA_DIR = DATA / 'index/chroma_v0'
COLLECTION_NAME = 'rapport_v0'



### retrieval / generation
K_RETRIEVER = 10 #  nbr de docs envoye par bm25 et chroma pour la fusion rrf derriere
K_CONTEXT = 5    #nbr de docs envoye au llm 
WEIGHTS_RRF = [0.3, 0.7]          # bm25 / chroma
LLM_MODEL = "openai/gpt-oss-120b"
LLM_RPS = 0.05
