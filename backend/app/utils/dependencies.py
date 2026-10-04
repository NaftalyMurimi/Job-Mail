from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import store
from app.utils.auth_utils import decode_access_token

# HTTPBearer (not OAuth2PasswordBearer) gives Swagger a simple
# "paste your token" box instead of a username/password form
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    user_id = decode_access_token(credentials.credentials)
    user = store.get_user_by_id(user_id) if user_id else None

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user