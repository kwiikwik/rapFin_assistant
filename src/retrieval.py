from langchain_classic.retrievers import EnsembleRetriever


def build_hybride_retriever(retrievers, weights=None,c=60,id_key='chunk_id'):
    """Renvoie fusion de retrievers par RRF """
    if weights is None:
        weights = [1/len(retrievers)]*len(retrievers)
    return EnsembleRetriever(retrievers=retrievers,
                                      weights=weights,
                                      c=c,
                                      id_key=id_key)
