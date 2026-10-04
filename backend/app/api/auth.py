from fastapi import APIRouter, Depends, HTTPException, status

from app import store
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.utils.auth_utils import create_access_token, hash_password, verify_password
from app.utils.dependencies import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(data: SignupRequest):
    if store.get_user_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = store.create_user(data.email, hash_password(data.password), data.full_name)
    logger.info(f"New user signed up: {user['email']}")
    # response_model strips hashed_password from the output automatically
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = store.get_user_by_email(data.email)

    # Same message for "no such user" and "wrong password" so attackers
    # can't tell which emails are registered
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    logger.info(f"User logged in: {user['email']}")
    return TokenResponse(access_token=create_access_token(user["id"]))


@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    # JWTs are stateless: the server can't "delete" one. Logging out means the
    # frontend discards the token. This endpoint just confirms the token was valid.
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)):
    return current_user