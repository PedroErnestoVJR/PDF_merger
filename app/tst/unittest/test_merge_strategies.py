import unittest
from unittest.mock import patch, MagicMock
import subprocess
from app.core.merge_strategies import PyPDFMergeStrategy, GhostscriptMergeStrategy

class TestPyPDFMergeStrategy(unittest.TestCase):
    @patch('app.core.merge_strategies.PdfWriter')
    def test_merge(self, MockPdfWriter):
        mock_writer_instance = MockPdfWriter.return_value
        
        strategy = PyPDFMergeStrategy()
        strategy.title = "Test Title"
        strategy.author = "Test Author"
        strategy.password = "secret"
        strategy.lossless_compression = True
        
        # Provide mock pages for compression iteration
        mock_page = MagicMock()
        mock_writer_instance.pages = [mock_page]
        
        result = strategy.merge(["file1.pdf", "file2.pdf"], "output.pdf")
        
        self.assertEqual(result, "output.pdf")
        self.assertEqual(mock_writer_instance.append.call_count, 2)
        mock_writer_instance.add_metadata.assert_called_once_with({"/Title": "Test Title", "/Author": "Test Author"})
        mock_page.compress_content_streams.assert_called_once()
        mock_writer_instance.encrypt.assert_called_once_with("secret")
        mock_writer_instance.write.assert_called_once_with("output.pdf")
        mock_writer_instance.close.assert_called_once()

class TestGhostscriptMergeStrategy(unittest.TestCase):
    @patch('app.core.merge_strategies.shutil.which')
    @patch('app.core.merge_strategies.subprocess.run')
    def test_merge_success(self, mock_subprocess_run, mock_which):
        mock_which.return_value = "/usr/bin/gs"  # Simulate Ghostscript found in system
        strategy = GhostscriptMergeStrategy()
        
        result = strategy.merge(["file1.pdf", "file2.pdf"], "output.pdf")
        
        self.assertEqual(result, "output.pdf")
        mock_subprocess_run.assert_called_once()

    @patch('app.core.merge_strategies.shutil.which')
    def test_merge_gs_not_found(self, mock_which):
        mock_which.return_value = None  # Simulate Ghostscript not found
        strategy = GhostscriptMergeStrategy()
        
        with self.assertRaises(RuntimeError) as context:
            strategy.merge(["file1.pdf", "file2.pdf"], "output.pdf")
        
        self.assertIn("Ghostscript not found", str(context.exception))