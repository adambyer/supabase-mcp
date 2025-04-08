"""
Supabase MCP Server

This server implements the Model Context Protocol (MCP) to allow LLMs to interact with a Supabase database.
It uses the Stdio transport layer and provides tools for reading, creating, updating, and deleting records.
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any

from dotenv import load_dotenv
from fastmcp import FastMCP
from supabase import create_client, Client

# Configure logging
try:
    # Try to set up file logging, but fall back to console-only if in a read-only environment
    handlers = [logging.StreamHandler()]
    try:
        handlers.append(logging.FileHandler("supabase_mcp.log"))
    except (OSError, IOError):
        # Skip file logging if we're in a read-only environment (like Claude Desktop)
        pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
except Exception as e:
    # Last resort fallback
    logging.basicConfig(level=logging.INFO)
    print(f"Logging setup error: {str(e)}")

logger = logging.getLogger("supabase-mcp")

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error(
        "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables."
    )
    sys.exit(1)

# Initialize Supabase client
try:
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    sys.exit(1)


# Initialize FastMCP
mcp = FastMCP(
    "Supabase MCP Server",
    description="An MCP server for interacting with Supabase databases",
    dependencies=["supabase", "python-dotenv"],
)


@mcp.tool()
def read_records(
    table_name: str,
    columns: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    order_by: Optional[str] = None,
    order_direction: str = "asc",
) -> Dict[str, Any]:
    """
    Reads records from a specified table in the Supabase database.

    Args:
        table_name: The name of the table to read from.
        columns: Optional list of column names to return. If not provided, all columns will be returned.
        filters: Optional dictionary of filters to apply, where keys are column names and values are the filter values.
        limit: Optional limit on the number of records to return. Defaults to 100.
        order_by: Optional column name to order results by.
        order_direction: Optional direction for ordering (asc or desc). Defaults to asc.

    Returns:
        A dictionary with the query results and metadata.
    """
    try:
        # Start building the query
        query = supabase_client.table(table_name)

        # Select columns if specified
        if columns:
            query = query.select(",".join(columns))
        else:
            query = query.select("*")

        # Apply filters if provided
        if filters:
            # Use match for exact equality filters
            query = query.match(filters)

        # Apply order if specified
        if order_by:
            if order_direction.lower() == "desc":
                query = query.order(order_by, desc=True)
            else:
                query = query.order(order_by)

        # Apply limit
        query = query.limit(limit)

        # Execute the query
        response = query.execute()

        # Return the results
        return {
            "success": True,
            "data": response.data,
            "count": len(response.data),
            "table": table_name,
        }
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error reading records from {table_name}: {error_message}")
        return {"success": False, "error": error_message, "table": table_name}


@mcp.tool()
def create_records(table_name: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Creates one or more records in a specified table in the Supabase database.

    Use this tool when you need to insert new data into a table. You can create multiple
    records at once by providing a list of dictionaries.

    Args:
        table_name: The name of the table to create records in.
        records: A list of dictionaries, where each dictionary represents a record with column names as keys and values to insert.

    Returns:
        A dictionary with the creation results and metadata.
    """
    if not records:
        return {
            "success": False,
            "error": "No records provided for insertion",
            "table": table_name,
        }

    try:
        # Insert the records
        response = supabase_client.table(table_name).insert(records).execute()

        # Return the results
        return {
            "success": True,
            "data": response.data,
            "count": len(response.data),
            "table": table_name,
        }
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error creating records in {table_name}: {error_message}")
        return {"success": False, "error": error_message, "table": table_name}


@mcp.tool()
def update_records(
    table_name: str, updates: Dict[str, Any], filters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Updates one or more records in a specified table in the Supabase database.

    Use this tool when you need to modify existing data. You must provide filters to
    identify which records to update, as updating all records is not allowed.

    Args:
        table_name: The name of the table to update records in.
        updates: A dictionary with column names as keys and new values to set.
        filters: A dictionary of filters to identify which records to update, where keys are column names and values are the filter values.

    Returns:
        A dictionary with the update results and metadata.
    """
    if not updates:
        return {"success": False, "error": "No updates provided", "table": table_name}

    if not filters:
        return {
            "success": False,
            "error": "No filters provided. Updating all records is not allowed for safety reasons.",
            "table": table_name,
        }

    try:
        # First, retrieve the records that match the filters
        read_response = read_records(table_name=table_name, filters=filters)

        if (
            not read_response.get("success", False)
            or len(read_response.get("data", [])) == 0
        ):
            return {
                "success": False,
                "error": "No records found matching the provided filters",
                "table": table_name,
            }

        # Extract IDs of matching records
        record_ids = [
            record["id"] for record in read_response.get("data", []) if "id" in record
        ]

        if not record_ids:
            return {
                "success": False,
                "error": "Could not find ID field in the records",
                "table": table_name,
            }

        # Update each record by ID
        updated_records = []
        for record_id in record_ids:
            # Update by ID which should work on all implementations
            update_query = (
                supabase_client.table(table_name)
                .update(updates)
                .match({"id": record_id})
            )
            update_result = update_query.execute()
            updated_records.extend(update_result.data)

        # Return the results
        return {
            "success": True,
            "data": updated_records,
            "count": len(updated_records),
            "table": table_name,
        }
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error updating records in {table_name}: {error_message}")
        return {"success": False, "error": error_message, "table": table_name}


@mcp.tool()
def delete_records(table_name: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deletes one or more records from a specified table in the Supabase database.

    Use this tool when you need to remove data from a table. You must provide filters to
    identify which records to delete, as deleting all records is not allowed.

    Args:
        table_name: The name of the table to delete records from.
        filters: A dictionary of filters to identify which records to delete, where keys are column names and values are the filter values.

    Returns:
        A dictionary with the deletion results and metadata.
    """
    if not filters:
        return {
            "success": False,
            "error": "No filters provided. Deleting all records is not allowed for safety reasons.",
            "table": table_name,
        }

    try:
        # First, retrieve the records that match the filters
        read_response = read_records(table_name=table_name, filters=filters)

        if (
            not read_response.get("success", False)
            or len(read_response.get("data", [])) == 0
        ):
            return {
                "success": False,
                "error": "No records found matching the provided filters",
                "table": table_name,
            }

        # Extract IDs of matching records
        record_ids = [
            record["id"] for record in read_response.get("data", []) if "id" in record
        ]

        if not record_ids:
            return {
                "success": False,
                "error": "Could not find ID field in the records",
                "table": table_name,
            }

        # Delete each record by ID
        deleted_records = []
        for record_id in record_ids:
            # Delete by ID which should work on all implementations
            delete_query = (
                supabase_client.table(table_name).delete().match({"id": record_id})
            )
            delete_result = delete_query.execute()
            deleted_records.extend(delete_result.data)

        # Return the results
        return {
            "success": True,
            "data": deleted_records,
            "count": len(deleted_records),
            "table": table_name,
        }
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error deleting records from {table_name}: {error_message}")
        return {"success": False, "error": error_message, "table": table_name}


if __name__ == "__main__":
    logger.info("Starting Supabase MCP Server")
    mcp.run()
