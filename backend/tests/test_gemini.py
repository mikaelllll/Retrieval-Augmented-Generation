from app.services.gemini import provider_error


def test_provider_error_explains_invalid_key() -> None:
    error = ValueError("400 INVALID_ARGUMENT: API_KEY_INVALID. API key not valid")
    assert "rejected this API key" in provider_error(error)


def test_provider_error_explains_quota() -> None:
    error = ValueError("429 RESOURCE_EXHAUSTED")
    assert "quota is exhausted" in provider_error(error)


def test_provider_error_redacts_key_from_unknown_errors() -> None:
    error = ValueError(f"Provider failed for {'AIza' + 'x' * 35}")
    message = provider_error(error)
    assert "AIza" not in message
    assert "[REDACTED]" in message
