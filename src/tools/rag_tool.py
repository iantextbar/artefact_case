from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.utils.settings import Settings

# Global variables
settings = Settings()

@tool
def query_store_policy_and_procedures(query: str) -> str:
    """
    Busca informações sobre a loja Empório da Música, como suas políticas e procedimentos.
    Informações incluem formas de pagamento, políticas de devolução e trocas, políticas de entrega e fretes,
    descontos e promoções, garantias e informações básicas da loja como seu endereço física, de email, seu CNPJ e telefone de contato.

    Use essa ferramenta SEMPRE que o cliente fizer perguntas relacionadas às políticas da loja ou aos temas citados, por exemplo:
    'Em quantas vezes posso parcelar meu pedido?', 'Tem frete grátis?', 'Meu produto está danificado, quais as condições para trocá-lo?'.

    Argumentos:
        query: A pergunta feita pelo cliente relacionada às políticas e procedimentos da loja.
    """

    embedding = GoogleGenerativeAIEmbeddings(model=settings.EMBEDDING_MODEL)
    vector_db = Chroma(
        persist_directory=str(settings.PERSISTENCE_DIR), 
        embedding_function=embedding,
        collection_name="politicas_loja"

    )

    docs = vector_db.similarity_search(query, k=3)
    
    return "\n\n".join([d.page_content for d in docs])
