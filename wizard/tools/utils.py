import re
from typing import Any


def parse_sql_error(error_message: str) -> dict[str, str]:
    """
    Parse SQL error messages to provide more meaningful feedback
    """
    error_patterns = {
        "table_not_exists": r'relation "([^"]+)" does not exist',
        "column_not_exists": r'column "([^"]+)" does not exist',
        "duplicate_table": r'relation "([^"]+)" already exists',
        "duplicate_column": r'column "([^"]+)" of relation "([^"]+)" already exists',
        "syntax_error": r'syntax error at or near "([^"]+)"',
        "permission_denied": r'permission denied for relation "([^"]+)"',
        "data_type_mismatch": r'invalid input syntax for type (\w+): "([^"]+)"',
    }

    for error_type, pattern in error_patterns.items():
        match = re.search(pattern, error_message, re.IGNORECASE)
        if match:
            return {
                "error_type": error_type,
                "details": match.groups(),
                "suggestion": get_error_suggestion(error_type, match.groups()),
            }

    return {
        "error_type": "unknown",
        "details": [],
        "suggestion": "Check the SQL syntax and table/column names",
    }


def get_error_suggestion(error_type: str, details: tuple) -> str:
    """
    Provide helpful suggestions based on error type
    """
    suggestions = {
        "table_not_exists": f"Table '{details[0]}' doesn't exist. Use describe_database to see available tables or create_table to create it.",
        "column_not_exists": f"Column '{details[0]}' doesn't exist. Use describe_table to see available columns.",
        "duplicate_table": f"Table '{details[0]}' already exists. Use a different name or check existing tables with describe_database.",
        "duplicate_column": f"Column '{details[0]}' already exists in table '{details[1]}'. Use a different column name.",
        "syntax_error": f"SQL syntax error near '{details[0]}'. Check the query structure.",
        "permission_denied": f"No permission to access table '{details[0]}'. Check database permissions.",
        "data_type_mismatch": f"Invalid value '{details[1]}' for type {details[0]}. Check data format.",
    }

    return suggestions.get(
        error_type, "Review the error and adjust your query accordingly."
    )


def sanitize_identifier(identifier: str) -> str:
    """
    Sanitize SQL identifiers to prevent injection attacks
    """
    # Remove dangerous characters and limit to alphanumeric + underscore
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "", identifier)

    # Ensure it starts with a letter
    if sanitized and not sanitized[0].isalpha():
        sanitized = "x" + sanitized

    return sanitized[:63]  # PostgreSQL identifier limit


def validate_table_name(table_name: str) -> bool:
    """
    Validate table name format
    """
    if not table_name:
        return False

    # Check for valid PostgreSQL identifier
    pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
    return bool(re.match(pattern, table_name)) and len(table_name) <= 63


def validate_column_definition(column_def: dict[str, str]) -> dict[str, Any]:
    """
    Validate column definition structure
    """
    required_fields = ["name", "type"]
    errors = []

    for field in required_fields:
        if field not in column_def:
            errors.append(f"Missing required field: {field}")

    if "name" in column_def and not validate_table_name(column_def["name"]):
        errors.append(f"Invalid column name: {column_def['name']}")

    return {"valid": len(errors) == 0, "errors": errors}


def build_where_clause(conditions: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """
    Build a safe WHERE clause from conditions
    """
    if not conditions:
        return "", {}

    where_parts = []
    params = {}

    for key, value in conditions.items():
        sanitized_key = sanitize_identifier(key)
        param_key = f"param_{sanitized_key}"

        if isinstance(value, list):
            # Handle IN clauses
            placeholders = []
            for i, item in enumerate(value):
                item_key = f"{param_key}_{i}"
                placeholders.append(f":{item_key}")
                params[item_key] = item
            where_parts.append(f"{sanitized_key} IN ({', '.join(placeholders)})")
        else:
            where_parts.append(f"{sanitized_key} = :{param_key}")
            params[param_key] = value

    where_clause = " AND ".join(where_parts)
    return where_clause, params


def format_query_result(
    result: list[dict[str, Any]], max_rows: int = 100
) -> dict[str, Any]:
    """
    Format query results for display
    """
    if not result:
        return {"rows": [], "count": 0, "columns": [], "truncated": False}

    truncated = len(result) > max_rows
    display_result = result[:max_rows] if truncated else result

    return {
        "rows": display_result,
        "count": len(result),
        "columns": list(result[0].keys()) if result else [],
        "truncated": truncated,
    }


def extract_table_references(query: str) -> list[str]:
    """
    Extract table names referenced in a SQL query
    """
    # Simple regex to find table names after FROM and JOIN
    patterns = [
        r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"\bINTO\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        r"\bUPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)",
    ]

    tables = set()
    for pattern in patterns:
        matches = re.findall(pattern, query, re.IGNORECASE)
        tables.update(matches)

    return list(tables)
