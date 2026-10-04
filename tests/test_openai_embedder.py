"""Test the REAL embedder: offline with a pretend client, plus one opt-in live check"""
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import pytest

from app.rag import OpenAIEmbedder, DocumentStore

SAMPLE = (Path(__file__).parent.parent / "sample_data" / "login_requirements.md").read_text()


def pretend_client(vectors):
    client = MagicMock()
    client.embeddings.create.return_value = SimpleNamespace(
        data=[SimpleNamespace(embedding=v) for v in vectors]
    )
    return client


def test_embeds_all_texts_in_one_call():
    client = pretend_client([[1.0, 0.0], [0.0, 1.0]])
    OpenAIEmbedder(model="test-model", client=client).embed(["first", "second"])
    client.embeddings.create.assert_called_once_with(model="test-model", input=["first", "second"])


def test_every_vector_is_normalized():
    client = pretend_client([[3.0, 4.0], [0.0, 2.0]])
    out = OpenAIEmbedder(client=client).embed(["a", "b"])
    assert np.allclose(out, [[0.6, 0.8], [0.0, 1.0]])  # [3, 4] has length 5 -> divide by 5


@pytest.mark.skipif(os.getenv("RUN_LIVE_TESTS") != "1", reason="live test: set RUN_LIVE_TESTS=1 (costs a tiny amount)")
def test_live_search_understands_meaning():
    store = DocumentStore(OpenAIEmbedder())
    doc_id, _ = store.add("Login spec", SAMPLE)
    top = store.search(doc_id, "I forgot my password", top_k=1)[0]
    assert top.id == "C2"
    assert "REQ-4" in top.text  # the password reset requirement

    