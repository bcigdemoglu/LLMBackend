from sqlmodel import SQLModel, Field, create_engine
from typing import Optional, Dict, Any
from datetime import datetime
import os

# This module demonstrates the "As Above, So Below" principle
# These SQLModel classes serve as both API models and database table definitions

class WizardLog(SQLModel, table=True):
    """
    Log of all wizard operations for debugging and auditing
    """
    __tablename__ = "wizard_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    operation: str = Field(max_length=50)
    table_name: Optional[str] = Field(default=None, max_length=100)
    query: Optional[str] = Field(default=None)
    success: bool = Field(default=False)
    error_message: Optional[str] = Field(default=None)
    execution_time_ms: Optional[float] = Field(default=None)

class DynamicTableMetadata(SQLModel, table=True):
    """
    Metadata about dynamically created tables
    """
    __tablename__ = "dynamic_tables_metadata"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    table_name: str = Field(max_length=100, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by_question: str = Field(max_length=500)
    schema_definition: str  # JSON string of the schema
    last_modified: datetime = Field(default_factory=datetime.utcnow)

def create_all_tables():
    """
    Create the wizard's internal management tables
    """
    from .database import engine
    SQLModel.metadata.create_all(engine)

def get_postgres_type_mapping() -> Dict[str, str]:
    """
    Map common data types to PostgreSQL types
    """
    return {
        "string": "VARCHAR(255)",
        "text": "TEXT",
        "integer": "INTEGER",
        "int": "INTEGER",
        "float": "REAL",
        "decimal": "DECIMAL",
        "boolean": "BOOLEAN",
        "bool": "BOOLEAN",
        "date": "DATE",
        "datetime": "TIMESTAMP",
        "timestamp": "TIMESTAMP",
        "json": "JSONB",
        "uuid": "UUID"
    }

def infer_postgres_type(value: Any) -> str:
    """
    Infer PostgreSQL type from a Python value
    """
    if isinstance(value, bool):
        return "BOOLEAN"
    elif isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "REAL"
    elif isinstance(value, datetime):
        return "TIMESTAMP"
    elif isinstance(value, dict):
        return "JSONB"
    elif isinstance(value, list):
        return "JSONB"
    else:
        # Default to VARCHAR for strings and unknown types
        return "VARCHAR(255)"

def create_table_schema_from_data(table_name: str, sample_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a table schema from sample data
    This embodies the wizard's ability to create structure from intention
    """
    columns = []
    
    # Always include an ID column
    columns.append({
        "name": "id",
        "type": "SERIAL PRIMARY KEY"
    })
    
    # Infer columns from sample data
    for key, value in sample_data.items():
        if key != "id":  # Skip if user provided ID
            postgres_type = infer_postgres_type(value)
            columns.append({
                "name": key,
                "type": postgres_type
            })
    
    return {
        "table_name": table_name,
        "columns": columns,
        "created_from_data": True
    }
