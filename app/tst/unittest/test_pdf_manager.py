import unittest
from unittest.mock import MagicMock
from app.core.pdf_manager import PDFManager

class TestPDFManager(unittest.TestCase):
    def setUp(self):
        self.manager = PDFManager()

    def test_add_files(self):
        # Test adding new files
        self.manager.add_files(["file1.pdf", "file2.pdf"])
        self.assertEqual(self.manager.get_files(), ["file1.pdf", "file2.pdf"])
        
        # Test avoiding duplicates
        self.manager.add_files(["file1.pdf", "file3.pdf"])
        self.assertEqual(self.manager.get_files(), ["file1.pdf", "file2.pdf", "file3.pdf"])

    def test_remove_file(self):
        self.manager.add_files(["file1.pdf", "file2.pdf"])
        self.manager.remove_file("file1.pdf")
        self.assertEqual(self.manager.get_files(), ["file2.pdf"])

    def test_move_up(self):
        self.manager.add_files(["file1.pdf", "file2.pdf", "file3.pdf"])
        self.manager.move_up(1)  # Move file2.pdf up
        self.assertEqual(self.manager.get_files(), ["file2.pdf", "file1.pdf", "file3.pdf"])

    def test_move_down(self):
        self.manager.add_files(["file1.pdf", "file2.pdf", "file3.pdf"])
        self.manager.move_down(0)  # Move file1.pdf down
        self.assertEqual(self.manager.get_files(), ["file2.pdf", "file1.pdf", "file3.pdf"])

    def test_merge_empty(self):
        strategy_mock = MagicMock()
        with self.assertRaises(ValueError) as context:
            self.manager.merge("output.pdf", strategy_mock)
        self.assertEqual(str(context.exception), "No files queued for merging.")

    def test_merge_success(self):
        self.manager.add_files(["file1.pdf", "file2.pdf"])
        strategy_mock = MagicMock()
        strategy_mock.merge.return_value = "output.pdf"
        
        result = self.manager.merge("output.pdf", strategy_mock)
        self.assertEqual(result, "output.pdf")
        strategy_mock.merge.assert_called_once_with(["file1.pdf", "file2.pdf"], "output.pdf")