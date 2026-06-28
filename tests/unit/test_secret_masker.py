from shared.ai.secret_masker import mask_secrets


def test_mask_secrets_redacts_api_key():
    text = "api_key=super-secret-key-12345678"
    masked = mask_secrets(text)
    assert "super-secret-key" not in masked
    assert "***REDACTED***" in masked


def test_mask_secrets_redacts_bearer_token():
    text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    masked = mask_secrets(text)
    assert "eyJhbGci" not in masked
    assert "Bearer ***REDACTED***" in masked
