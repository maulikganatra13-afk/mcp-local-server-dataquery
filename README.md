# SQLQueryServer - MCP Server Documentation

A Model Context Protocol (MCP) server that provides SQL database query capabilities through FastMCP. This server allows AI assistants like Claude to interact with a SQLite database for querying and data manipulation.

## Overview

This MCP server exposes three main tools:
- **list_tables**: List all tables in the database
- **describe_table**: Get schema information for a specific table
- **run_query**: Execute any SQL query (SELECT, INSERT, UPDATE, DELETE, etc.)

## Prerequisites

- **Python**: Version 3.11 or higher
- **uv**: Python package installer (recommended) or pip

## Installation

### 1. Install uv (if not already installed)

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Dependencies

Navigate to the project directory and install dependencies:

```bash
cd "c:\Users\Maulik Ganatra\Desktop\github_projects\test-local_mcp-server-dataquery"
uv pip install -e .
```

Or using pip:
```bash
pip install -e .
```

This will install:
- `fastmcp` (>=0.3.0)
- `aiosqlite` (>=0.20.0)

## Running the Server Locally

To test the server locally before connecting it to Claude Desktop:

```bash
python main.py
```

Or with uv:
```bash
uv run main.py
```

The server will:
1. Create a `sql_demo.db` SQLite database in the project directory
2. Initialize two tables: `cars` and `users`
3. Start listening for MCP requests
4. Log activities to `logs/sql_query_server.log`

## Connecting to Claude Desktop

### Step 1: Locate Claude Desktop Configuration File

The configuration file location depends on your operating system:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Edit Configuration File

Open `claude_desktop_config.json` in a text editor. If the file doesn't exist, create it.

Add the following configuration to the `mcpServers` section:

**Using uv (Recommended):**
```json
{
  "mcpServers": {
    "sql-query-server": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\Users\\Maulik Ganatra\\Desktop\\github_projects\\test-local_mcp-server-dataquery",
        "run",
        "main.py"
      ]
    }
  }
}
```

**Using Python directly:**
```json
{
  "mcpServers": {
    "sql-query-server": {
      "command": "python",
      "args": [
        "c:\\Users\\Maulik Ganatra\\Desktop\\github_projects\\test-local_mcp-server-dataquery\\main.py"
      ]
    }
  }
}
```

**Important Notes:**
- Replace the path with your actual project directory path
- On Windows, use double backslashes (`\\`) in the path
- On macOS/Linux, use forward slashes (`/`) in the path

### Step 3: Restart Claude Desktop

After saving the configuration file:
1. Completely quit Claude Desktop (not just close the window)
2. Restart Claude Desktop
3. The MCP server will automatically start when Claude Desktop launches

### Step 4: Verify Connection

In Claude Desktop, you should be able to use the SQL query tools. Try asking:
- "Can you list the tables in the database?"
- "What's the schema of the cars table?"
- "Run a query to select all rows from the users table"

## Available Tools

### 1. list_tables
Lists all tables in the SQLite database.

**Example usage in Claude:**
> "Show me all the tables in the database"

**Returns:**
```json
{
  "status": "success",
  "tables": ["cars", "users"]
}
```

### 2. describe_table
Returns the schema (column names, types, nullable, defaults) for a specific table.

**Parameters:**
- `table` (string): Name of the table to describe

**Example usage in Claude:**
> "What columns does the cars table have?"

**Returns:**
```json
{
  "status": "success",
  "table": "cars",
  "columns": [
    {"name": "id", "type": "INTEGER", "nullable": false, "default": null},
    {"name": "make", "type": "TEXT", "nullable": false, "default": null},
    {"name": "model", "type": "TEXT", "nullable": false, "default": null},
    {"name": "price", "type": "REAL", "nullable": false, "default": null}
  ]
}
```

### 3. run_query
Executes any SQL query without restrictions (SELECT, INSERT, UPDATE, DELETE, etc.).

**Parameters:**
- `query` (string): SQL query to execute

**Example usage in Claude:**
> "Insert a new car: Toyota Camry with price 25000"
> "Select all users from Japan"
> "Update the price of Honda Civic to 19000"

**Returns (for SELECT queries):**
```json
{
  "status": "success",
  "row_count": 2,
  "rows": [
    {"id": 1, "make": "Toyota", "model": "Corolla", "price": 15000},
    {"id": 2, "make": "Honda", "model": "Civic", "price": 18000}
  ]
}
```

**Returns (for INSERT/UPDATE/DELETE queries):**
```json
{
  "status": "success",
  "rows_affected": 1,
  "message": "Query executed successfully. 1 row(s) affected."
}
```

## Database Schema

The server automatically creates two tables:

### cars table
```sql
CREATE TABLE cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    price REAL NOT NULL
)
```

### users table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    country TEXT NOT NULL
)
```

## Logs

All server activities are logged to:
```
logs/sql_query_server.log
```

Check this file for debugging connection issues or query errors.

## Troubleshooting

### Claude Desktop doesn't show the tools
1. Verify the configuration file path is correct
2. Check that the JSON syntax is valid (no trailing commas, proper quotes)
3. Ensure the project path in the config is absolute and correct
4. Restart Claude Desktop completely (quit and relaunch)

### Server fails to start
1. Check `logs/sql_query_server.log` for error messages
2. Verify Python 3.11+ is installed: `python --version`
3. Ensure dependencies are installed: `uv pip list` or `pip list`
4. Check that the project directory is accessible

### Database errors
1. Check that `sql_demo.db` has write permissions
2. Review the log file for specific error messages
3. Try deleting `sql_demo.db` and restarting to reinitialize

### Path issues on Windows
- Always use double backslashes (`\\`) in JSON configuration
- Or use forward slashes (`/`) which also work on Windows
- Ensure no special characters cause path parsing issues

## Security Notes

⚠️ **Warning**: This server allows unrestricted SQL query execution including INSERT, UPDATE, and DELETE operations. It's designed for local development and testing.

For production use, consider:
- Adding query validation and restrictions
- Implementing authentication
- Using read-only database connections
- Sanitizing user inputs

## Example Claude Interactions

**Getting started:**
> "Can you help me explore the database? First show me what tables exist."

**Querying data:**
> "Show me all cars that cost less than $20,000"

**Inserting data:**
> "Add a new user: Name 'Sarah', Country 'Canada'"

**Analyzing data:**
> "What's the average price of all cars in the database?"

**Complex queries:**
> "Show me the count of users by country, ordered by count descending"

## Additional Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Desktop Documentation](https://claude.ai/desktop)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## License

This project is for educational and development purposes.