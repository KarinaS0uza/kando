"""Unit tests for ai_core.llm: error classification, logging, and key fallback."""

# The active_prompt fixture below is intentionally reused as a test argument
# name, matching pytest's fixture-injection convention already used in
# conftest.py.
# pylint: disable=redefined-outer-name

import json
from unittest.mock import MagicMock

import httpx
import pytest
from groq import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)

from . import llm
from .models import Prompt, PromptCallMetadata


def make_groq_error(error_cls, status_code, message="groq error", headers=None):
    """Build a real Groq SDK exception instance with a minimal httpx response."""
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    response = httpx.Response(status_code=status_code, request=request, headers=headers or {})
    return error_cls(message, response=response, body=None)


def make_fake_client(side_effect):
    """Return a MagicMock standing in for a Groq client, with the given create() behavior."""
    client = MagicMock()
    client.chat.completions.create.side_effect = side_effect
    return client


def make_success_response(content='{"ok": true}'):
    """Return a MagicMock shaped like a successful chat.completions.create() response."""
    response = MagicMock()
    response.choices[0].message.content = content
    response.usage.prompt_tokens = 10
    response.usage.completion_tokens = 5
    response.usage.total_tokens = 15
    return response


@pytest.fixture
def active_prompt(db):  # pylint: disable=unused-argument
    """Return an active Prompt usable as the run_prompt() target."""
    return Prompt.objects.create(prompt_description="test_prompt", prompt_detail="hello $name")


class TestRunPromptErrorClassification:
    """run_prompt must raise the right exception and log the matching status."""

    @pytest.mark.django_db
    def test_missing_prompt_raises_and_logs(self):
        """An unknown prompt_key raises Prompt.DoesNotExist and logs PROMPT_MISSING."""
        with pytest.raises(Prompt.DoesNotExist):
            llm.run_prompt("does_not_exist", {})

        call = PromptCallMetadata.objects.get()
        assert call.status == PromptCallMetadata.Status.PROMPT_MISSING
        assert call.prompt_description == "does_not_exist"

    @pytest.mark.django_db
    def test_invalid_json_raises_and_logs(self, active_prompt, monkeypatch):
        """A non-JSON completion raises JSONDecodeError and logs INVALID_JSON."""
        monkeypatch.setattr(
            llm, "clients", [make_fake_client([make_success_response("not json")])]
        )

        with pytest.raises(json.JSONDecodeError):
            llm.run_prompt(active_prompt.prompt_description, {"name": "x"})

        call = PromptCallMetadata.objects.get()
        assert call.status == PromptCallMetadata.Status.INVALID_JSON
        assert call.output_text == "not json"

    @pytest.mark.django_db
    def test_rate_limit_raises_and_logs(self, active_prompt, monkeypatch):
        """A RateLimitError still failing on the wait-and-retry attempt raises and logs RATE_LIMITED."""
        exc = make_groq_error(RateLimitError, 429)
        monkeypatch.setattr(llm.time, "sleep", lambda seconds: None)
        monkeypatch.setattr(llm, "clients", [make_fake_client([exc, exc])])

        with pytest.raises(RateLimitError):
            llm.run_prompt(active_prompt.prompt_description, {"name": "x"})

        call = PromptCallMetadata.objects.get()
        assert call.status == PromptCallMetadata.Status.RATE_LIMITED
        assert call.error_message == str(exc)

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "error_cls,status_code",
        [
            (AuthenticationError, 401),
            (PermissionDeniedError, 403),
            (BadRequestError, 400),
            (NotFoundError, 404),
        ],
    )
    def test_config_errors_raise_and_log(self, active_prompt, monkeypatch, error_cls, status_code):
        """Auth/permission/bad-request/not-found errors raise and log CONFIG_ERROR."""
        exc = make_groq_error(error_cls, status_code)
        monkeypatch.setattr(llm, "clients", [make_fake_client([exc])])

        with pytest.raises(error_cls):
            llm.run_prompt(active_prompt.prompt_description, {"name": "x"})

        call = PromptCallMetadata.objects.get()
        assert call.status == PromptCallMetadata.Status.CONFIG_ERROR

    @pytest.mark.django_db
    def test_generic_error_raises_and_logs(self, active_prompt, monkeypatch):
        """Any other exception raises as-is and logs API_ERROR."""
        monkeypatch.setattr(
            llm, "clients", [make_fake_client([ConnectionError("boom")])]
        )

        with pytest.raises(ConnectionError):
            llm.run_prompt(active_prompt.prompt_description, {"name": "x"})

        call = PromptCallMetadata.objects.get()
        assert call.status == PromptCallMetadata.Status.API_ERROR
        assert call.error_message == "boom"

    @pytest.mark.django_db
    def test_success_logs_and_returns_parsed_json(self, active_prompt, monkeypatch):
        """A successful call returns the parsed JSON and logs SUCCESS with token usage."""
        monkeypatch.setattr(
            llm, "clients", [make_fake_client([make_success_response('{"ok": true}')])]
        )

        result = llm.run_prompt(active_prompt.prompt_description, {"name": "x"})

        assert result == {"ok": True}
        call = PromptCallMetadata.objects.get()
        assert call.status == PromptCallMetadata.Status.SUCCESS
        assert call.prompt_tokens == 10
        assert call.completion_tokens == 5


