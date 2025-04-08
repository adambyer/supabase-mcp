# Supabase MCP Server

A Model Context Protocol (MCP) server implementation that allows Large Language Models (LLMs) to interact with Supabase databases using natural language. This server implements the MCP specification and provides a set of tools for performing common database operations.

## Features

- **Read Records**: Query and filter data from Supabase tables
- **Create Records**: Insert new records into tables
- **Update Records**: Modify existing records based on filters
- **Delete Records**: Remove records that match specific criteria

## Prerequisites

- Python 3.8+
- Supabase project with a valid URL and service role key

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd supabase-mcp
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

   For development and testing, install development dependencies:
   ```
   pip install -r requirements-dev.txt
   ```

4. Create a `.env` file with your Supabase credentials:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file to add your actual Supabase URL and service role key.

## Usage

Run the MCP server:

```
python server.py
```

The server uses standard input/output (Stdio) for communication with LLMs, as recommended by the MCP protocol specification. This allows it to be used with LLM tools that support the MCP standard, such as various AI assistants and coding tools.

## Available Tools

### Read Records
Reads records from a specified table in the Supabase database.

**Parameters**:
- `table_name`: The name of the table to read from
- `columns`: (Optional) List of column names to return
- `filters`: (Optional) Dictionary of filters to apply
- `limit`: (Optional) Limit on the number of records to return (default: 100)
- `order_by`: (Optional) Column name to order results by
- `order_direction`: (Optional) Direction for ordering (asc or desc, default: asc)

### Create Records
Creates one or more records in a specified table.

**Parameters**:
- `table_name`: The name of the table to create records in
- `records`: A list of dictionaries, where each dictionary represents a record

### Update Records
Updates one or more records in a specified table.

**Parameters**:
- `table_name`: The name of the table to update records in
- `updates`: A dictionary with column names as keys and new values to set
- `filters`: A dictionary of filters to identify which records to update

### Delete Records
Deletes one or more records from a specified table.

**Parameters**:
- `table_name`: The name of the table to delete records from
- `filters`: A dictionary of filters to identify which records to delete

## Example Interactions

### Reading Data
```python
# Example of reading user records filtered by role
{
  "table_name": "users",
  "columns": ["id", "name", "email"],
  "filters": {"role": "admin"},
  "limit": 10,
  "order_by": "created_at",
  "order_direction": "desc"
}
```

### Creating Records
```python
# Example of creating a new product
{
  "table_name": "products",
  "records": [
    {
      "name": "New Product",
      "price": 29.99,
      "category": "electronics",
      "in_stock": true
    }
  ]
}
```

### Updating Records
```python
# Example of updating product price
{
  "table_name": "products",
  "updates": {
    "price": 24.99,
    "on_sale": true
  },
  "filters": {
    "id": 123
  }
}
```

### Deleting Records
```python
# Example of deleting a comment
{
  "table_name": "comments",
  "filters": {
    "id": 456
  }
}
```

## Security Considerations

This server uses the Supabase service role key, which has full access to your database. Be careful about how you deploy and use this server, and ensure that proper authentication and authorization checks are in place.

## Troubleshooting

- **Connection Issues**: Ensure your Supabase URL and service role key are correct in the `.env` file.
- **Permission Errors**: Make sure your service role key has the necessary permissions for the operations you're trying to perform.
- **Missing Tables**: Verify that the tables you're accessing exist in your Supabase project.

## Development

### Running Tests

To run the test suite:

```
pytest
```

For tests with coverage report:

```
pytest --cov=.
```

### Code Formatting

Format code using black:

```
black .
```

## License

[MIT License](LICENSE)
