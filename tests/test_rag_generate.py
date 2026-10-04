"""Grounded generation: every test must point to what was retrieved."""
import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.generator import build_input
from app.main import app
from app.models import RetrievedChunk

SAMPLE = (Path(__file__).parent.parent / "sample_data" / "login_requirements.md").read_text()

client =TestClient(app)


def upload():
    return client.post("/documents", json={"title": "Login spec", "text": SAMPLE}).json()["doc_id"]


def test_generate_from_document_cites_only_retrieved_chunks():
    r = client.post(f"/documents/{upload()}/generate", json={"focus": "account lockout", "top_k": 2})
    assert r.status_code == 200
    body = r.json()
    retrieved_ids = {c["id"] for c in body["retrieved"]}
    for tc in body["test_cases"]:
        assert set(tc["sources"]) <= retrieved_ids


def test_requirement_ids_exist_in_the_retrieved_text():
    body = client.post(f"/documents/{upload()}/generate", json={"focus": "account lockout"}).json()
    retrieved_text = " ".join(c["text"] for c in body["retrieved"])
    for tc in body["test_cases"]:
        for req_id in tc["requirement_ids"]:
            assert re.search(rf"\b{req_id}\b", retrieved_text)  # never an invented REQ-99


def test_plain_generate_has_no_citations():
    tc = client.post("/generate", json={"requirement": "Login"}).json()["test_cases"][0]
    assert tc["sources"] == [] and tc["requirement_ids"] == []


def test_prompt_wraps_context_and_focus_in_tags():
    ctx = [RetrievedChunk(id="C2", text="REQ-2 Lockout after 5 tries.", score=0.9)]
    prompt = build_input("account lockout", 3, ctx)
    assert '<chunk id="C2">' in prompt and "<focus>\naccount lockout\n</focus>" in prompt