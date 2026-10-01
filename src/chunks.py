from pathlib import Path
import json
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.extraction import save_pages
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, SEPARATORS

def read_pages(jsonl_path):
    """Renvois liste de documents lu d'un jsonl """
    with open(jsonl_path, 'r',encoding='utf-8') as f:
        pages = [Document(**json.loads(line)) for line in f]
    return pages

splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
        keep_separator="end"
        )

def chunk_pages(pages, splitter):
    chunk_list = splitter.split_documents(pages)
    iD = 0
    page_precedent = None
    for c in chunk_list:
        source = c.metadata['source'].rsplit('.',1)[0]
        page_number = c.metadata['page']
        if page_precedent == page_number:
            iD +=1
        else: 
            iD =0
            page_precedent = page_number
        c.metadata['chunk_id'] = f'{source}_p{page_number}_c{iD}'
    return chunk_list

def dump_chunk(in_path, out_path,splitter):
    chunks = []
    for jsonl in sorted(Path(in_path).glob('*.jsonl')):
        c = chunk_pages(read_pages(jsonl),splitter)
        chunks.extend(c)
        print(f'{jsonl.name} lu, {len(c)} chunks crees')
    # tailles = [len(c.page_content) for c in chunks]
    # obs = f'Au total, {len(chunks)} chunks crees, max, min et mediane des chunks est {max(tailles), min(tailles), sorted(tailles)[len(tailles)//2]}'
    # print(obs)
    # ob1 = sum(len(c.page_content)<50 for c in chunks)
    # ob2 = sum(len(c.page_content)<100 for c in chunks)
    # ob3 = sum(len(c.page_content)<200 for c in chunks)
    # print(f'''On observe:
    # -{ob1} chunks a moins de 50 caracteres soit {round(ob1/len(chunks)*100,3)}% des chunks
    # -{ob2} chunks a moins de 100 caracteres soit {round(ob2/len(chunks)*100,3)}% des chunks
    # -{ob3} chunks a moins de 200 caracteres soit {round(ob3/len(chunks)*100,3)}% des chunks''')
    # print('Un chunk au hasard :')
    # pp(chunks[250].metadata)
    save_pages(chunks, Path(out_path))
