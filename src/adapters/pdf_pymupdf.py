class PyMuPdfParser:
    def extract(self, data: bytes) -> str:
        import pymupdf as fitz
        document = fitz.open(stream=data, filetype="pdf")
        try:
            return "\n\n".join(page.get_text() for page in document).strip()
        finally:
            document.close()
