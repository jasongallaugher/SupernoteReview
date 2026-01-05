import click
import os
from pathlib import Path
from datetime import datetime
from .device import SupernoteDevice
from .converter import convert_to_pdf
from . import state

@click.group()
def cli():
    """Manta Review CLI - Supernote round-trip workflow."""
    pass

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
def review(file_path):
    """Push a markdown file to Supernote for review."""
    file_path = Path(file_path)
    
    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_name = f"{file_path.stem}_{timestamp}.pdf"
    
    local_pdf = file_path.parent / pdf_name
    remote_path = f"/storage/emulated/0/Document/PDFs/ForReview/{pdf_name}"

    click.echo(f"  -> Input: {file_path}")
    click.echo(f"  -> Output: {local_pdf}")
    click.echo(f"  -> Remote: {remote_path}")
    
    click.echo(f"\n[1/3] Converting Markdown to PDF...")
    convert_to_pdf(file_path, local_pdf)
    file_size_kb = local_pdf.stat().st_size / 1024
    click.echo(f"  -> PDF generated ({file_size_kb:.1f} KB)")

    click.echo(f"[2/3] Connecting to Supernote...")
    try:
        device = SupernoteDevice()
        click.echo(f"  -> Connected to {device.device.serial}")
        
        click.echo(f"[3/3] Pushing file...")
        device.push(str(local_pdf), remote_path)
        state.add_review(file_path, remote_path)
        click.echo(f"  -> Upload complete")
        
        click.echo("Launching viewer on device...")
        device.open_pdf(remote_path)
        
        click.echo("\nSuccess! Document is open for review.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.argument('file_pattern', required=False)
def done(file_pattern):
    """Retrieve annotated PDF and generate review summary."""
    pending = state.get_pending_reviews()
    
    if not pending:
        click.echo("No pending reviews found.")
        return

    # If pattern is provided, filter; otherwise list and ask
    targets = []
    if file_pattern:
        targets = [k for k in pending if file_pattern in k]
    else:
        # Just pick the most recent or list them
        targets = list(pending.keys())

    if not targets:
        click.echo(f"No pending review matching '{file_pattern}'")
        return

    for local_path_str in targets:
        info = pending[local_path_str]
        local_path = Path(local_path_str)
        remote_path = info['device_path']
        
        # The file on device is named like: file_TIMESTAMP.pdf
        # If the user exports it, it ends up in /storage/emulated/0/EXPORT/file_TIMESTAMP.pdf
        
        export_name = Path(remote_path).name
        remote_export_path = f"/storage/emulated/0/EXPORT/{export_name}"
        
        click.echo(f"\nProcessing review for: {local_path.name}")
        click.echo(f"  -> Looking for exact export: {export_name}")
        
        device = SupernoteDevice()
        pull_path = None
        
        # 1. Try Exact Match
        if device.exists(remote_export_path):
            pull_path = remote_export_path
            click.echo(f"  -> Exact match found!")
            
        # 2. Try Fuzzy Match (Same stem, different timestamp)
        else:
            click.echo(f"  -> Exact match not found. Searching for other versions...")
            # Pattern: stem_*.pdf
            search_prefix = f"{local_path.stem}_"
            candidates = []
            
            try:
                files = device.list_dir("/storage/emulated/0/EXPORT/")
                for f in files:
                    if f.startswith(search_prefix) and f.endswith(".pdf"):
                        candidates.append(f)
            except Exception as e:
                click.echo(f"  -> [WARN] Error listing exports: {e}", err=True)

            if candidates:
                # Pick the most recent (assuming standard naming sort works or just last one)
                candidates.sort() 
                best_match = candidates[-1]
                pull_path = f"/storage/emulated/0/EXPORT/{best_match}"
                click.echo(f"  -> Found alternative: {best_match}")
            else:
                # 3. Fallback to original remote path (un-annotated)
                click.echo(f"  -> [WARN] No exported annotations found. Pulling original file.", err=True)
                pull_path = remote_path

        # We pull it back to a distinct name to avoid overwriting previous reviews if any
        reviewed_pdf_name = f"{local_path.stem}_reviewed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        reviewed_pdf = local_path.parent / reviewed_pdf_name
        
        click.echo(f"Downloading artifact to: {reviewed_pdf.name}...")
        device.pull(pull_path, str(reviewed_pdf))
        click.echo("  -> Download complete.")
        
        # Generate review markdown (No prompt, LLM-ready)
        review_md = local_path.parent / f"{local_path.stem}-review.md"
        
        with open(review_md, "w") as f:
            f.write(f"# Review: {local_path.name}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Annotated PDF:** [{reviewed_pdf.name}]({reviewed_pdf.name})\n\n")
            f.write("## Status\n")
            f.write("Review completed on device. See annotated PDF for details.")
            f.write("\n")

        state.mark_completed(local_path_str)
        click.echo(f"Created review report: {review_md.name}", err=True)
        
        # Output the content to stdout for piping/agent consumption
        with open(review_md, "r") as f:
            print(f.read())

@cli.command()
def list():
    """List all pending reviews."""
    pending = state.get_pending_reviews()
    if not pending:
        click.echo("No pending reviews.")
        return
    
    click.echo("Pending Reviews:")
    for path, info in pending.items():
        click.echo(f"- {Path(path).name} (Out since: {info['timestamp']})")

@cli.command()
def usage():
    """Output the LLM integration guide and playbook."""
    guide = """
# Supernote Review Integration Guide

This tool is designed to provide a "Human-in-the-loop" review workflow for AI agents using a Supernote Manta device.

## Playbook for LLM Agents
Add the following to your system prompt:

---
### Supernote Review Capabilities
You have access to a Supernote Manta E-Ink device for human-in-the-loop reviews.
1. **request_review(file_path)**: Converts Markdown to PDF and pushes it to the user's tablet. Tell the user it's sent and wait for them to "Export" it.
2. **retrieve_review(pattern)**: Pulls the annotated PDF and the user's text summary. Use this to refine your work.
---

## Tool Schemas (OpenAI/Gemini Format)
```json
[
  {
    "name": "request_review",
    "description": "Push markdown to Supernote for review",
    "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}}
  },
  {
    "name": "retrieve_review",
    "description": "Pull annotated results from Supernote",
    "parameters": {"type": "object", "properties": {"file_pattern": {"type": "string"}}}
  }
]
```

## Multimodal Workflow
When `retrieve_review` is called, the tool returns a Markdown summary. This summary contains a local file link to the **Annotated PDF**. 
**If you are a multimodal model:** You should read this PDF file directly to see the user's handwritten notes and drawings alongside their text summary.
"""
    click.echo(guide)

if __name__ == '__main__':
    cli()