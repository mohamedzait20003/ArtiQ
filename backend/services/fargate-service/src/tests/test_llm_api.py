import sys
import types
import pytest

from ece461.API import llm_api


class _FakeBody:
    def __init__(self, b: bytes):
        self._b = b

    def read(self):
        return self._b


class _FakeClient:
    def __init__(self, ret: bytes | None = None, exc: Exception | None = None):
        self._ret = ret
        self._exc = exc

    def invoke_model(self, modelId=None, body=None, contentType=None):
        if self._exc:
            raise self._exc
        return {"body": _FakeBody(self._ret or b"")}


def test_query_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure BEDROCK_MODEL_ID present and boto3 client returns simple bytes
    monkeypatch.setenv("BEDROCK_MODEL_ID", "test-model")
    client = _FakeClient(ret=b"hello")
    fake_boto3 = types.SimpleNamespace(client=lambda *a, **k: client)
    monkeypatch.setitem(sys.modules, "boto3", fake_boto3)

    response = llm_api.query_llm("What is the best software engineering tool?")
    assert isinstance(response, str)
    assert len(response) > 0


def test_llm_api_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    # BEDROCK_MODEL_ID not set -> ValueError
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)
    with pytest.raises(ValueError):
        llm_api.query_llm("hi")


def test_llm_api_non_200(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate boto3 client raising an exception
    monkeypatch.setenv("BEDROCK_MODEL_ID", "x")
    client = _FakeClient(exc=Exception("invoke_model failed"))
    fake_boto3 = types.SimpleNamespace(client=lambda *a, **k: client)
    monkeypatch.setitem(sys.modules, "boto3", fake_boto3)

    with pytest.raises(Exception):
        llm_api.query_llm("hi")


def test_llm_api_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    # Return JSON body with an "output" key containing a JSON string
    monkeypatch.setenv("BEDROCK_MODEL_ID", "x")
    client = _FakeClient(ret=b'{"output":"{\\"k\\":1}"}')
    fake_boto3 = types.SimpleNamespace(client=lambda *a, **k: client)
    monkeypatch.setitem(sys.modules, "boto3", fake_boto3)

    out = llm_api.query_llm("prompt")
    assert out == "{\"k\":1}"
