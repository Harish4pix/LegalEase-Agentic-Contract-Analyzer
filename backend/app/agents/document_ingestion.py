from io import BytesIO
from pathlib import Path

from docx import Document
from pypdf import PdfReader


class DocumentIngestionAgent:
    """Validates and extracts plain text from one uploaded contract."""

    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

    def extract(self, filename: str, content: bytes) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix not in self.ALLOWED_EXTENSIONS:
            raise ValueError("Only PDF, DOCX, and TXT contracts are supported.")

        if suffix == ".pdf":
            reader = PdfReader(BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif suffix == ".docx":
            document = Document(BytesIO(content))
            text = "\n".join(p.text for p in document.paragraphs)
        else:
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                text = content.decode("latin-1")

        text = self._clean(text)
        if len(text) < 120:
            raise ValueError(
                "The contract contains too little readable text. Scanned PDFs need OCR first."
            )
        return text

    @staticmethod
    def _clean(text: str) -> str:
        lines = [" ".join(line.split()) for line in text.replace("\x00", "").splitlines()]
        return "\n".join(line for line in lines if line).strip()
