# SupernoteReview - Claude Integration Guide

## Purpose
The `sn-review` CLI tool enables human-in-the-loop review of markdown documents via a Supernote e-ink device using wireless ADB.

## Core Commands

### sn-review review <file.md>
Initiates a review workflow:
- Converts markdown file to PDF
- Pushes PDF to connected Supernote device
- Opens PDF viewer on device
- User annotates directly on the e-ink display

**Use this when:** You need human feedback on architecture docs, specifications, design documents, or other markdown artifacts that benefit from annotation and review.

### sn-review done [pattern]
Completes a review workflow:
- Retrieves annotated PDF from device (user must export from Supernote first)
- Outputs review summary with annotations
- Returns annotated content for integration

**Use this when:** User confirms they've finished annotating and exported the PDF on the device.

### sn-review list
Shows all pending reviews waiting for user input or retrieval.

**Use this when:** You need to check current review status.

## Workflow

1. **Initiate Review**: When user requests feedback on a markdown document, run `sn-review review <file.md>`
2. **Wait for User**: Inform user to annotate on device and export the PDF when done
3. **Retrieve Results**: Once user confirms export, run `sn-review done` to get annotated version
4. **Process Output**: Integrate the review feedback back into the document or workflow

## Prerequisites
- Supernote device connected via wireless ADB
- Device has export capability configured

## Integration Notes
- Always wait for user confirmation before running `sn-review done`
- File paths should be absolute or relative to current working directory
- PDF conversion happens automatically via markdown parsing
