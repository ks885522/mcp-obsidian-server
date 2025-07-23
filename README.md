# MCP server for Obsidian

MCP server to interact with Obsidian via the Local REST API community plugin, built with FastMCP framework.

<a href="https://glama.ai/mcp/servers/3wko1bhuek"><img width="380" height="200" src="https://glama.ai/mcp/servers/3wko1bhuek/badge" alt="server for Obsidian MCP server" /></a>

## Components

### Tools

The server implements multiple tools to interact with Obsidian:

- list_files_in_vault: Lists all files and directories in the root directory of your Obsidian vault
- list_files_in_dir: Lists all files and directories in a specific Obsidian directory
- get_file_contents: Return the content of a single file in your vault.
- search: Search for documents matching a specified text query across all files in the vault
- patch_content: Insert content into an existing note relative to a heading, block reference, or frontmatter field.
- append_content: Append content to a new or existing file in the vault.
- delete_file: Delete a file or directory from your vault.

### Example prompts

Its good to first instruct Claude to use Obsidian. Then it will always call the tool.

The use prompts like this:
- Get the contents of the last architecture call note and summarize them
- Search for all files where Azure CosmosDb is mentioned and quickly explain to me the context in which it is mentioned
- Summarize the last meeting notes and put them into a new note 'summary meeting.md'. Add an introduction so that I can send it via email.

## Configuration

### Obsidian REST API Key

There are two ways to configure the environment with the Obsidian REST API Key. 

1. Add to server config (preferred)

```json
{
  "mcp-obsidian": {
    "command": "uvx",
    "args": [
      "mcp-obsidian",
      "--transport",
      "sse",
      "--port",
      "8000"
    ],
    "env": {
      "OBSIDIAN_API_KEY": "<your_api_key_here>",
      "OBSIDIAN_HOST": "<your_obsidian_host>",
      "OBSIDIAN_PORT": "<your_obsidian_port>"
    }
  }
}
```
Sometimes Claude has issues detecting the location of uv / uvx. You can use `which uvx` to find and paste the full path in above config in such cases.

2. Create a `.env` file in the working directory with the following required variables:

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=your_obsidian_host
OBSIDIAN_PORT=your_obsidian_port
```

Note:
- You can find the API key in the Obsidian plugin config
- Default port is 27124 if not specified
- Default host is 127.0.0.1 if not specified

## Quickstart

### Install

#### Obsidian REST API

You need the Obsidian REST API community plugin running: https://github.com/coddingtonbear/obsidian-local-rest-api

Install and enable it in the settings and copy the api key.

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

## Usage Modes

### Mode 1: Standalone Server (Recommended for Multi-Client)

**Step 1: Start the Server Independently**

Open a terminal, navigate to the project directory, and run:

```bash
# Start with SSE transport (recommended for multi-client)
uv run mcp-obsidian --transport sse --port 8000

# Or start with stdio transport (single client)
uv run mcp-obsidian --transport stdio

# Or start with streamable-http transport
uv run mcp-obsidian --transport streamable-http --port 8000
```

Keep this terminal window open for the server to remain active.

**Step 2: Configure Client to Connect**

Configure your MCP client to connect to the running server:

<details>
  <summary>Claude Desktop Configuration (SSE Mode)</summary>
  
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "transport": "sse",
      "url": "http://127.0.0.1:8000/mcp",
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_HOST": "<your_obsidian_host>",
        "OBSIDIAN_PORT": "<your_obsidian_port>"
      }
    }
  }
}
```
</details>

<details>
  <summary>mcp-agent Configuration (SSE Mode)</summary>
  
```yaml
# mcp_agent.config.yaml
mcp:
  servers:
    obsidian:
      transport: "sse"
      url: "http://127.0.0.1:8000/mcp"
      env:
        OBSIDIAN_API_KEY: "<your_api_key_here>"
        OBSIDIAN_HOST: "<your_obsidian_host>"
        OBSIDIAN_PORT: "<your_obsidian_port>"
```
</details>

### Mode 2: Client-Launched Server (Single Client Only)

For single client usage, you can let the client launch the server automatically:

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uv",
      "args": [
        "--directory",
        "<dir_to>/mcp-obsidian",
        "run",
        "mcp-obsidian",
        "--transport",
        "stdio"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_HOST": "<your_obsidian_host>",
        "OBSIDIAN_PORT": "<your_obsidian_port>"
      }
    }
  }
}
```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uvx",
      "args": [
        "mcp-obsidian",
        "--transport",
        "stdio"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<YOUR_OBSIDIAN_API_KEY>",
        "OBSIDIAN_HOST": "<your_obsidian_host>",
        "OBSIDIAN_PORT": "<your_obsidian_port>"
      }
    }
  }
}
```
</details>

**Note**: Mode 2 is limited to single client usage and uses stdio transport. For multi-client support, use Mode 1.

## Development

### Running as a Network Server (for Multi-Client Support)

The server now uses FastMCP framework and supports multiple transport protocols. The default `stdio` transport limits the server to a single client. To support multiple clients simultaneously, you can run the server in SSE mode. This is the recommended approach for any shared or multi-user environment.

**Step 1: Start the Server**

Open a terminal, navigate to the project directory, and run one of the following commands:

```bash
# Start with SSE transport (recommended for multi-client)
uv run mcp-obsidian --transport sse --port 8000

# Start with stdio transport (single client)
uv run mcp-obsidian --transport stdio

# Start with streamable-http transport
uv run mcp-obsidian --transport streamable-http --port 8000
```

You must keep this terminal window open for the server to remain active.

**Step 2: Configure Your Client**

Now, configure your MCP client (e.g., another `mcp-agent` application, Claude Desktop) to connect to the server's URL instead of launching it as a command.

Update your client's configuration (e.g., `mcp_agent.config.yaml` or `claude_desktop_config.json`) with the following settings:

```yaml
# Example for an mcp-agent client (mcp_agent.config.yaml)
mcp:
  servers:
    obsidian:
      transport: "sse" # Server-Sent Events
      url: "http://127.0.0.1:8000/mcp"
      # No command or args needed
      env:
        OBSIDIAN_API_KEY: "<your_api_key_here>"
        OBSIDIAN_HOST": "<your_obsidian_host>"
        OBSIDIAN_PORT": "<your_obsidian_port>"
```

This change fundamentally alters the server's architecture from a single-use tool to a shareable service.

### Transport Options

The server supports three transport protocols:

- **stdio**: Standard input/output transport (default, single client)
- **sse**: Server-Sent Events transport (recommended for multi-client)
- **streamable-http**: Streamable HTTP transport

### Building

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-obsidian run mcp-obsidian --transport sse --port 8000
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

You can also watch the server logs with this command:

```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp-server-mcp-obsidian.log
```
