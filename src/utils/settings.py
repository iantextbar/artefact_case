"""
    Settings file to load relevant environment variables and set
    default parameters.
"""

import os
from pathlib import Path


from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

class Settings:

    def __init__(self) -> None:

        self.google_key = os.getenv("GOOGLE_API_KEY")
