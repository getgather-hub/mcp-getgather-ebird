# eBird MCP

A CLI tool for eBird MCP integration.

## Installation

### Prerequisites

If you don't have `uv` installed, first install it:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### Clone the repository

```bash
git clone https://github.com/getgather-hub/mcp-getgather-ebird.git
cd mcp-getgather-ebird
```

## Usage

### CLI Commands

```bash
# Get books from Goodreads
uv run ebird-mcp get-birds --username your-username --password your-password

# Use a custom host (default: 127.0.0.1:8000)
uv run ebird-mcp get-birds --username your-username --password your-password --host myserver.com
```

### Using with Claude Desktop

To use ebird-mcp as an MCP server in Claude Desktop:

1. First clone the repository:
   ```bash
   git clone https://github.com/getgather-hub/mcp-getgather-ebird.git
   cd mcp-getgather-ebird
   ```

2. Configure Claude Desktop by editing the config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`

3. Add the following configuration:
   ```json
   {
     "mcpServers": {
       "ebird-mcp": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/mcp-getgather-ebird",
           "run",
           "ebird-mcp"
         ],
         "env": {
           "EBIRD_USERNAME": "your-username",
           "EBIRD_PASSWORD": "your-password",
           "GETGATHER_URL": "127.0.0.1:8000"
         }
       }
     }
   }
   ```

   **Notes**: 
    * Replace `/path/to/mcp-getgather-ebird` with the actual path where you cloned the repository.
    * If the MCP server fails to startup at first, you may have to replace the `uv` command with the correct version of `uv` that you are running. For example, run `which uv` in your terminal and replace the standard `uv` command in the MCP config with the outputted path. It might look something like this: `/Users/username/.local/bin/uv`

4. Restart Claude Desktop

### Available MCP Tools

Once configured, the following tools will be available in Claude:

- **get_ebird_birds**: Get a list of birds with date and location where you first saw them.

### Environment Variables

The MCP server requires these environment variables:

- `EBIRD_USERNAME`: Your eBird account username
- `EBIRD_PASSWORD`: Your eBird password
- `GETGATHER_URL`: (Optional) Host URL for the service (default: 127.0.0.1:8000)


## License

This project is licensed under the MIT License.