class TestRunPromptSafe:
    """run_prompt_safe must degrade every failure to an {error, retryable} dict."""

    @pytest.mark.django_db
    def test_missing_prompt_is_not_retryable(self):
        """A missing prompt returns the caller-supplied message, not retryable."""
        result = llm.run_prompt_safe(
            "does_not_exist", {}, missing_prompt_message="Prompt não configurado."
        )

        assert result == {"error": "Prompt não configurado.", "retryable": False}

    @pytest.mark.django_db
    def test_invalid_json_is_retryable(self, active_prompt, monkeypatch):
        """Invalid JSON from the LLM is reported as retryable."""
        monkeypatch.setattr(
            llm, "clients", [make_fake_client([make_success_response("not json")])]
        )

        result = llm.run_prompt_safe(
            active_prompt.prompt_description, {"name": "x"}, missing_prompt_message="x"
        )

        assert result["retryable"] is True
        assert "JSON" in result["error"]

    @pytest.mark.django_db
    def test_rate_limit_is_retryable(self, active_prompt, monkeypatch):
        """A rate limit still failing after the wait-and-retry is reported as retryable with a user-facing PT-BR message."""
        exc = make_groq_error(RateLimitError, 429)
        monkeypatch.setattr(llm.time, "sleep", lambda seconds: None)
        monkeypatch.setattr(llm, "clients", [make_fake_client([exc, exc])])

        result = llm.run_prompt_safe(
            active_prompt.prompt_description, {"name": "x"}, missing_prompt_message="x"
        )

        assert result == {
            "error": "Você atingiu o limite de uso. Tente novamente mais tarde.",
            "retryable": True,
        }

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "error_cls,status_code", [(AuthenticationError, 401), (BadRequestError, 400)]
    )
    def test_config_error_is_not_retryable(
        self, active_prompt, monkeypatch, error_cls, status_code
    ):
        """Config errors (auth/bad request/etc.) are reported as not retryable."""
        exc = make_groq_error(error_cls, status_code)
        monkeypatch.setattr(llm, "clients", [make_fake_client([exc])])

        result = llm.run_prompt_safe(
            active_prompt.prompt_description, {"name": "x"}, missing_prompt_message="x"
        )

        assert result["retryable"] is False
        assert "Falha de configuração" in result["error"]

    @pytest.mark.django_db
    def test_generic_error_is_retryable(self, active_prompt, monkeypatch):
        """Any other exception falls back to a generic retryable error."""
        monkeypatch.setattr(
            llm, "clients", [make_fake_client([ConnectionError("boom")])]
        )

        result = llm.run_prompt_safe(
            active_prompt.prompt_description, {"name": "x"}, missing_prompt_message="x"
        )

        assert result == {"error": "Falha ao chamar o LLM.", "retryable": True}


