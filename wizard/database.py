import os
from collections.abc import Generator
from datetime import datetime

from dotenv import load_dotenv
from sqlmodel import Session, create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL, echo=False)


def get_session() -> Generator[Session]:
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
            rows = []
            for row in result.fetchall():
                row_dict = {}
                for col, val in zip(columns, row, strict=False):
                    # Convert datetime objects to ISO format strings
                    if isinstance(val, datetime):
                        row_dict[col] = val.isoformat()
                    else:
                        row_dict[col] = val
                rows.append(row_dict)
            return rows
        else:
            session.commit()
            return []
