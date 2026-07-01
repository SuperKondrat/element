from fastapi import APIRouter, Depends

from app.auth.jwt import create_access_token
from app.config import Settings, get_settings
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, settings: Settings = Depends(get_settings)) -> TokenResponse:
    subject = auth_service.authenticate(settings, data.username, data.password)
    token = create_access_token(settings, subject)
    return TokenResponse(access_token=token)