class TestMultiKeyFallback:
    """create_completion must fail over across keys only for key-specific errors."""

    @pytest.mark.django_db
    def test_retries_same_key_once_after_rate_limit_then_succeeds(self, active_prompt, monkeypatch):
        """A rate limit is retried on the same key and, if that retry
        succeeds, the call completes normally without moving to another key."""
        exc = make_groq_error(RateLimitError, 429)
        client = make_fake_client([exc, make_success_response('{"ok": true}')])
        monkeypatch.setattr(llm.time, "sleep", lambda seconds: None)
        monkeypatch.setattr(llm, "clients", [client])

        result = llm.run_prompt(active_prompt.prompt_description, {"name": "x"})

        assert result == {"ok": True}
        assert client.chat.completions.create.call_count == 2
        call = PromptCallMetadata.objects.get()
        assert call.status == PromptCallMetadata.Status.SUCCESS

    @pytest.mark.django_db
    def test_falls_back_to_next_key_on_rate_limit(self, active_prompt, monkeypatch):
        """A first key rate-limited on both its attempt and its retry falls back to a working second key."""
        exc = make_groq_error(RateLimitError, 429)
        failing_client = make_fake_client([exc, exc])
        working_client = make_fake_client([make_success_response('{"ok": true}')])
        monkeypatch.setattr(llm.time, "sleep", lambda seconds: None)
        monkeypatch.setattr(llm, "clients", [failing_client, working_client])

        result = llm.run_prompt(active_prompt.prompt_description, {"name": "x"})

        assert result == {"ok": True}
        assert failing_client.chat.completions.create.call_count == 2
        working_client.chat.completions.create.assert_called_once()
        call = PromptCallMetadata.objects.get()
        assert call.status == PromptCallMetadata.Status.SUCCESS

    @pytest.mark.django_db
    def test_falls_back_to_next_key_on_auth_error(self, active_prompt, monkeypatch):
        """An unauthorized first key falls back to a working second key."""
        failing_client = make_fake_client([make_groq_error(AuthenticationError, 401)])
        working_client = make_fake_client([make_success_response('{"ok": true}')])
        monkeypatch.setattr(llm, "clients", [failing_client, working_client])

        result = llm.run_prompt(active_prompt.prompt_description, {"name": "x"})

        assert result == {"ok": True}

    @pytest.mark.django_db
    def test_raises_last_error_when_all_keys_exhausted(self, active_prompt, monkeypatch):
        """When every key fails on both its attempt and its retry, the last key's error is the one raised and logged."""
        first_exc = make_groq_error(RateLimitError, 429, message="first key limited")
        second_exc = make_groq_error(RateLimitError, 429, message="second key limited")
        client_a = make_fake_client([first_exc, first_exc])
        client_b = make_fake_client([second_exc, second_exc])
        monkeypatch.setattr(llm.time, "sleep", lambda seconds: None)
        monkeypatch.setattr(llm, "clients", [client_a, client_b])

        with pytest.raises(RateLimitError) as excinfo:
            llm.run_prompt(active_prompt.prompt_description, {"name": "x"})

        assert str(excinfo.value) == "second key limited"
        call = PromptCallMetadata.objects.get()
        assert call.status == PromptCallMetadata.Status.RATE_LIMITED
        assert call.error_message == "second key limited"

    @pytest.mark.django_db
    def test_does_not_fall_back_on_bad_request(self, active_prompt, monkeypatch):
        """A malformed request fails the same way on every key, so no point retrying."""
        failing_client = make_fake_client([make_groq_error(BadRequestError, 400)])
        untouched_client = make_fake_client([make_success_response('{"ok": true}')])
        monkeypatch.setattr(llm, "clients", [failing_client, untouched_client])

        with pytest.raises(BadRequestError):
            llm.run_prompt(active_prompt.prompt_description, {"name": "x"})

        untouched_client.chat.completions.create.assert_not_called()


class TestRateLimitWaitSeconds:
    """rate_limit_wait_seconds must read the retry-after header, fall back to
    the message text, then a fixed default -- always capped at the maximum.
    """

    def test_reads_retry_after_header(self):
        """The retry-after response header takes precedence when present."""
        exc = make_groq_error(RateLimitError, 429, headers={"retry-after": "3.5"})

        assert llm.rate_limit_wait_seconds(exc) == 3.5

    def test_parses_wait_from_message_when_header_missing(self):
        """Without a header, the wait is parsed from Groq's message text."""
        exc = make_groq_error(
            RateLimitError, 429, message="rate limited, please try again in 2.085s"
        )

        assert llm.rate_limit_wait_seconds(exc) == 2.085

    def test_falls_back_to_default_when_nothing_available(self):
        """With neither a header nor a parseable message, use the fixed default."""
        exc = make_groq_error(RateLimitError, 429, message="rate limited")

        assert llm.rate_limit_wait_seconds(exc) == llm.RATE_LIMIT_DEFAULT_WAIT_SECONDS

    def test_caps_wait_at_maximum(self):
        """A very long indicated wait is capped so a single call can't hang the request."""
        exc = make_groq_error(RateLimitError, 429, headers={"retry-after": "999"})

        assert llm.rate_limit_wait_seconds(exc) == llm.RATE_LIMIT_MAX_WAIT_SECONDS


class TestLoadApiKeys:
    """load_api_keys must parse GROQ_API_KEYS with a GROQ_API_KEY fallback."""

    def test_parses_comma_separated_keys(self, monkeypatch):
        """GROQ_API_KEYS is split into an ordered list of keys."""
        monkeypatch.setenv("GROQ_API_KEYS", "key1,key2,key3")

        assert llm.load_api_keys() == ["key1", "key2", "key3"]

    def test_strips_whitespace_and_drops_empty_entries(self, monkeypatch):
        """Whitespace around keys and empty comma-separated entries are dropped."""
        monkeypatch.setenv("GROQ_API_KEYS", " key1 ,, key2,")

        assert llm.load_api_keys() == ["key1", "key2"]

    def test_falls_back_to_single_key_when_groq_api_keys_unset(self, monkeypatch):
        """Without GROQ_API_KEYS, the single GROQ_API_KEY is used."""
        monkeypatch.delenv("GROQ_API_KEYS", raising=False)
        monkeypatch.setenv("GROQ_API_KEY", "single-key")

        assert llm.load_api_keys() == ["single-key"]

    def test_returns_none_entry_when_nothing_configured(self, monkeypatch):
        """With neither env var set, a single None entry preserves the old behavior."""
        monkeypatch.delenv("GROQ_API_KEYS", raising=False)
        monkeypatch.delenv("GROQ_API_KEY", raising=False)

        assert llm.load_api_keys() == [None]
