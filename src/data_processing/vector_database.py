import re

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
import pdfplumber

from src.utils.settings import Settings

# Declare settings and global variables
settings = Settings()


class PDFProcessor:
    
    @classmethod
    def _load_and_clean_pdf(cls, file_name: str) -> list:

        documents = []

        # Extract PDF
        with pdfplumber.open(file_name) as pdf:

            # Get file metadata
            file_metadata = pdf.metadata

            for page_n, page in enumerate(pdf.pages, start=1):


                # Correctly extract table text to ensure
                # agent comprehension
                tables = page.extract_tables()
                tables_text = ""

                if tables:
                    for table in tables:
                        for line in table:
                            
                            # Cleans and correctly formats table text
                            clean_line = [str(item).strip() if item is not None else "" for item in line]
                            tables_text += "| " + " | ".join(clean_line) + " |\n"

                        tables_text += "\n"

                text = page.extract_text(layout=False) or ""
                clean_text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])

                page_content = f"{clean_text}\n\n### Dados Estruturados da Página:\n{tables_text}"

                # Cleaning page text to remove excess spaces and unnecessary text
                page_content = re.sub('Empório da Música Manual de Políticas e Procedimentos', ' ', page_content)
                page_content = re.sub(r'[^\S\n]+', ' ', page_content)
                page_content = re.sub(r'\n{3,}', '\n\n', page_content)
                
                # Creating page document
                meta_page = (file_metadata or {}).copy()
                meta_page["pagina"] = page_n
                meta_page["fonte"] = str(file_name)
                
                documents.append(Document(page_content=page_content, metadata=meta_page))

            if documents:
                print(len(documents[2].page_content))
            
        return documents

    @classmethod
    def _chunk_pdf(cls, documents: list):
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 512,
            chunk_overlap = 50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = text_splitter.split_documents(documents)

        return chunks

    @classmethod
    def process(cls, file_name: str):
        
        documents = cls._load_and_clean_pdf(file_name)
        chunks = cls._chunk_pdf(documents)

        return chunks


class VectorDB:

    def __init__(self, embedding_model: str, PERSISTENCE_DIR: str) -> None:
        
        self.embedding_model = embedding_model
        self.PERSISTENCE_DIR = PERSISTENCE_DIR

    def create_vecdb(self, chunks: list) -> dict:

        embedding = GoogleGenerativeAIEmbeddings(
                model=self.embedding_model,
                google_api_key=settings.google_key
            )

        try:
            vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=embedding,
                persist_directory=self.PERSISTENCE_DIR,
                collection_name="politicas_loja"
            )

        except Exception as e:
            return {
                'status': 400,
                'error': str(e)
            }
        
        return {
            'status': 200,
            'result': vector_db
        }


def main():
    
    chunks = PDFProcessor.process(settings.PDF_PATH)
    vector_db_creator = VectorDB(settings.EMBEDDING_MODEL, settings.PERSISTENCE_DIR)
    result = vector_db_creator.create_vecdb(chunks)

    if result['status'] == 400:
        print(result['error'])

    print("Status:", result['status'])


# Quick test to see if vector_db was created correctly (Written by AI)
def test_quick_search():
    settings = Settings()
    
    print("🔍 Iniciando teste rápido de integração com ChromaDB...")
    print(f"📁 Diretório de Persistência: {settings.PERSISTENCE_DIR}")
    print(f"🤖 Modelo de Embedding: {settings.EMBEDDING_MODEL}")
    print("-" * 60)

    try:
        # 1. Configura o modelo de embedding idêntico ao do pipeline
        embedding = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=settings.google_key
        )

        # 2. Conecta ao banco carregando a coleção correta que você nomeou
        vector_db = Chroma(
            persist_directory=str(settings.PERSISTENCE_DIR),
            embedding_function=embedding,
            collection_name="politicas_loja"
        )

        # 3. Teste de Sanidade: Quantos registros temos salvos?
        collection_data = vector_db._collection.get()
        total_chunks = len(collection_data.get('ids', []))
        
        print(f"📊 Coleção 'politicas_loja' encontrada!")
        print(f"📊 Quantidade de chunks armazenados: {total_chunks}")
        
        if total_chunks == 0:
            print("❌ Erro: O banco existe, mas nenhum documento foi indexado. Execute o pipeline principal primeiro.")
            return

        # 4. Simulação de busca que o agente faria
        query_teste = "Qual o prazo para solicitar reembolso de um produto?"
        print(f"\n🧠 Executando busca semântica para: '{query_teste}'")
        
        # Testando com o top k = 3 que discutimos
        resultados = vector_db.similarity_search(query_teste, k=3)
        
        print(f"📥 Documentos recuperados (Top {len(resultados)}):")
        print("=" * 60)
        
        for idx, doc in enumerate(resultados, start=1):
            pagina = doc.metadata.get('pagina', 'N/A')
            fonte = doc.metadata.get('fonte', 'Desconhecida')
            print(f"📄 CHUNK {idx} | Origem: {fonte} | Página: {pagina}")
            print(f"Trecho: {doc.page_content[:250]}...") # Exibe os primeiros 250 caracteres do bloco
            print("-" * 60)
            
        print("🎉 Sucesso! Se os trechos acima trouxeram informações sobre prazos ou devoluções, seu Vector DB está validado e pronto para a Tool do agente.")

    except Exception as e:
        print(f"❌ Falha crítica ao validar o Vector DB: {str(e)}")
        print("Dica: Verifique se o caminho especificado em settings.PERSISTENCE_DIR realmente contém os arquivos '.bin' e sqlite do Chroma.")

if __name__ == "__main__":

    main()
    test_quick_search()
