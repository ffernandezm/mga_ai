import fitz  # PyMuPDF

class Document:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_text(self):
        with fitz.open(self.file_path) as doc:
            return "\n".join([page.get_text() for page in doc])
