import pypandoc
from weasyprint import HTML, CSS
from pathlib import Path

def convert_to_pdf(input_path, output_path):
    """
    Converts markdown to PDF optimized for E-ink using WeasyPrint.
    """
    # 1. Convert Markdown to HTML using Pandoc
    html_content = pypandoc.convert_file(str(input_path), 'html')
    
    # 2. Define E-ink optimized CSS
    css_content = """
    @page {
        size: A5;
        margin: 15mm;
    }
    body {
        font-family: "Georgia", serif;
        font-size: 11pt;
        line-height: 1.5;
        color: black;
        background-color: white;
    }
    h1, h2, h3, h4 {
        font-family: "Georgia", serif;
        font-weight: bold;
        margin-top: 1.2em;
    }
    h1 { font-size: 18pt; }
    h2 { font-size: 15pt; }
    h3 { font-size: 13pt; }
    
    code, pre {
        font-family: "Courier New", monospace;
        font-size: 9pt;
        background-color: #f0f0f0;
    }
    blockquote {
        border-left: 2px solid black;
        padding-left: 1em;
        margin-left: 0;
        font-style: italic;
        font-size: 10pt;
    }
    img {
        max-width: 100%;
        height: auto;
    }
    """
    
    # 3. Generate PDF
    HTML(string=html_content).write_pdf(
        str(output_path),
        stylesheets=[CSS(string=css_content)]
    )

def get_pdf_name(input_path):
    p = Path(input_path)
    return p.with_suffix('.pdf').name