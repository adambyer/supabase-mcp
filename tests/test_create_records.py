"""
Tests for the create_records function in the Supabase MCP server.
"""

import pytest
from unittest.mock import MagicMock, patch

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import create_records


class TestCreateRecords:
    """Tests for the create_records function."""
    
    def test_create_records_success(self, patched_server_module, mock_supabase_client):
        """
        Test successful record creation.
        
        Args:
            patched_server_module: The patched server module.
            mock_supabase_client: A mock of the Supabase client.
        """
        # Test data
        records = [{"name": "New Record", "value": 300}]
        
        # Call the function
        result = create_records(table_name="test_table", records=records)
        
        # Check the response structure
        assert result["success"] is True
        assert "data" in result
        assert "count" in result
        assert "table" in result
        assert result["table"] == "test_table"
        
        # Verify client interactions
        mock_supabase_client.table.assert_called_with("test_table")
        mock_supabase_client.table().insert.assert_called_once_with(records)
        mock_supabase_client.table().insert().execute.assert_called_once()
        
    def test_create_multiple_records(self, patched_server_module, mock_supabase_client):
        """
        Test creating multiple records at once.
        
        Args:
            patched_server_module: The patched server module.
            mock_supabase_client: A mock of the Supabase client.
        """
        # Test data with multiple records
        records = [
            {"name": "Record 1", "value": 100},
            {"name": "Record 2", "value": 200},
            {"name": "Record 3", "value": 300}
        ]
        
        # Call the function
        result = create_records(table_name="test_table", records=records)
        
        # Check the response
        assert result["success"] is True
        
        # Verify client interactions
        mock_supabase_client.table().insert.assert_called_once_with(records)
        
    def test_create_records_empty_input(self, patched_server_module, mock_supabase_client):
        """
        Test handling of empty records list.
        
        Args:
            patched_server_module: The patched server module.
            mock_supabase_client: A mock of the Supabase client.
        """
        # Call the function with empty records list
        result = create_records(table_name="test_table", records=[])
        
        # Check the error response
        assert result["success"] is False
        assert "error" in result
        assert "No records provided" in result["error"]
        
        # Verify client was not called
        mock_supabase_client.table.assert_not_called()
        
    def test_create_records_failure(self, patched_server_module, mock_supabase_client):
        """
        Test handling of errors during record creation.
        
        Args:
            patched_server_module: The patched server module.
            mock_supabase_client: A mock of the Supabase client.
        """
        # Configure the mock to raise an exception
        mock_supabase_client.table().insert().execute.side_effect = Exception("Test error")
        
        # Test data
        records = [{"name": "New Record", "value": 300}]
        
        # Call the function
        result = create_records(table_name="test_table", records=records)
        
        # Check the error response
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]
        assert result["table"] == "test_table"
