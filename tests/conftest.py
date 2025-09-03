import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_pdf_path(temp_dir):
    """Create a mock PDF file path for testing."""
    pdf_path = temp_dir / "sample.pdf"
    # Create an empty file to simulate a PDF
    pdf_path.write_bytes(b"%PDF-1.4\n%Mock PDF content for testing")
    return str(pdf_path)


@pytest.fixture
def output_dir(temp_dir):
    """Create a temporary output directory."""
    output_path = temp_dir / "output"
    output_path.mkdir()
    return str(output_path)


@pytest.fixture
def mock_qapplication():
    """Mock QApplication for testing PyQt components without GUI."""
    mock_app = MagicMock()
    return mock_app


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing command execution."""
    mock_subprocess = Mock()
    mock_subprocess.run.return_value = Mock(returncode=0)
    return mock_subprocess


@pytest.fixture
def sample_config():
    """Provide sample configuration data for testing."""
    return {
        "compression_level": "medium",
        "output_folder": "~/Desktop",
        "quality_settings": {
            "high": "/printer",
            "medium": "/ebook", 
            "low": "/screen"
        }
    }


@pytest.fixture
def mock_file_system(temp_dir):
    """Create a mock file system structure for testing."""
    # Create some test files
    (temp_dir / "test.pdf").write_bytes(b"%PDF-1.4\nTest PDF")
    (temp_dir / "large.pdf").write_bytes(b"%PDF-1.4\n" + b"x" * 1024 * 1024)  # 1MB file
    (temp_dir / "empty.pdf").write_bytes(b"")
    
    return temp_dir


@pytest.fixture
def mock_ghostscript_command():
    """Mock Ghostscript command for PDF compression testing."""
    return [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/screen",
        "-dNOPAUSE",
        "-dBATCH",
        "-sOutputFile=output.pdf",
        "input.pdf"
    ]


@pytest.fixture
def mock_pyqt_widgets():
    """Mock PyQt widgets for testing UI components."""
    widgets = MagicMock()
    widgets.QWidget = MagicMock()
    widgets.QPushButton = MagicMock()
    widgets.QLabel = MagicMock()
    widgets.QFileDialog = MagicMock()
    widgets.QMessageBox = MagicMock()
    return widgets


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup common test environment variables."""
    # Set test environment variables
    monkeypatch.setenv("TESTING", "true")
    # Mock home directory for consistent testing
    monkeypatch.setenv("HOME", "/tmp/test_home")


@pytest.fixture
def large_file_content():
    """Generate large file content for testing file size operations."""
    return b"x" * (5 * 1024 * 1024)  # 5MB of data


@pytest.fixture
def compression_test_data():
    """Provide test data for compression operations."""
    return {
        "input_sizes": [100, 1024, 1024*1024, 5*1024*1024],  # bytes
        "compression_ratios": [0.1, 0.3, 0.5, 0.7],
        "quality_levels": ["low", "medium", "high"]
    }