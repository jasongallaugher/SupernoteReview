import pytest
import subprocess
from unittest.mock import MagicMock
from mcp.types import TextContent
from sn.mcp_server import list_tools, sn_review, sn_done, sn_list


@pytest.mark.anyio
async def test_list_tools():
    """Verify list_tools returns 3 tools with correct names."""
    tools = await list_tools()

    assert len(tools) == 3
    tool_names = [tool.name for tool in tools]
    assert "sn_review" in tool_names
    assert "sn_done" in tool_names
    assert "sn_list" in tool_names

    # Verify sn_review tool schema
    sn_review_tool = next(t for t in tools if t.name == "sn_review")
    assert "file_path" in sn_review_tool.inputSchema["required"]

    # Verify sn_done tool has optional file_pattern
    sn_done_tool = next(t for t in tools if t.name == "sn_done")
    assert "file_pattern" in sn_done_tool.inputSchema["properties"]
    assert "required" not in sn_done_tool.inputSchema or "file_pattern" not in sn_done_tool.inputSchema.get("required", [])

    # Verify sn_list has no required params
    sn_list_tool = next(t for t in tools if t.name == "sn_list")
    assert sn_list_tool.inputSchema["properties"] == {}


@pytest.mark.anyio
async def test_sn_review_success(mocker):
    """Mock subprocess.run to return success, verify correct args passed."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Review sent successfully."
    mock_result.stderr = ""

    mock_run = mocker.patch("subprocess.run", return_value=mock_result)

    result = await sn_review("/path/to/test.md")

    # Verify subprocess.run was called with correct arguments
    mock_run.assert_called_once_with(
        ["sn-review", "review", "/path/to/test.md"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Verify return value
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert "Review sent successfully." in result[0].text


@pytest.mark.anyio
async def test_sn_review_success_with_stderr(mocker):
    """Test that stderr info is appended when present along with success."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Review sent successfully."
    mock_result.stderr = "Warning: Some deprecation notice"

    mocker.patch("subprocess.run", return_value=mock_result)

    result = await sn_review("/path/to/test.md")

    assert len(result) == 1
    assert "Review sent successfully." in result[0].text
    assert "Additional info:" in result[0].text
    assert "Warning: Some deprecation notice" in result[0].text


@pytest.mark.anyio
async def test_sn_review_empty_stdout(mocker):
    """Test default message when stdout is empty."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    mocker.patch("subprocess.run", return_value=mock_result)

    result = await sn_review("/path/to/test.md")

    assert len(result) == 1
    assert "Review successfully sent to device." in result[0].text


@pytest.mark.anyio
async def test_sn_done_with_pattern(mocker):
    """Mock subprocess, call with file_pattern, verify pattern is passed to command."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Review retrieved."
    mock_result.stderr = ""

    mock_run = mocker.patch("subprocess.run", return_value=mock_result)

    result = await sn_done("draft")

    # Verify subprocess.run was called with pattern argument
    mock_run.assert_called_once_with(
        ["sn-review", "done", "draft"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Verify return value
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert "Review retrieved." in result[0].text


@pytest.mark.anyio
async def test_sn_done_without_pattern(mocker):
    """Mock subprocess, call without pattern, verify command has no extra arg."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "All reviews retrieved."
    mock_result.stderr = ""

    mock_run = mocker.patch("subprocess.run", return_value=mock_result)

    # Call with empty string (default)
    result = await sn_done("")

    # Verify subprocess.run was called without pattern argument
    mock_run.assert_called_once_with(
        ["sn-review", "done"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Verify return value
    assert len(result) == 1
    assert "All reviews retrieved." in result[0].text


@pytest.mark.anyio
async def test_sn_done_default_message(mocker):
    """Test default message when stdout is empty."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    mocker.patch("subprocess.run", return_value=mock_result)

    result = await sn_done()

    assert len(result) == 1
    assert "Review retrieved successfully." in result[0].text


@pytest.mark.anyio
async def test_sn_list_success(mocker):
    """Mock subprocess, verify correct command called."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Pending reviews:\n- test.md\n- draft.md"
    mock_result.stderr = ""

    mock_run = mocker.patch("subprocess.run", return_value=mock_result)

    result = await sn_list()

    # Verify subprocess.run was called with correct arguments
    mock_run.assert_called_once_with(
        ["sn-review", "list"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Verify return value
    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert "test.md" in result[0].text
    assert "draft.md" in result[0].text


@pytest.mark.anyio
async def test_sn_list_default_message(mocker):
    """Test default message when no pending reviews."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""

    mocker.patch("subprocess.run", return_value=mock_result)

    result = await sn_list()

    assert len(result) == 1
    assert "No pending reviews." in result[0].text


@pytest.mark.anyio
async def test_error_timeout(mocker):
    """Mock subprocess.TimeoutExpired, verify graceful error message."""
    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="sn-review", timeout=60)
    )

    result = await sn_review("/path/to/test.md")

    assert len(result) == 1
    assert "Error: Command timed out after 60 seconds" in result[0].text
    assert "Check device connection" in result[0].text


