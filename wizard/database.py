from sqlmodel import create_engine, Session, text
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL, echo=False)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def execute_raw_sql(query: str, params: dict = None) -> list:
    """Execute raw SQL and return results as list of dictionaries"""
    with Session(engine) as session:
        # SQLModel's exec doesn't support parameters directly, use execute instead
        if params:
            result = session.execute(text(query), params)
        else:
            result = session.execute(text(query))
        
        if result.returns_rows:
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
        else:
            session.commit()
            return []
