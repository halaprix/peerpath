from __future__ import annotations

import re

_SECRET_ASSIGNMENT_PATTERNS = (
    re.compile(r"(?im)^(\s*PrivateKey\s*=\s*).+$"),
    re.compile(r"(?im)^(\s*PresharedKey\s*=\s*).+$"),
)

_PEM_PRIVATE_BLOCK = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
    re.DOTALL,
)
_HOME_PATH = re.compile(r"/home/[^/\s]+/")
_USERS_PATH = re.compile(r"/Users/[^/\s]+/")
_LONG_CONTAINER_ID = re.compile(r"\b[0-9a-f]{13,64}\b")


def redact_text(text: str) -> str:
    redacted = text
    for pattern in _SECRET_ASSIGNMENT_PATTERNS:
        redacted = pattern.sub(r"\1<redacted>", redacted)
    redacted = _PEM_PRIVATE_BLOCK.sub("<redacted private key block>", redacted)
    redacted = _HOME_PATH.sub("/home/<user>/", redacted)
    redacted = _USERS_PATH.sub("/Users/<user>/", redacted)
    redacted = _LONG_CONTAINER_ID.sub("<container-id>", redacted)
    return redacted
