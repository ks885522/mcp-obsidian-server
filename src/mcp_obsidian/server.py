
import logging
import argparse
import os
from dotenv import load_dotenv
from fastmcp import FastMCP

from . import tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-obsidian")

# Create the FastMCP application instance
app = FastMCP("mcp-obsidian")

# Register all the tool functions defined in tools.py
tools.register_tools(app)

def main():
    """
    This is the main entry point for the server, executed when you run `mcp-obsidian`.
    It parses command-line arguments to decide which transport to use.
    """
    parser = argparse.ArgumentParser(description="MCP Obsidian Server")
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "sse", "streamable-http"],
        help="The transport protocol to use.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="The port to use for network transports.",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="The host to bind to for network transports.",
    )
    args = parser.parse_args()

    # Load environment variables from a .env file in the current directory
    load_dotenv()
    logger.info("Attempting to load .env file from current directory.")

    logger.info(f"Starting MCP Obsidian Server in '{args.transport}' mode")
    
    app.run(transport=args.transport, port=args.port, host=args.host)
