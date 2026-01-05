import subprocess
import json
import os
from pathlib import Path

# Path to the compiled binary
BINARY_PATH = Path(__file__).parent / "dist" / "manta-review"

# 1. System Prompt / Playbook
# Add this to your LLM's system message so it understands the workflow.
SYSTEM_PROMPT_ADDENDUM = """
## Supernote Review Capabilities
You have access to a Supernote Manta E-Ink device for human-in-the-loop reviews.
Use this workflow when you need feedback, validation, or creative direction on a document:

1.  **Request Review**: Call `request_review(file_path)` to send a Markdown file to the user's tablet. 
    *   Tell the user you have sent it and are waiting for their "Export".
    *   Stop generating and wait for the user to prompt you that they are done.

2.  **Retrieve Review**: When the user says they are done (or "check reviews"), call `retrieve_review()`.
    *   This will pull the annotated PDF and the user's text summary.
    *   The tool output will contain the user's summary and a link to the PDF.
    *   Use this feedback to revise the original document or answer questions.
"""

# 2. Tool Definitions (OpenAI Format)
# Pass this list to your LLM.ask_tool(..., tools=MANTA_TOOLS)
MANTA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "request_review",
            "description": "Sends a local markdown file to the Supernote tablet for human review.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The relative path to the markdown file to review (e.g., 'docs/draft.md')."
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_review",
            "description": "Checks for completed reviews from the Supernote. Returns the user's summary and feedback.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_pattern": {
                        "type": "string",
                        "description": "Optional filename pattern to filter specifically (e.g., 'draft'). Leave empty to check all."
                    }
                }
            }
        }
    }
]

# 3. Execution Logic
# Call this when the LLM returns a tool_call
def execute_manta_tool(tool_name: str, args: dict) -> str:
    """
    Executes the manta-review binary based on the tool selection.
    """
    cmd = [str(BINARY_PATH)]
    
    if tool_name == "request_review":
        cmd.extend(["review", args["file_path"]])
        
    elif tool_name == "retrieve_review":
        cmd.append("done")
        if "file_pattern" in args and args["file_pattern"]:
            cmd.append(args["file_pattern"])
            
    else:
        return f"Error: Unknown tool '{tool_name}'"

    try:
        # Run the binary and capture stdout/stderr
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True,
            cwd=os.getcwd() # Ensure we run from the project root
        )
        # Return stdout (which now contains the review content for 'done')
        return result.stdout.strip()
        
    except subprocess.CalledProcessError as e:
        return f"Tool execution failed: {e.stderr}"
    except Exception as e:
        return f"System error: {str(e)}"

# Example Usage
if __name__ == "__main__":
    print("Manta Agent Integration Module")
    print(f"Binary Path: {BINARY_PATH}")
    print("Import `MANTA_TOOLS` and `execute_manta_tool` into your LLM loop.")
