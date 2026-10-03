"""RAG tests: chunking, retrieval and the document endpoints (no real AI)"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rag import DocumentStore, FakeEmbedder, chunk_text

SAMPLE = (Path(__file__).parent.parent / "sample_data" / "login_requirements.md").read_text()
client = TestClient(app)


def test_chunks_respect_max_size():
    assert all(len(c) <= 300 for c in chunk_text(SAMPLE, max_chars=300))


def test_requirements_are_never_split():
    for chunk in chunk_text(SAMPLE, max_chars=300):
        for line in chunk.split("\n\n"):
            assert line in SAMPLE  # every paragraph survives whole


@pytest.mark.parametrize("text", ["", " ", "\n\n"])
def test_empty_text_gives_no_chunks(text):
    assert chunk_text(text) == []


def test_search_finds_the_right_requirement():
    store = DocumentStore(FakeEmbedder(), max_chars=300)
    doc_id, _ = store.add("spec", SAMPLE)
    top = store.search(doc_id, "account locked after failed login attempts", top_k=1)[0]
    assert "REQ-2" in top.text


def test_upload_and_search_endpoints():
    r = client.post("/documents", json={"title": "Login spec", "text": SAMPLE})
    assert r.status_code == 201
    doc_id = r.json()["doc_id"]
    r = client.post(f"/documents/{doc_id}/search", json={"query": "session timeout", "top_k": 2})
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_unknown_document_returns_404():
    assert client.post("/documents/nope/search", json={"query": "x"}).status_code == 404
    