import re
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import K_CONTEXT


SYSTEM_PROMPT = """Tu es un assistant d'analyse financière. Tu réponds à des questions sur les rapports annuels 2025 de banques, à partir d'extraits numérotés.

Règles :
1. Utilise UNIQUEMENT les informations des extraits. N'utilise jamais tes connaissances propres.
2. Après chaque affirmation, cite le ou les extraits utilisés avec leur numéro entre crochets, par exemple [1] ou [2][4].
3. Si les extraits ne permettent pas de répondre, réponds exactement : « Je ne trouve pas cette information dans les extraits fournis. »
4. Donne les chiffres exactement comme dans les extraits, avec leur unité et leur date.
5. Si la question est ambiguë (par exemple, la banque n'est pas précisée) et que les extraits concernent plusieurs banques, donne la réponse pour chacune, en le précisant.
6. Réponds dans la langue de la question : question en anglais → réponse entièrement en anglais ; question en français → réponse entièrement en français. Le tout de façon concise.
7. Si les extraits portent sur plusieurs entités (groupe consolidé, filiale, maison mère), précise toujours l'entité concernée. Pour une question sur « la banque » sans précision, privilégie le chiffre du groupe consolidé s'il figure dans les extraits."""

USER_TEMPLATE = """Extraits :

{context}

Question : {question}

Answer in the same language as the question (English question → English answer, question en français → réponse en français)."""


def format_context(docs):
    """Chunks en texte formate pour llm"""
    blocs = []
    for i, doc in enumerate(docs, start=1):
        m = doc.metadata
        blocs.append(f"[{i}] ({m['banque']}, {m['source']}, page {m['page']})\n{doc.page_content}")
    return "\n\n".join(blocs)


def generate(question, docs, llm) -> str:
    sys_msg = SystemMessage(content=SYSTEM_PROMPT)
    context=format_context(docs)
    hum_msg = HumanMessage(content=USER_TEMPLATE.format(question=question, context=context))
    ai_msg = llm.invoke([sys_msg, hum_msg])
    return ai_msg.content

def extraire_citations(reponse, docs):
    sources = re.findall(r"[\[【](\d+)(?:†[^\]】]*)?[\]】]", reponse)
    details = []
    vus = set()
    for i in map(int,sources):
        if i in vus or not 1 <= i<= len(docs):
            continue
        vus.add(i)
        m = docs[i-1].metadata
        detail = {'n':i,
                  "banque":m['banque'],
                  "source":m['source'],
                  "annee":m['annee'],
                  "langue":m['langue'],
                  "page":m['page']
                 }
        details.append(detail)
    return details

def answer(question, retriever, llm, k=K_CONTEXT) -> dict:
    docs = retriever.invoke(question)[:k]
    reponse = generate(question, docs, llm)
    ans = {"question": question,
           "reponse":reponse,
           "sources": extraire_citations(reponse,docs)}
    return ans




