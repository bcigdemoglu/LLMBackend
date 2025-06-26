from typing import Any

from ..database import execute_raw_sql


def create_record(table_name: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    CREATE: Insert new records into a table
    """
    try:
        columns = ", ".join(data.keys())
        placeholders = ", ".join([f":{key}" for key in data.keys()])

        query = (
            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING *"
        )

        result = execute_raw_sql(query, data)

        return {
            "success": True,
            "message": f"Successfully created record in {table_name}",
            "data": result[0] if result else None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create record in {table_name}",
        }


def read_records(
    table_name: str,
    conditions: dict[str, Any] | None = None,
    columns: list[str] | None = None,
    limit: int | None = None,
    order_by: str | None = None,
) -> dict[str, Any]:
    """
    READ: Query records from a table with flexible filtering
    """
    try:
        # Build SELECT clause
        select_columns = ", ".join(columns) if columns else "*"
        query = f"SELECT {select_columns} FROM {table_name}"

        params = {}

        # Build WHERE clause
        if conditions:
            where_clauses = []
            for key, value in conditions.items():
                where_clauses.append(f"{key} = :{key}")
                params[key] = value

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

        # Add ORDER BY
        if order_by:
            query += f" ORDER BY {order_by}"

        # Add LIMIT
        if limit:
            query += f" LIMIT {limit}"

        result = execute_raw_sql(query, params)

        return {
            "success": True,
            "message": f"Successfully queried {table_name}",
            "data": result,
            "count": len(result),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to query {table_name}",
        }


def update_record(
    table_name: str, data: dict[str, Any], conditions: dict[str, Any]
) -> dict[str, Any]:
    """
    UPDATE: Modify existing records in a table
    """
    try:
        # Build SET clause
        set_clauses = []
        params = {}

        for key, value in data.items():
            set_clauses.append(f"{key} = :set_{key}")
            params[f"set_{key}"] = value

        # Build WHERE clause
        where_clauses = []
        for key, value in conditions.items():
            where_clauses.append(f"{key} = :where_{key}")
            params[f"where_{key}"] = value

        query = f"""
            UPDATE {table_name}
            SET {", ".join(set_clauses)}
            WHERE {" AND ".join(where_clauses)}
            RETURNING *
        """

        result = execute_raw_sql(query, params)

        return {
            "success": True,
            "message": f"Successfully updated records in {table_name}",
            "data": result,
            "updated_count": len(result),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update records in {table_name}",
        }


def delete_record(table_name: str, conditions: dict[str, Any]) -> dict[str, Any]:
    """
    DELETE: Remove records from a table
    """
    try:
        # Build WHERE clause
        where_clauses = []
        params = {}

        for key, value in conditions.items():
            where_clauses.append(f"{key} = :{key}")
            params[key] = value

        if not where_clauses:
            return {
                "success": False,
                "error": "No conditions provided for deletion",
                "message": "DELETE operations require conditions to prevent accidental data loss",
            }

        query = f"""
            DELETE FROM {table_name}
            WHERE {" AND ".join(where_clauses)}
            RETURNING *
        """

        result = execute_raw_sql(query, params)

        return {
            "success": True,
            "message": f"Successfully deleted records from {table_name}",
            "data": result,
            "deleted_count": len(result),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to delete records from {table_name}",
        }
