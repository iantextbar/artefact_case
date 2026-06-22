"""
    Settings file to load relevant environment variables and set
    default parameters.
"""

import os
from pathlib import Path


from dotenv import load_dotenv

ROOT_PATH = Path(__file__).resolve().parent.parent.parent
_env_path = ROOT_PATH / ".env"
load_dotenv(dotenv_path=_env_path)

class Settings:

    def __init__(self) -> None:

        self.google_key = os.getenv("GOOGLE_API_KEY")

        # Global variables
        self.PDF_PATH = ROOT_PATH / "data" / "raw" / "politicas_da_loja.pdf"
        self.EMBEDDING_MODEL = "gemini-embedding-001"
        self.PERSISTENCE_DIR = ROOT_PATH / "data" / "chroma_db_storage"
        self.MODEL = "gemini-2.0-flash"

