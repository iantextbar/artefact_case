from pathlib import Path
import re

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
import pdfplumber

from src.utils.settings import Settings

# Declare settings and global variables
ROOT_PATH = Path(__file__).resolve().parent.parent.parent
PDF_PATH = ROOT_PATH / "data" / "raw" / "politicas_da_loja.pdf"
EMBEDDING_MODEL = "models/text-embedding-004"
PERSISTENCE_DIR = ROOT_PATH / "data" / "vector_db" / "chroma_db_storage"
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
                meta_page["fonte"] = file_name
                
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

    def __init__(self, embedding_model: str, persistence_dir: str) -> None:
        
        self.embedding_model = embedding_model
        self.persistence_dir = persistence_dir

    def create_vecdb(self, chunks: list) -> dict:

        embedding = GoogleGenerativeAIEmbeddings(
                model=self.embedding_model,
                google_api_key=settings.google_key
            )

        try:
            vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=embedding,
                persist_directory=self.persistence_dir
            )

        except Exception as e:
            return {
                'status': 400,
                'error': str(e)
            }
        
        return {
            'status': 200,
        }


def main():
    
    chunks = PDFProcessor.process(PDF_PATH)
    vector_db_creator = VectorDB(EMBEDDING_MODEL, PERSISTENCE_DIR)
    result = vector_db_creator.create_vecdb(chunks)

    print("Status:", result['status'])

if __name__ == "__main__":

    main()
