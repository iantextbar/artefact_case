from pathlib import Path
import sys
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from src.data_processing.base import Base

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # go up from scripts/ to src/
DB_PATH = BASE_DIR / "data" / "sql_db" / "music_store.db"
CONNECTION_STRING = f"sqlite:///{DB_PATH}"

class Db:

    def __init__(self):

        self.connection_string = CONNECTION_STRING

        self.engine = create_engine(
            self.connection_string,
            pool_pre_ping=True,
            pool_size=300,
            max_overflow=50,
            pool_recycle=3600,
            pool_timeout=30,
        )

        # Create a thread-safe session factory
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations.

        This context manager handles the session lifecycle, including:
        - Creating a new session
        - Handling commits and rollbacks
        - Ensuring the session is properly closed

        Yields:
            SQLAlchemy Session: A database session for executing queries

        Example:
            with db.get_session() as session:
                result = session.query(MyModel).filter_by(id=1).first()
                # Session is automatically committed if no exceptions occur
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_table(self, tablemodel):
        """Create table in the database."""
        try:
            Base.metadata.create_all(self.engine, tables=[tablemodel.__table__])
            print('MySQL table created successfully')
        except SQLAlchemyError as e:
            print(f"Error creating table: {e}")
            sys.exit(1)

    def drop_all_tables(self):
        try:
            Base.metadata.drop_all(self.engine)
        except SQLAlchemyError as e:
            sys.exit(1)
