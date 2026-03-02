import hashlib
import hmac
import json
import time

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import Settings, get_settings

bearer_scheme = HTTPBearer(auto_error=False)


def _verify_jwt(token: str, secret: str) -> dict:
    """Minimal JWT verification (HS256 only, no external dependency)."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("invalid token")

    import base64

    def _b64decode(s: str) -> bytes:
        s += "=" * (-len(s) % 4)
        return base64.urlsafe_b64decode(s)

    header = json.loads(_b64decode(parts[0]))
    if header.get("alg") != "HS256":
        raise ValueError("unsupported algorithm")

    payload = json.loads(_b64decode(parts[1]))

    # check expiry
    if "exp" in payload and payload["exp"] < time.time():
        raise ValueError("token expired")

    # verify signature
    signing_input = f"{parts[0]}.{parts[1]}".encode()
    expected = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    actual = _b64decode(parts[2])
    if not hmac.compare_digest(expected, actual):
        raise ValueError("invalid signature")

    return payload


async def authenticate(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Authenticate via API Key (X-API-Key header) or JWT Bearer token.

    Returns a dict with at least {"sub": "..."} identifying the caller.
    """
    # 1) API Key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        if not settings.api_keys:
            # no keys configured → allow all (dev mode)
            return {"sub": "dev", "auth": "api_key"}
        if api_key in settings.api_keys:
            return {"sub": f"key:{api_key[:8]}", "auth": "api_key"}
        raise HTTPException(status_code=401, detail="Invalid API key")

    # 2) JWT Bearer
    if credentials and credentials.credentials:
        try:
            payload = _verify_jwt(credentials.credentials, settings.gateway_jwt_secret)
            return {**payload, "auth": "jwt"}
        except ValueError as e:
            raise HTTPException(status_code=401, detail=f"JWT error: {e}")

    # 3) No auth in dev mode (no API keys configured)
    if not settings.api_keys:
        return {"sub": "anonymous", "auth": "none"}

    raise HTTPException(status_code=401, detail="Authentication required")
