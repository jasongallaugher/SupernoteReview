# Supernote Manta Review CLI

A streamlined, round-trip workflow for reviewing agent-generated Markdown files on the **Supernote Manta (A5X/A6X/Nomad)**. 

This tool provides a "Human-in-the-loop" bridge for AI agents to send documents to your e-ink tablet for handwriting annotation and pull them back into the development context.

## 🚀 Features

-   **E-Ink Optimization:** Automatically converts Markdown to high-contrast, large-serif PDFs optimized for reading on e-ink displays.
-   **Seamless Transfer:** Pushes files directly to your Supernote via wireless ADB and **automatically launches** the native PDF viewer.
-   **Intelligent Retrieval:** Pulls annotated "Export" files back from your device, handling timestamp drifts with fuzzy-matching logic.
-   **Agent Ready:** Designed to work with multimodal LLM CLIs (Claude, Gemini, etc.), providing a structured Markdown artifact and direct file links for agent consumption.
-   **Standalone Binary:** Packaged as a single executable for easy installation without Python environment overhead.

## 🛠 Installation

### Prerequisites
- **ADB:** Ensure Android Debug Bridge is installed (`brew install android-platform-tools`).
- **Supernote Setup:** Enable "USB Debugging" in your Supernote settings. For wireless use, run `adb connect <device-ip>`.

### Fast Install (Binary)
Move the compiled binary to your local path:
```bash
mv dist/sn-review /usr/local/bin/
```

### Developer Setup (using uv)
```bash
git clone https://github.com/your-username/SupernoteReview.git
cd SupernoteReview
uv sync
```

## 📖 Usage

### Start a Review
Convert a local Markdown file and pop it open on your Supernote:
```bash
sn-review review FEATURE_SPEC.md
```
The file will be pushed to `/Document/PDFs/ForReview/` on the device.

### Complete a Review
1.  On your Supernote, use the toolbar to **Export** your annotations (this bakes the handwriting into the PDF).
2.  Run the retrieval command:
```bash
sn-review done FEATURE_SPEC
```
This downloads the annotated PDF and generates a `FEATURE_SPEC-review.md` report.

### List Pending Reviews
```bash
sn-review list
```

## 🤖 LLM / Agent Integration

This tool is designed to be invoked by AI agents. A detailed **[Integration Guide](INTEGRATION.md)** is provided, including:
- **System Prompt Addendum:** How to teach the agent to use the tablet.
- **Tool Schemas:** OpenAI/Gemini compatible JSON definitions for function calling.
- **Multimodal Workflow:** Instructions for models to "read" the handwriting via the linked PDF.

To view the integration guide directly from the CLI:
```bash
sn-review usage
```

## 🧪 Testing
The project includes a robust suite of sanity tests covering conversion, state management, and device logic.
```bash
uv run pytest
```

---
*Created with ❤️ for the Supernote community.*