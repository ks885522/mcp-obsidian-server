from collections.abc import Sequence
from fastmcp import FastMCP
from mcp.types import (
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import json
import os
from . import obsidian

# This function will be called by server.py to register all tools
def register_tools(app: FastMCP):

    def get_api_client() -> obsidian.Obsidian:
        """
        Helper function to get the Obsidian API client.
        It checks for the API key environment variable right before it's needed.
        """
        api_key = os.getenv("OBSIDIAN_API_KEY")
        if not api_key:
            raise ValueError(f"OBSIDIAN_API_KEY environment variable not set or found. Working directory: {os.getcwd()}")
        
        obsidian_host = os.getenv("OBSIDIAN_HOST", "127.0.0.1")
        return obsidian.Obsidian(api_key=api_key, host=obsidian_host)

    @app.tool()
    async def obsidian_list_files_in_vault() -> str:
        """Lists all files and directories in the root directory of your Obsidian vault."""
        api = get_api_client()
        files = await api.list_files_in_vault()
        return json.dumps(files, indent=2)

    @app.tool()
    async def obsidian_list_files_in_dir(dirpath: str) -> str:
        """
        Lists all files and directories that exist in a specific Obsidian directory.
        
        :param dirpath: Path to list files from (relative to your vault root). Note that empty directories will not be returned.
        """
        api = get_api_client()
        files = await api.list_files_in_dir(dirpath)
        return json.dumps(files, indent=2)

    @app.tool()
    async def obsidian_get_file_contents(filepath: str) -> str:
        """
        Return the content of a single file in your vault.
        
        :param filepath: Path to the relevant file (relative to your vault root).
        """
        api = get_api_client()
        content = await api.get_file_contents(filepath)
        return json.dumps(content, indent=2)

    @app.tool()
    async def obsidian_simple_search(query: str, context_length: int = 100) -> str:
        """
        Simple search for documents matching a specified text query across all files in the vault. 
        Use this tool when you want to do a simple text search.
        
        :param query: Text to a simple search for in the vault.
        :param context_length: How much context to return around the matching string (default: 100).
        """
        api = get_api_client()
        results = await api.search(query, context_length)
        # Formatting logic remains the same as before
        formatted_results = []
        for result in results:
            formatted_matches = []
            for match in result.get('matches', []):
                context = match.get('context', '')
                match_pos = match.get('match', {})
                start = match_pos.get('start', 0)
                end = match_pos.get('end', 0)
                
                formatted_matches.append({
                    'context': context,
                    'match_position': {'start': start, 'end': end}
                })
                
            formatted_results.append({
                'filename': result.get('filename', ''),
                'score': result.get('score', 0),
                'matches': formatted_matches
            })
        return json.dumps(formatted_results, indent=2)

    @app.tool()
    async def obsidian_append_content(filepath: str, content: str) -> str:
        """
        Append content to a new or existing file in the vault.
        
        :param filepath: Path to the file (relative to vault root).
        :param content: Content to append to the file.
        """
        api = get_api_client()
        await api.append_content(filepath, content)
        return f"Successfully appended content to {filepath}"

    @app.tool()
    async def obsidian_patch_content(filepath: str, operation: str, target_type: str, target: str, content: str) -> str:
        """
        Insert content into an existing note relative to a heading, block reference, or frontmatter field.
        
        :param filepath: Path to the file (relative to vault root).
        :param operation: Operation to perform (append, prepend, or replace).
        :param target_type: Type of target to patch (heading, block, or frontmatter).
        :param target: Target identifier (heading path, block reference, or frontmatter field).
        :param content: Content to insert.
        """
        api = get_api_client()
        await api.patch_content(filepath, operation, target_type, target, content)
        return f"Successfully patched content in {filepath}"

    @app.tool()
    async def obsidian_put_content(filepath: str, content: str) -> str:
        """
        Create a new file in your vault or update the content of an existing one in your vault.
        
        :param filepath: Path to the relevant file (relative to your vault root).
        :param content: Content of the file you would like to upload.
        """
        api = get_api_client()
        await api.put_content(filepath, content)
        return f"Successfully uploaded content to {filepath}"

    @app.tool()
    async def obsidian_delete_file(filepath: str, confirm: bool = False) -> str:
        """
        Delete a file or directory from the vault.
        
        :param filepath: Path to the file or directory to delete (relative to vault root).
        :param confirm: Confirmation to delete the file (must be true).
        """
        if not confirm:
            raise ValueError("confirm must be set to true to delete a file")
        api = get_api_client()
        await api.delete_file(filepath)
        return f"Successfully deleted {filepath}"

    @app.tool()
    async def obsidian_complex_search(query: dict) -> str:
        """
        Complex search for documents using a JsonLogic query. 
        Supports standard JsonLogic operators plus 'glob' and 'regexp' for pattern matching.
        
        :param query: JsonLogic query object.
        """
        api = get_api_client()
        results = await api.search_json(query)
        return json.dumps(results, indent=2)

    @app.tool()
    async def obsidian_batch_get_file_contents(filepaths: list[str]) -> str:
        """
        Return the contents of multiple files in your vault, concatenated with headers.
        
        :param filepaths: List of file paths to read.
        """
        api = get_api_client()
        content = await api.get_batch_file_contents(filepaths)
        return content

    @app.tool()
    async def obsidian_get_periodic_note(period: str, type: str = "content") -> str:
        """
        Get current periodic note for the specified period.
        
        :param period: The period type (daily, weekly, monthly, quarterly, yearly).
        :param type: The type of data to get ('content' or 'metadata').
        """
        valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
        if period not in valid_periods:
            raise ValueError(f"Invalid period: {period}. Must be one of: {', '.join(valid_periods)}")
        valid_types = ["content", "metadata"]
        if type not in valid_types:
            raise ValueError(f"Invalid type: {type}. Must be one of: {', '.join(valid_types)}")
        api = get_api_client()
        content = await api.get_periodic_note(period, type)
        return content

    @app.tool()
    async def obsidian_get_recent_periodic_notes(period: str, limit: int = 5, include_content: bool = False) -> str:
        """
        Get most recent periodic notes for the specified period type.
        
        :param period: The period type (daily, weekly, monthly, quarterly, yearly).
        :param limit: Maximum number of notes to return (default: 5).
        :param include_content: Whether to include note content (default: false).
        """
        api = get_api_client()
        results = await api.get_recent_periodic_notes(period, limit, include_content)
        return json.dumps(results, indent=2)

    @app.tool()
    async def obsidian_get_recent_changes(limit: int = 10, days: int = 90) -> str:
        """
        Get recently modified files in the vault.
        
        :param limit: Maximum number of files to return (default: 10).
        :param days: Only include files modified within this many days (default: 90).
        """
        api = get_api_client()
        results = await api.get_recent_changes(limit, days)
        return json.dumps(results, indent=2)