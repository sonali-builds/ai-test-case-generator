"""Test our OpenAI code WITHOUT calling OpenAI: we
give it a pretend client."""
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.generator import FakeGenerator, GenerationError, OpenAIGenerator
from app.models import TestSuite


def pretend_client(suite):
    client = MagicMock()
    client.responses.parse.return_value = SimpleNamespace(output_parsed=suite)
    return client


def test_sends_requirement_inside_tags():
    client = pretend_client(FakeGenerator().generate("x", 3))
    OpenAIGenerator(model="test-model", client=client).generate("Session expires after 30 min")
    sent = client.responses.parse.call_args.kwargs
    assert "<requirement>\nSession expires after 30 min\n</requirement>" in sent["input"]
    assert sent["text_format"] is TestSuite


def test_enforces_max_cases_even_if_ai_returns_more():
    client = pretend_client(FakeGenerator().generate("x", 3))  # AI returns 3
    suite = OpenAIGenerator(client=client).generate("x", max_cases=1)
    assert len(suite.test_cases) == 1


def test_no_usable_output_raises_error():
    with pytest.raises(GenerationError):
        OpenAIGenerator(client=pretend_client(None)).generate("x")