"""
Supabase Client Wrapper

This module provides helper functions for interacting with the Supabase client.
"""

import logging
from typing import Dict, List, Optional, Any, Union

from supabase import Client

logger = logging.getLogger("supabase-mcp")


def get_table_schema(client: Client, table_name: str) -> Dict[str, Any]:
    """
    Gets the schema of a specified table.

    Args:
        client: The Supabase client.
        table_name: The name of the table to get the schema for.

    Returns:
        A dictionary with the table schema information.
    """
    try:
        # Use RPC to call the PostgreSQL information_schema
        response = client.rpc("get_table_schema", {"table_name": table_name}).execute()

        return {"success": True, "schema": response.data, "table": table_name}
    except Exception as e:
        logger.error(f"Error getting schema for table {table_name}: {str(e)}")
        return {"success": False, "error": str(e), "table": table_name}


def validate_table_exists(client: Client, table_name: str) -> bool:
    """
    Validates that a specified table exists in the database.

    Args:
        client: The Supabase client.
        table_name: The name of the table to validate.

    Returns:
        True if the table exists, False otherwise.
    """
    try:
        # Query the information_schema to check if the table exists
        response = client.rpc(
            "check_table_exists", {"table_name": table_name}
        ).execute()

        return response.data
    except Exception as e:
        logger.error(f"Error validating table {table_name}: {str(e)}")
        return False


def get_table_list(client: Client) -> Dict[str, Any]:
    """
    Gets a list of all tables in the database.

    Args:
        client: The Supabase client.

    Returns:
        A dictionary with the list of tables.
    """
    try:
        # Query the information_schema to get all tables
        response = client.rpc("get_table_list").execute()

        return {"success": True, "tables": response.data}
    except Exception as e:
        logger.error(f"Error getting table list: {str(e)}")
        return {"success": False, "error": str(e)}


def execute_raw_query(
    client: Client, query: str, params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Executes a raw SQL query.

    Args:
        client: The Supabase client.
        query: The SQL query string.
        params: Optional parameters for the query.

    Returns:
        A dictionary with the query results.
    """
    try:
        # Execute the query using RPC
        # Note: This should be used carefully as it allows arbitrary SQL execution
        response = client.rpc(
            "execute_sql", {"query_text": query, "params": params or {}}
        ).execute()

        return {"success": True, "data": response.data}
    except Exception as e:
        logger.error(f"Error executing raw query: {str(e)}")
        return {"success": False, "error": str(e)}
