# Supernote Review Integration Guide

This tool is designed to provide a "Human-in-the-loop" review workflow for AI agents using a Supernote Manta device.

## Playbook for LLM Agents
Add the following to your system prompt to teach the agent how to use the device:

---
### Supernote Review Capabilities
You have access to a Supernote Manta E-Ink device for human-in-the-loop reviews.

1. **request_review(file_path)**: Converts Markdown to PDF and pushes it to the user's tablet. 
   - **When to use:** Use this when you need detailed feedback, validation of long documents, or creative direction where visual annotations might help.
   - **Instruction:** Tell the user you have sent the file and are waiting for them to "Export" the review on their device. Stop generating and wait for the user to confirm they are done.

2. **retrieve_review(pattern)**: Pulls the annotated PDF and the user's text summary from the device.
   - **Instruction:** Use the returned text summary and (if multimodal) the linked PDF to revise your previous work.
---

## Tool Schemas (OpenAI/Gemini Format)
```json
[
  {
    "name": "request_review",
    "description": "Push markdown to Supernote for review",
    "parameters": {
      "type": "object", 
      "properties": {
        "file_path": {"type": "string", "description": "Local path to the .md file"}
      },
      "required": ["file_path"]
    }
  },
  {
    "name": "retrieve_review",
    "description": "Pull annotated results from Supernote",
    "parameters": {
      "type": "object", 
      "properties": {
        "file_pattern": {"type": "string", "description": "Optional pattern to match file"}
      }
    }
  }
]
```

## Multimodal Workflow
When `retrieve_review` is called, the tool returns a Markdown summary. This summary contains a local file link to the **Annotated PDF**. 

**Important for Multimodal Models:** 
The summary you receive is the user's *typed* feedback. However, the most valuable information is often in the **Annotated PDF**. You should utilize your visual capabilities to read the PDF file linked in the summary to interpret handwritten notes, circled text, and diagrams provided by the user.