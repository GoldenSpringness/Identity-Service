from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Dict, Any, Optional

from app.core.config import settings, load_private_key, load_public_key

#region General
ALGORITHM = "RS256"

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)
#endregion

#region Password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
#endregion

#region JWT
def _create_token(
    subject: str,
    expires_delta: timedelta,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    jti = str(uuid4())

    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": jti,
    }

    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(
        payload,
        load_private_key(),
        algorithm=ALGORITHM,
    )

def create_access_token(
    user_id: str,
    roles: list[str],
    session_id: str,
    correlation_id: str,
) -> str:

    return _create_token(
        subject=user_id,
        expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ),
        additional_claims={
            "roles": roles,
            "session_id": session_id,
            "type": "access",
            "cid": correlation_id,
        },
    )

def create_refresh_token(
    user_id: str,
    session_id: str,
) -> str:

    return _create_token(
        subject=user_id,
        expires_delta=timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
        additional_claims={
            "session_id": session_id,
            "type": "refresh",
        },
    )


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(
            token,
            load_public_key(),
            algorithms=[ALGORITHM],
        )
    except JWTError:
        raise ValueError("Invalid token")

def validate_token_type(payload: dict, expected_type: str):
    if payload.get("type") != expected_type:
        raise ValueError("Invalid token type")
#endregion