import hashlib
import re

SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?[\w-]{8,}"), r"\1=***REDACTED***"),
    (re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?[^\s'\"]{4,}"), r"\1=***REDACTED***"),
    (re.compile(r"(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*"), "Bearer ***REDACTED***"),
    (re.compile(r"(?i)(token|secret)\s*[:=]\s*['\"]?[\w-]{8,}"), r"\1=***REDACTED***"),
    (re.compile(r"postgresql://[^\s]+"), "postgresql://***REDACTED***"),
    (re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+ PRIVATE KEY-----"), "***REDACTED_KEY***"),
]


def mask_secrets(text: str) -> str:
    if not text:
        return text
    masked = text
    for pattern, replacement in SECRET_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked
