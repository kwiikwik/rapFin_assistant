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

CHROMA_DIR = DATA / 'index/chroma'
COLLECTION_NAME = 'report_banques_bgem3'


