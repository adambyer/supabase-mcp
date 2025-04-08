"""
Configuration for pytest fixtures.

This module provides fixtures for testing the Supabase MCP server.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import after setting up path
from fastmcp import FastMCP


@pytest.fixture
def mock_execute_response():
    """
    Create a mock response for execute() method.
    
    Returns:
        MagicMock: A mock response with test data.
    """
    mock_response = MagicMock()
    mock_response.data = [
        {"id": 1, "name": "Test Record 1", "value": 100},
        {"id": 2, "name": "Test Record 2", "value": 200},
    ]
    return mock_response


@pytest.fixture
def mock_supabase_client(mock_execute_response):
    """
    Create a mock Supabase client for testing.
    
    Args:
        mock_execute_response: The mock response to return from execute().
        
    Returns:
        MagicMock: A mocked Supabase client with predefined responses.
    """
    mock_client = MagicMock()
    
    # Mock table method
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    
    # Mock select chain
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select
    
    mock_limit = MagicMock()
    mock_select.limit.return_value = mock_limit
    
    mock_order = MagicMock()
    mock_select.order.return_value = mock_order
    mock_limit.order.return_value = mock_order
    mock_order.order.return_value = mock_order
    
    mock_match = MagicMock()
    mock_select.match.return_value = mock_match
    mock_limit.match.return_value = mock_match
    mock_order.match.return_value = mock_match
    
    # Make all chains return the execute method that returns our mock response
    mock_select.execute.return_value = mock_execute_response
    mock_limit.execute.return_value = mock_execute_response
    mock_order.execute.return_value = mock_execute_response
    mock_match.execute.return_value = mock_execute_response
    
    # Mock insert chain
    mock_insert = MagicMock()
    mock_table.insert.return_value = mock_insert
    mock_insert.execute.return_value = mock_execute_response
    
    # Mock update chain
    mock_update = MagicMock()
    mock_table.update.return_value = mock_update
    
    mock_update_match = MagicMock()
    mock_update.match.return_value = mock_update_match
    mock_update_match.execute.return_value = mock_execute_response
    
    # Mock delete chain
    mock_delete = MagicMock()
    mock_table.delete.return_value = mock_delete
    
    mock_delete_match = MagicMock()
    mock_delete.match.return_value = mock_delete_match
    mock_delete_match.execute.return_value = mock_execute_response
    
    return mock_client


@pytest.fixture
def mock_environment():
    """
    Set up mock environment variables for testing.
    
    Returns:
        dict: A dictionary containing the mock environment variables.
    """
    env_vars = {
        "SUPABASE_URL": "https://test-project.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "test-service-key"
    }
    
    # Apply environment variables
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def patched_server_module(mock_supabase_client):
    """
    Patch the server module for testing.
    
    Args:
        mock_supabase_client: The mock Supabase client.
        
    Returns:
        module: The patched server module.
    """
    # Import the server module here to avoid circular imports
    import server
    
    # Apply the patch
    with patch.object(server, 'supabase_client', mock_supabase_client):
        yield server
