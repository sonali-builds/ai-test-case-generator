"""Retrieval: split a document into chunks, embed them, find the ones that match a query."""
import os
import re
import uuid
import zlib
from functools import lru_cache
from typing import Protocol

import numpy as np

from .models import RetrievedChunk


# ------------ 1. Chunking ---------------

def chunk_text(text: str, max_chars: int = 800) -> list[str]:
    """Paragraph-aware chunking: keep each requirement whole, pack paragraphs up to max_chars"""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current = [], ""
    for p in paragraphs:
        if current and len(current) + 2 + len(p) > max_chars:
            chunks.append(current)
            current = p
        else:
            current = f"{current}\n\n{p}".strip()

    if current:
        chunks.append(current)
    return chunks


# ------------- 2. Embedding: text -> vector of numbers ----------

class Embedder(Protocol):
    def embed(self, texts: list[str]) -> np.ndarray: ...


def _normalize(m: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    return m / np.where(norms == 0, 1, norms)


class FakeEmbedder:
    """Free and offline: counts shared words (keyword-like, not true meaning.)"""
    DIMS = 512

    def embed(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.DIMS), dtype=np.float32)
        for row, text in enumerate(texts):
            for word in re.findall(r"[a-z0-9]+", text.lower()):
                out[row, zlib.crc32(word.encode()) % self.DIMS] += 1.0
        return _normalize(out)


class OpenAIEmbedder:
    """Real embeddings: similar meaning -> similar vectors."""


    def __init__(self, model: str | None = None, client=None):
        self.model = model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        if client is None:
            from openai import OpenAI
            client = OpenAI(max_retries=3, timeout=60)
        self.client = client


    def embed(self, texts: list[str]) -> np.ndarray:
        resp = self.client.embeddings.create(model=self.model, input=texts)
        return _normalize(np.array([d.embedding for d in resp.data], dtype=np.float32))


# ---------- 3. Store + search --------------

class DocumentStore:
    """Keeps documents in memory (lost on restart; fine for learning)."""

    def __init__(self, embedder: Embedder, max_chars: int = 800):
        self.embedder = embedder
        self.max_chars = max_chars
        self._docs: dict[str, dict] = {}

    def add(self, title: str, text: str) -> tuple[str, int]:
        chunks = chunk_text(text, self.max_chars)
        if not chunks:
            raise ValueError("The document has no text")
        doc_id = uuid.uuid4().hex[:8]
        self._docs[doc_id] = {"title": title, "chunks": chunks, "vectors": self.embedder.embed(chunks)}
        return doc_id,len(chunks)

    def has(self, doc_id: str) -> bool:
        return doc_id in self._docs

    def search(self, doc_id: str, query: str, top_k: int =3) -> list[RetrievedChunk]:
        doc = self._docs[doc_id]
        q = self.embedder.embed([query])[0]
        scores = doc["vectors"] @ q # dot product of normalized vectors = cosine similarity
        best = np.argsort(scores)[::-1][:top_k]
        return [RetrievedChunk(id=f"C{i + 1}", text=doc["chunks"][i], score=round(float(scores[i]), 3))
                for i in best]


@lru_cache
def get_store() -> DocumentStore:
    embedder = OpenAIEmbedder() if os.getenv("OPENAI_API_KEY") else FakeEmbedder()
    return DocumentStore(embedder)