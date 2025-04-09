# Supabase MCP Server

A Model Context Protocol (MCP) server implementation that allows Large Language Models (LLMs) to interact with Supabase databases using natural language. This server implements the MCP specification and provides a set of tools for performing common database operations.

**Note that this implementation is experimental and should be used with caution.**

## Features

- **Read Records**: Query and filter data from Supabase tables
- **Create Records**: Insert new records into tables
- **Update Records**: Modify existing records based on filters
- **Delete Records**: Remove records that match specific criteria

## Prerequisites

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
   source venv/bin/activate
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

## Running as an MCP Server

The Supabase MCP server can be integrated with AI assistants using the Model Context Protocol.

1. Include the below configuration in your MCP config (in Claude Desktop, Windsurf, etc.)

```json
{
  "mcpServers": {
    "supabase": {
      "command": "/path/to/python3/in/your/virtual/environment",
      "args": ["path/to/server.py"]
    }
  }
}
```

## Development

### Running Tests

To run the test suite:

```
python -m pytest
```

The tests use pytest's fixtures and mocking capabilities to test the functionality without requiring a real Supabase connection.

### Code Formatting

Format code using black:

```
black .
```

## License

[MIT License](LICENSE)
