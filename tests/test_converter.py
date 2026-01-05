import os
from pathlib import Path
from manta.converter import convert_to_pdf, get_pdf_name

def test_get_pdf_name():
    assert get_pdf_name("test.md") == "test.pdf"
    assert get_pdf_name("path/to/doc.markdown") == "doc.pdf"

def test_convert_to_pdf_creation(tmp_path):
    """
    Functional test: Check if PDF is actually created from simple markdown.
    Requires pypandoc and weasyprint to be working.
    """
    input_md = tmp_path / "test_doc.md"
    output_pdf = tmp_path / "test_doc.pdf"
    
    input_md.write_text("# Hello World\n\nThis is a test.")
    
    try:
        convert_to_pdf(input_md, output_pdf)
        assert output_pdf.exists()
        assert output_pdf.stat().st_size > 0
    except OSError as e:
        # Fallback if system dependencies (like pandoc binary) aren't found in test env
        pytest.skip(f"Skipping PDF generation test due to missing deps: {e}")
    except Exception as e:
        # If weasyprint/font config fails
        if "Fontconfig" in str(e) or "pypandoc" in str(e):
             pytest.skip(f"Skipping PDF generation test due to config issues: {e}")
        else:
            raise e
