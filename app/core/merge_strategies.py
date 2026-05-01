import subprocess
import shutil
from abc import ABC, abstractmethod
from pypdf import PdfWriter
from app.core.debug import debug_trace

class MergeStrategy(ABC):
    """
    Abstract base class for a PDF merging strategy.
    """
    @abstractmethod
    def merge(self, file_paths, output_path):
        """
        Merges a list of PDF files into a single output file.

        :param file_paths: A list of paths to the PDF files to merge.
        :param output_path: The path to save the merged PDF file.
        """
        pass

class PyPDFMergeStrategy(MergeStrategy):
    """
    Merges PDFs using the pypdf library.
    """
    @debug_trace
    def __init__(self):
        self.password = ""
        self.title = ""
        self.author = ""
        self.lossless_compression = False

    @debug_trace
    def merge(self, file_paths, output_path):
        merger = PdfWriter()
        try:
            for pdf in file_paths:
                merger.append(pdf)
            
            if self.title or self.author:
                metadata = {}
                if self.title:
                    metadata["/Title"] = self.title
                if self.author:
                    metadata["/Author"] = self.author
                merger.add_metadata(metadata)
                
            if self.lossless_compression:
                for page in merger.pages:
                    page.compress_content_streams()

            if self.password:
                merger.encrypt(self.password)
                
            merger.write(output_path)
        finally:
            merger.close()
        return output_path

class GhostscriptMergeStrategy(MergeStrategy):
    """
    Merges PDFs using the Ghostscript command-line tool.
    Note: This requires Ghostscript to be installed and accessible in the system's PATH.
    """
    @debug_trace
    def __init__(self):
        self.pdf_settings = "/default"
        self.compatibility_level = "1.4"
        self.color_conversion = "LeaveColorUnchanged"

    @debug_trace
    def merge(self, file_paths, output_path):
        gs_cmd = shutil.which('gswin64c') or shutil.which('gswin32c') or shutil.which('gs')
        if not gs_cmd:
            raise RuntimeError("Ghostscript not found. Please install Ghostscript and ensure it's in your system's PATH.")

        command = [
            gs_cmd, '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite',
            f'-dPDFSETTINGS={self.pdf_settings}',
            f'-dCompatibilityLevel={self.compatibility_level}',
            f'-sColorConversionStrategy={self.color_conversion}',
            f'-sOutputFile={output_path}'
        ]
        command.extend(file_paths)
        
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except FileNotFoundError:
            raise RuntimeError(f"Ghostscript ('{gs_cmd}') not found. Please ensure it's in your system's PATH.")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr and e.stderr.strip() else (e.stdout.strip() if e.stdout else "Unknown Error")
            raise RuntimeError(f"Ghostscript failed to merge PDFs. Error: {error_msg}")
        except OSError as e:
            raise RuntimeError(f"Failed to execute Ghostscript ('{gs_cmd}'). It might be an incompatible version (e.g., WSL binary on Windows). Error: {e}")
        
        return output_path

# Note on Tesseract:
# Tesseract is an Optical Character Recognition (OCR) engine. Its primary function is to
# extract text from images, including images within PDF files. It is not designed for
# merging, combining, or manipulating the structure of PDF documents themselves.
# Therefore, it is not included as a merge strategy.