import json
from types import SimpleNamespace

import pytest

from pipeline import AnalysisError, analyze_inquiry
from tests.sample_brief import SAMPLE_BRIEF, SAMPLE_INPUT


class FakeClient:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        reply = self.replies[min(self.calls, len(self.replies) - 1)]
        self.calls += 1
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=reply))])


def test_happy_path_with_code_fences():
    client = FakeClient(["```json\n" + json.dumps(SAMPLE_BRIEF) + "\n```"])
    brief = analyze_inquiry(SAMPLE_INPUT, client=client, model="x")
    assert brief.suggested_approach.startswith("LLM + RAG")
    assert client.calls == 1


def test_retry_recovers_from_bad_json():
    client = FakeClient(["not json", json.dumps(SAMPLE_BRIEF)])
    assert analyze_inquiry(SAMPLE_INPUT, client=client, model="x").confidence.value == "Medium"
    assert client.calls == 2


def test_gives_up_after_retries():
    client = FakeClient(["nope"])
    with pytest.raises(AnalysisError):
        analyze_inquiry(SAMPLE_INPUT, client=client, model="x")
    assert client.calls == 2


def test_empty_input_never_calls_llm():
    client = FakeClient([json.dumps(SAMPLE_BRIEF)])
    with pytest.raises(AnalysisError):
        analyze_inquiry("   ", client=client, model="x")
    assert client.calls == 0
