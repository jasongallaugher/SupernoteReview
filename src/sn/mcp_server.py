"""MCP Server for SupernoteReview CLI.

This server provides MCP tools for the Supernote Review workflow, enabling
AI assistants to manage human-in-the-loop reviews on a Supernote device.
"""

import asyncio
import subprocess
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool


# Initialize the MCP server
app = Server("supernote")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Supernote tools."""
    return [
        Tool(
            name="sn_review",
            description=(
                "Push a markdown file to Supernote device for human review. "
                "Converts the markdown to PDF and uploads it to the connected Supernote tablet. "
                "Use this when you need human feedback on a document you've created. "
                "The user will review it on their e-ink tablet and export it when done."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the markdown file to review",
                    }
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="sn_done",
            description=(
                "Retrieve annotated PDF from Supernote device and generate review summary. "
                "Pulls back the reviewed document with annotations from the device. "
                "Use this after the user has completed their review and exported the PDF. "
                "If file_pattern is provided, only retrieves reviews matching that pattern. "
                "If omitted, retrieves all pending reviews."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_pattern": {
                        "type": "string",
                        "description": "Optional pattern to filter which reviews to retrieve",
                    }
                },
            },
        ),
        Tool(
            name="sn_list",
            description=(
                "List all pending reviews waiting to be retrieved from the Supernote device. "
                "Shows which documents have been sent for review but not yet pulled back. "
                "Use this to check the status of ongoing reviews."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""

    if name == "sn_review":
        return await sn_review(arguments["file_path"])
    elif name == "sn_done":
        file_pattern = arguments.get("file_pattern", "")
        return await sn_done(file_pattern)
    elif name == "sn_list":
        return await sn_list()
    else:
        raise ValueError(f"Unknown tool: {name}")


async def sn_review(file_path: str) -> list[TextContent]:
    """Push a markdown file to Supernote for review."""
    try:
        result = subprocess.run(
            ["sn-review", "review", file_path],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            output = result.stdout if result.stdout else "Review successfully sent to device."
            if result.stderr:
                output += f"\n\nAdditional info:\n{result.stderr}"
            return [TextContent(type="text", text=output)]
        else:
            error_msg = f"Error sending review (exit code {result.returncode}):\n{result.stderr or result.stdout}"
            return [TextContent(type="text", text=error_msg)]

    except subprocess.TimeoutExpired:
        return [TextContent(
            type="text",
            text="Error: Command timed out after 60 seconds. Check device connection."
        )]
    except FileNotFoundError:
        return [TextContent(
            type="text",
            text="Error: sn-review command not found. Make sure SupernoteReview is installed."
        )]
    except subprocess.CalledProcessError as e:
        return [TextContent(
            type="text",
            text=f"Error running sn-review: {e.stderr or e.stdout}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Unexpected error: {str(e)}"
        )]


async def sn_done(file_pattern: str = "") -> list[TextContent]:
    """Retrieve annotated PDF and generate review summary."""
    try:
        cmd = ["sn-review", "done"]
        if file_pattern:
            cmd.append(file_pattern)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            output = result.stdout if result.stdout else "Review retrieved successfully."
            if result.stderr:
                output += f"\n\nAdditional info:\n{result.stderr}"
            return [TextContent(type="text", text=output)]
        else:
            error_msg = f"Error retrieving review (exit code {result.returncode}):\n{result.stderr or result.stdout}"
            return [TextContent(type="text", text=error_msg)]

    except subprocess.TimeoutExpired:
        return [TextContent(
            type="text",
            text="Error: Command timed out after 60 seconds. Check device connection."
        )]
    except FileNotFoundError:
        return [TextContent(
            type="text",
            text="Error: sn-review command not found. Make sure SupernoteReview is installed."
        )]
    except subprocess.CalledProcessError as e:
        return [TextContent(
            type="text",
            text=f"Error running sn-review: {e.stderr or e.stdout}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Unexpected error: {str(e)}"
        )]


async def sn_list() -> list[TextContent]:
    """List all pending reviews."""
    try:
        result = subprocess.run(
            ["sn-review", "list"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            output = result.stdout if result.stdout else "No pending reviews."
            if result.stderr:
                output += f"\n\nAdditional info:\n{result.stderr}"
            return [TextContent(type="text", text=output)]
        else:
            error_msg = f"Error listing reviews (exit code {result.returncode}):\n{result.stderr or result.stdout}"
            return [TextContent(type="text", text=error_msg)]

    except subprocess.TimeoutExpired:
        return [TextContent(
            type="text",
            text="Error: Command timed out after 30 seconds."
        )]
    except FileNotFoundError:
        return [TextContent(
            type="text",
            text="Error: sn-review command not found. Make sure SupernoteReview is installed."
        )]
    except subprocess.CalledProcessError as e:
        return [TextContent(
            type="text",
            text=f"Error running sn-review: {e.stderr or e.stdout}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Unexpected error: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
