from typing import Any

from ..database import execute_raw_sql


def describe_database() -> dict[str, Any]:
    """
    DESCRIBE DATABASE: List all tables in the current database
    """
    try:
        query = """
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """

        result = execute_raw_sql(query)

        return {
            "success": True,
            "message": "Successfully retrieved database schema",
            "tables": result,
            "table_count": len(result),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to describe database",
        }


def describe_table(table_name: str) -> dict[str, Any]:
    """
    DESCRIBE TABLE: Show table structure, constraints, and row count
    """
    try:
        # Get column information
        columns_query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_name = :table_name
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """

        # Get constraints
        constraints_query = """
            SELECT
                tc.constraint_name,
                tc.constraint_type,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = :table_name
            AND tc.table_schema = 'public'
        """

        # Get row count
        count_query = f"SELECT COUNT(*) as row_count FROM {table_name}"

        columns = execute_raw_sql(columns_query, {"table_name": table_name})
        constraints = execute_raw_sql(constraints_query, {"table_name": table_name})
        row_count = execute_raw_sql(count_query)

        return {
            "success": True,
            "message": f"Successfully described table {table_name}",
            "table_name": table_name,
            "columns": columns,
            "constraints": constraints,
            "row_count": row_count[0]["row_count"] if row_count else 0,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to describe table {table_name}",
        }


def create_table(
    table_name: str, columns: list[dict[str, str]], constraints: list[str] | None = None
) -> dict[str, Any]:
    """
    CREATE TABLE: Create a new table with specified columns and constraints

    columns format: [{"name": "id", "type": "SERIAL PRIMARY KEY"}, {"name": "name", "type": "VARCHAR(255)"}]
    constraints format: ["UNIQUE(email)", "CHECK(age > 0)"]
    """
    try:
        # Build column definitions
        column_defs = []
        for col in columns:
            column_defs.append(f"{col['name']} {col['type']}")

        # Add constraints if provided
        if constraints:
            column_defs.extend(constraints)

        query = f"""
            CREATE TABLE {table_name} (
                {", ".join(column_defs)}
            )
        """

        execute_raw_sql(query)

        return {
            "success": True,
            "message": f"Successfully created table {table_name}",
            "table_name": table_name,
            "columns": columns,
            "constraints": constraints or [],
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create table {table_name}",
        }


def alter_table(
    table_name: str, operation: str, details: dict[str, Any]
) -> dict[str, Any]:
    """
    ALTER TABLE: Modify table structure

    operation types:
    - "add_column": details = {"column_name": "email", "column_type": "VARCHAR(255)"}
    - "drop_column": details = {"column_name": "old_field"}
    - "modify_column": details = {"column_name": "age", "new_type": "INTEGER"}
    - "add_constraint": details = {"constraint": "UNIQUE(email)"}
    - "drop_constraint": details = {"constraint_name": "unique_email"}
    """
    try:
        if operation == "add_column":
            query = f"""
                ALTER TABLE {table_name}
                ADD COLUMN {details["column_name"]} {details["column_type"]}
            """
        elif operation == "drop_column":
            query = f"""
                ALTER TABLE {table_name}
                DROP COLUMN {details["column_name"]}
            """
        elif operation == "modify_column":
            query = f"""
                ALTER TABLE {table_name}
                ALTER COLUMN {details["column_name"]} TYPE {details["new_type"]}
            """
        elif operation == "add_constraint":
            query = f"""
                ALTER TABLE {table_name}
                ADD {details["constraint"]}
            """
        elif operation == "drop_constraint":
            query = f"""
                ALTER TABLE {table_name}
                DROP CONSTRAINT {details["constraint_name"]}
            """
        else:
            return {
                "success": False,
                "error": f"Unsupported operation: {operation}",
                "message": f"ALTER TABLE operation '{operation}' not supported",
            }

        execute_raw_sql(query)

        return {
            "success": True,
            "message": f"Successfully altered table {table_name}",
            "operation": operation,
            "details": details,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to alter table {table_name}",
        }


def create_index(
    table_name: str, index_name: str, columns: list[str], unique: bool = False
) -> dict[str, Any]:
    """
    CREATE INDEX: Add an index to improve query performance
    """
    try:
        unique_keyword = "UNIQUE " if unique else ""
        columns_str = ", ".join(columns)

        query = f"""
            CREATE {unique_keyword}INDEX {index_name}
            ON {table_name} ({columns_str})
        """

        execute_raw_sql(query)

        return {
            "success": True,
            "message": f"Successfully created index {index_name}",
            "index_name": index_name,
            "table_name": table_name,
            "columns": columns,
            "unique": unique,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create index {index_name}",
        }


def drop_index(index_name: str) -> dict[str, Any]:
    """
    DROP INDEX: Remove an index
    """
    try:
        query = f"DROP INDEX {index_name}"
        execute_raw_sql(query)

        return {
            "success": True,
            "message": f"Successfully dropped index {index_name}",
            "index_name": index_name,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to drop index {index_name}",
        }


def manage_transaction(
    operations: list[str], operation_type: str = "commit"
) -> dict[str, Any]:
    """
    MANAGE TRANSACTIONS: Handle multi-step operations atomically

    operation_type: "commit" or "rollback"
    operations: List of SQL statements to execute in transaction
    """
    try:
        if operation_type == "commit":
            # Execute all operations in a transaction
            all_queries = ["BEGIN"] + operations + ["COMMIT"]
            for query in all_queries:
                execute_raw_sql(query)

            return {
                "success": True,
                "message": "Transaction committed successfully",
                "operations_count": len(operations),
            }
        elif operation_type == "rollback":
            execute_raw_sql("ROLLBACK")
            return {"success": True, "message": "Transaction rolled back successfully"}
        else:
            return {
                "success": False,
                "error": f"Invalid operation_type: {operation_type}",
                "message": "operation_type must be 'commit' or 'rollback'",
            }
    except Exception as e:
        # Attempt rollback on error
        try:
            execute_raw_sql("ROLLBACK")
        except Exception:
            pass

        return {
            "success": False,
            "error": str(e),
            "message": "Transaction failed and was rolled back",
        }
