import unittest
import os
import tempfile
import shutil
from pypdf import PdfWriter, PdfReader
from app.core.pdf_manager import PDFManager
from app.core.merge_strategies import PyPDFMergeStrategy, GhostscriptMergeStrategy

class TestPDFMergerIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to hold our actual test files
        self.test_dir = tempfile.mkdtemp()
        
        # Define paths for our dummy input PDFs and the expected output PDF
        self.pdf1_path = os.path.join(self.test_dir, "test1.pdf")
        self.pdf2_path = os.path.join(self.test_dir, "test2.pdf")
        self.output_path = os.path.join(self.test_dir, "output.pdf")
        
        # Generate real PDFs (test1.pdf with 1 page, test2.pdf with 2 pages)
        self._create_dummy_pdf(self.pdf1_path, 1)
        self._create_dummy_pdf(self.pdf2_path, 2)

    def tearDown(self):
        # Safely remove the temporary directory and all its contents after testing
        shutil.rmtree(self.test_dir)
        
    def _create_dummy_pdf(self, path, num_pages):
        """Helper method to create an actual PDF file on disk with blank pages."""
        writer = PdfWriter()
        for _ in range(num_pages):
            writer.add_blank_page(width=72, height=72)
        with open(path, "wb") as f:
            writer.write(f)

    def test_pypdf_real_merge(self):
        manager = PDFManager()
        manager.add_files([self.pdf1_path, self.pdf2_path])
        
        strategy = PyPDFMergeStrategy()
        result_path = manager.merge(self.output_path, strategy)
        
        self.assertTrue(os.path.exists(result_path), "Merged PDF file was not created on disk.")
        
        # Read the generated file to ensure the pages were combined (1 + 2 = 3 pages)
        reader = PdfReader(result_path)
        self.assertEqual(len(reader.pages), 3)

    # We skip this test automatically if Ghostscript isn't installed on the testing machine
    @unittest.skipIf(not (shutil.which('gswin64c') or shutil.which('gswin32c') or shutil.which('gs')), "Ghostscript not found on system.")
    def test_ghostscript_real_merge(self):
        manager = PDFManager()
        manager.add_files([self.pdf1_path, self.pdf2_path])
        
        strategy = GhostscriptMergeStrategy()
        result_path = manager.merge(self.output_path, strategy)
        
        self.assertTrue(os.path.exists(result_path), "Ghostscript merged PDF file was not created on disk.")
        
        reader = PdfReader(result_path)
        self.assertEqual(len(reader.pages), 3)