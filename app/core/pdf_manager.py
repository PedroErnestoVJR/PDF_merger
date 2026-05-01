from pypdf import PdfWriter
from app.core.debug import debug_trace

class PDFManager:
    @debug_trace
    def __init__(self):
        self.files = []

    @debug_trace
    def add_files(self, file_paths):
        for path in file_paths:
            if path not in self.files:
                self.files.append(path)

    @debug_trace
    def remove_file(self, file_path):
        if file_path in self.files:
            self.files.remove(file_path)

    @debug_trace
    def move_up(self, index):
        if index > 0:
            self.files[index - 1], self.files[index] = self.files[index], self.files[index - 1]

    @debug_trace
    def move_down(self, index):
        if index < len(self.files) - 1:
            self.files[index + 1], self.files[index] = self.files[index], self.files[index + 1]

    @debug_trace
    def get_files(self):
        return self.files

    @debug_trace
    def merge(self, output_path, strategy):
        """
        Merges the queued files using a provided strategy.
        :param output_path: The path for the output file.
        :param strategy: An instance of a class that implements the MergeStrategy interface.
        """
        if not self.files:
            raise ValueError("No files queued for merging.")
        return strategy.merge(self.files, output_path)