"""
Tests for the update_records function in the Supabase MCP server.
"""

import pytest
from unittest.mock import MagicMock, patch

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import update_records


class TestUpdateRecords:
    """Tests for the update_records function."""
    
    def test_update_records_success(self, patched_server_module, mock_supabase_client, mock_execute_response):
        """
        Test successful record update.
        
        Args:
            patched_server_module: The patched server module.
            mock_supabase_client: A mock of the Supabase client.
            mock_execute_response: Mock response for execute method.
        """
        # Use our patched read_records
        with patch('server.read_records') as mock_read_records:
            # Configure mock read_records to return test data
            mock_read_records.return_value = {
                "success": True,
                "data": [{"id": 1, "name": "Test Record", "value": 100}],
                "count": 1,
                "table": "test_table"
            }
            
            # Test data
            updates = {"name": "Updated Record", "value": 150}
            filters = {"id": 1}
            
            # Call the function
            result = update_records(
                table_name="test_table", 
                updates=updates, 
                filters=filters
            )
            
            # Check the response structure
            assert result["success"] is True
            assert "data" in result
            assert "count" in result
            assert "table" in result
            assert result["table"] == "test_table"
            
            # Verify client interactions
            mock_supabase_client.table.assert_called_with("test_table")
            mock_supabase_client.table().update.assert_called_once_with(updates)
            mock_supabase_client.table().update().match.assert_called_once_with({"id": 1})
    
    def test_update_records_no_updates(self, patched_server_module, mock_supabase_client):
        """
        Test handling of empty updates.
        
        Args:
            patched_server_module: The patched server module.
            mock_supabase_client: A mock of the Supabase client.
        """
        # Call the function with empty updates
        result = update_records(
            table_name="test_table", 
            updates={}, 
            filters={"id": 1}
        )
        
        # Check the error response
        assert result["success"] is False
        assert "error" in result
        assert "No updates provided" in result["error"]
        
        # Verify client was not called
        mock_supabase_client.table.assert_not_called()
    
    def test_update_records_no_filters(self, patched_server_module, mock_supabase_client):
        """
        Test handling of missing filters.
        
        Args:
            patched_server_module: The patched server module.
            mock_supabase_client: A mock of the Supabase client.
        """
        # Call the function with empty filters
        result = update_records(
            table_name="test_table", 
            updates={"name": "Updated Record"}, 
            filters={}
        )
        
        # Check the error response
        assert result["success"] is False
        assert "error" in result
        assert "No filters provided" in result["error"]
        
        # Verify client was not called
        mock_supabase_client.table.assert_not_called()
    
    def test_update_records_no_matching_records(self, patched_server_module, mock_supabase_client):
        """
        Test handling of no matching records found.
        
        Args:
            patched_server_module: The patched server module.
            mock_supabase_client: A mock of the Supabase client.
        """
        with patch('server.read_records') as mock_read_records:
            # Configure mock read_records to return empty data
            mock_read_records.return_value = {
                "success": True,
                "data": [],
                "count": 0,
                "table": "test_table"
            }
            
            # Test data
            updates = {"name": "Updated Record"}
            filters = {"id": 999}  # Non-existent ID
            
            # Call the function
            result = update_records(
                table_name="test_table", 
                updates=updates, 
                filters=filters
            )
            
            # Check the error response
            assert result["success"] is False
            assert "error" in result
            assert "No records found" in result["error"]
    
    def test_update_records_failure(self, patched_server_module, mock_supabase_client):
        """
        Test handling of errors during record update.
        
        Args:
            patched_server_module: The patched server module.
            mock_supabase_client: A mock of the Supabase client.
        """
        with patch('server.read_records') as mock_read_records:
            # Configure mock read_records to return test data
            mock_read_records.return_value = {
                "success": True,
                "data": [{"id": 1, "name": "Test Record", "value": 100}],
                "count": 1,
                "table": "test_table"
            }
            
            # Configure the mock to raise an exception
            mock_supabase_client.table().update().match().execute.side_effect = Exception("Test error")
            
            # Test data
            updates = {"name": "Updated Record"}
            filters = {"id": 1}
            
            # Call the function
            result = update_records(
                table_name="test_table", 
                updates=updates, 
                filters=filters
            )
            
            # Check the error response
            assert result["success"] is False
            assert "error" in result
            assert "Test error" in result["error"]
            assert result["table"] == "test_table"
