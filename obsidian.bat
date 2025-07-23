@echo off
setlocal

:: Change directory to the script's location to ensure uv finds the correct environment
cd /d "%~dp0"

:: Check for tool name argument
if "%~1"=="" (
    echo Error: Please provide a tool name.
    echo Usage: %0 tool_name [json_parameters]
    exit /b 1
)

set "TOOL_NAME=%~1"
:: If parameters are provided, use them, otherwise default to an empty JSON object
set "PARAMETERS=%~2"
if not defined PARAMETERS (
    set "PARAMETERS={}"
)

:: Construct the JSON payload for the MCP server
set "JSON_PAYLOAD={"mcp_version": "1.0", "request_id": "gemini-cli-req-1", "tool_calls": [{"tool_name": "%TOOL_NAME%", "parameters": %PARAMETERS%}]}"

:: Execute the command and pipe the JSON to the MCP server, redirecting stderr to stdout
echo %JSON_PAYLOAD% | uv run mcp-obsidian 2>&1

endlocal