@pytest.mark.anyio
async def test_error_timeout_sn_done(mocker):
    """Test timeout error for sn_done."""
    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="sn-review", timeout=60)
    )

    result = await sn_done("pattern")

    assert len(result) == 1
    assert "Error: Command timed out after 60 seconds" in result[0].text


@pytest.mark.anyio
async def test_error_timeout_sn_list(mocker):
    """Test timeout error for sn_list has different timeout."""
    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="sn-review", timeout=30)
    )

    result = await sn_list()

    assert len(result) == 1
    assert "Error: Command timed out after 30 seconds" in result[0].text


@pytest.mark.anyio
async def test_error_command_not_found(mocker):
    """Mock FileNotFoundError, verify graceful error message."""
    mocker.patch("subprocess.run", side_effect=FileNotFoundError())

    result = await sn_review("/path/to/test.md")

    assert len(result) == 1
    assert "Error: sn-review command not found" in result[0].text
    assert "Make sure SupernoteReview is installed" in result[0].text


@pytest.mark.anyio
async def test_error_command_not_found_sn_done(mocker):
    """Test FileNotFoundError for sn_done."""
    mocker.patch("subprocess.run", side_effect=FileNotFoundError())

    result = await sn_done()

    assert len(result) == 1
    assert "Error: sn-review command not found" in result[0].text


@pytest.mark.anyio
async def test_error_command_not_found_sn_list(mocker):
    """Test FileNotFoundError for sn_list."""
    mocker.patch("subprocess.run", side_effect=FileNotFoundError())

    result = await sn_list()

    assert len(result) == 1
    assert "Error: sn-review command not found" in result[0].text


@pytest.mark.anyio
async def test_error_nonzero_exit(mocker):
    """Mock subprocess returning non-zero exit code, verify error handling."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Error: Device not found"

    mocker.patch("subprocess.run", return_value=mock_result)

    result = await sn_review("/path/to/test.md")

    assert len(result) == 1
    assert "Error sending review (exit code 1)" in result[0].text
    assert "Error: Device not found" in result[0].text


@pytest.mark.anyio
async def test_error_nonzero_exit_sn_done(mocker):
    """Test non-zero exit code for sn_done."""
    mock_result = MagicMock()
    mock_result.returncode = 2
    mock_result.stdout = ""
    mock_result.stderr = "No reviews found"

    mocker.patch("subprocess.run", return_value=mock_result)

    result = await sn_done("pattern")

    assert len(result) == 1
    assert "Error retrieving review (exit code 2)" in result[0].text
    assert "No reviews found" in result[0].text


@pytest.mark.anyio
async def test_error_nonzero_exit_sn_list(mocker):
    """Test non-zero exit code for sn_list."""
    mock_result = MagicMock()
    mock_result.returncode = 3
    mock_result.stdout = "Some output"
    mock_result.stderr = ""

    mocker.patch("subprocess.run", return_value=mock_result)

    result = await sn_list()

    assert len(result) == 1
    assert "Error listing reviews (exit code 3)" in result[0].text
    assert "Some output" in result[0].text


@pytest.mark.anyio
async def test_error_nonzero_exit_stdout_fallback(mocker):
    """Test that stdout is used when stderr is empty."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = "Error from stdout"
    mock_result.stderr = ""

    mocker.patch("subprocess.run", return_value=mock_result)

    result = await sn_review("/path/to/test.md")

    assert len(result) == 1
    assert "Error from stdout" in result[0].text


@pytest.mark.anyio
async def test_unexpected_exception(mocker):
    """Test handling of unexpected exceptions."""
    mocker.patch("subprocess.run", side_effect=RuntimeError("Unexpected error"))

    result = await sn_review("/path/to/test.md")

    assert len(result) == 1
    assert "Unexpected error: Unexpected error" in result[0].text


@pytest.mark.anyio
async def test_unexpected_exception_sn_done(mocker):
    """Test handling of unexpected exceptions for sn_done."""
    mocker.patch("subprocess.run", side_effect=RuntimeError("Something went wrong"))

    result = await sn_done()

    assert len(result) == 1
    assert "Unexpected error: Something went wrong" in result[0].text


@pytest.mark.anyio
async def test_unexpected_exception_sn_list(mocker):
    """Test handling of unexpected exceptions for sn_list."""
    mocker.patch("subprocess.run", side_effect=ValueError("Invalid value"))

    result = await sn_list()

    assert len(result) == 1
    assert "Unexpected error: Invalid value" in result[0].text
