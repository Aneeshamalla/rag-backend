import re
import io
from sentence_transformers import SentenceTransformer
import pypdf

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    return model.encode(text).tolist()


def extract_text_from_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")


def extract_text_from_pdf(content: bytes) -> str:
    reader = pypdf.PdfReader(io.BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def chunk_fixed(text: str, chunk_size: int = 500) -> list[str]:
    return [
        text[i : i + chunk_size]
        for i in range(0, len(text), chunk_size)
        if text[i : i + chunk_size].strip()
    ]


def chunk_by_sentence(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]
    