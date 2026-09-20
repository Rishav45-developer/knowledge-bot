from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.security.jwt import verify_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="http://127.0.0.1:8000/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload


def require_admin(
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user