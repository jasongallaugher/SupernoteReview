import pytest
from click.testing import CliRunner
from sn.main import cli
from unittest.mock import MagicMock

@pytest.fixture
def runner():
    return CliRunner()

def test_usage_command(runner):
    result = runner.invoke(cli, ['usage'])
    assert result.exit_code == 0
    assert "Supernote Review Integration Guide" in result.output
    assert "Playbook for LLM Agents" in result.output

def test_list_command_empty(runner, temp_state_file):
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert "No pending reviews" in result.output

def test_review_flow(runner, temp_state_file, mocker):
    # Mock dependencies
    def mock_convert(src, dst):
        with open(dst, "w") as f: f.write("dummy pdf content")
    mocker.patch("sn.main.convert_to_pdf", side_effect=mock_convert)
    mock_dev_cls = mocker.patch("sn.main.SupernoteDevice")
    mock_dev = mock_dev_cls.return_value
    
    # Create dummy file
    with runner.isolated_filesystem():
        with open("draft.md", "w") as f:
            f.write("content")
            
        result = runner.invoke(cli, ['review', 'draft.md'])
        
        assert result.exit_code == 0
        assert "Document is open for review." in result.output
        
        # Verify push called
        assert mock_dev.push.called
        # Verify state updated
        from sn import state
        assert "draft.md" in str(list(state.get_pending_reviews().keys())[0])

def test_done_flow_exact_match(runner, temp_state_file, mocker):
    # 1. Setup State
    from sn import state
    state.add_review("draft.md", "/storage/emulated/0/Document/PDFs/ForReview/draft_123.pdf")
    
    # 2. Mock Device
    mock_dev_cls = mocker.patch("sn.main.SupernoteDevice")
    mock_dev = mock_dev_cls.return_value
    mock_dev.exists.return_value = True # Pretend export exists
    
    with runner.isolated_filesystem():
        # Create the 'draft.md' so Path(local_path).parent works
        with open("draft.md", "w") as f: f.write("src")
        
        result = runner.invoke(cli, ['done', 'draft'])
        
        assert result.exit_code == 0
        assert "Processing review for: draft.md" in result.output
        assert "Exact match found!" in result.output
        
        # Check if pulled
        mock_dev.pull.assert_called()
        
        # Check stdout has the content (for LLM)
        assert "# Review: draft.md" in result.output
        assert "See annotated PDF for details." in result.output

def test_done_flow_fuzzy_match(runner, temp_state_file, mocker):
    # 1. Setup State
    from sn import state
    state.add_review("draft.md", "/storage/emulated/0/Document/PDFs/ForReview/draft_123.pdf")
    
    # 2. Mock Device
    mock_dev_cls = mocker.patch("sn.main.SupernoteDevice")
    mock_dev = mock_dev_cls.return_value
    mock_dev.exists.return_value = False # Exact export missing
    mock_dev.list_dir.return_value = ["draft_456.pdf", "other.pdf"]
    
    with runner.isolated_filesystem():
        with open("draft.md", "w") as f: f.write("src")
        
        result = runner.invoke(cli, ['done', 'draft'])
        
        assert result.exit_code == 0
        assert "Found alternative: draft_456.pdf" in result.output
        
        # Check if pulled the alternative
        # The code sorts candidates and picks the last one
        mock_dev.pull.assert_called()
        args, _ = mock_dev.pull.call_args
        assert "draft_456.pdf" in args[0]