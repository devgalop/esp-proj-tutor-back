from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Annotated

from src.features.user_management.refresh_token.refresh_token_handler import (
    RefreshTokenHandler,
)
from src.features.user_management.refresh_token.refresh_token_request import (
    RefreshTokenRequest,
)
from src.features.user_management.refresh_token.refresh_token_response import (
    RefreshTokenResponse,
)
from src.features.user_management.shared.dependencies import (
    get_refresh_token_handler,
    get_token_generator,
)
from src.features.user_management.shared.token_generator import TokenGenerator

router = APIRouter()

security = HTTPBearer()


@router.post(
    "/sessions/refresh",
    status_code=200,
    summary="Refresh Session",
    description="Endpoint for refreshing an access token using a valid refresh token. Returns new access and refresh tokens if successful.",
    tags=["Authentication"],
    responses={
        200: {
            "description": "Refresh successful. Returns new access and refresh tokens.",
            "content": {
                "application/json": {
                    "example": {
                        "is_successful": True,
                        "access_token": "...new access token...",  # nosec
                        "refresh_token": "...new refresh token...",  # nosec
                        "expiration_time": 1800,
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Refresh token is invalid or expired.",
            "content": {
                "application/json": {
                    "example": {
                        "is_successful": False,
                        "access_token": None,  # nosec
                        "refresh_token": None,  # nosec
                        "expiration_time": None,  # nosec
                    }
                }
            },
        },
        403: {
            "description": "Forbidden. Refresh token has been revoked.",
            "content": {
                "application/json": {"example": {"detail": "Refresh token revoked"}}
            },
        },
        500: {
            "description": "Internal Server Error. Token generation failed.",
            "content": {
                "application/json": {"example": {"detail": "Token generation failed"}}
            },
        },
    },
)
async def refresh_session(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    token_generator: Annotated[TokenGenerator, Depends(get_token_generator)],
    request_http: Request,
    response_http: Response,
    handler: Annotated[RefreshTokenHandler, Depends(get_refresh_token_handler)],
) -> RefreshTokenResponse:
    """Endpoint for refreshing an access token.

    Args:
        credentials (HTTPAuthorizationCredentials): The Bearer token from the Authorization header.
        handler (RefreshTokenHandler): The handler responsible for processing the refresh.
        request_http (Request): The incoming HTTP request, used to access cookies.
        response_http (Response): The HTTP response, used to set new cookies.
        token_generator (TokenGenerator): The token generator for creating new tokens.

    Returns:
        RefreshTokenResponse: The response with new access and refresh tokens if successful.
    """
    refresh_token_cookie = request_http.cookies.get("refresh_token")
    if not refresh_token_cookie:
        raise HTTPException(status_code=401, detail="Refresh token cookie missing")
    token_info = token_generator.validate_token(
        credentials.credentials, verify_exp=False
    )
    if not token_info:
        raise HTTPException(status_code=401, detail="Invalid access token")

    refresh_token_request = RefreshTokenRequest(
        user_id=token_info.user_id,
        user_name=token_info.user_name,
        refresh_token=refresh_token_cookie,
    )
    response = await handler.handle(refresh_token_request)
    if not response.is_successful:
        raise HTTPException(status_code=401, detail=response.model_dump())

    if (
        not response.access_token
        or not response.refresh_token
        or not response.expiration_time
    ):
        raise HTTPException(status_code=500, detail="Token generation failed")

    response_http.set_cookie(
        key="refresh_token", value=response.refresh_token, httponly=True, secure=True
    )
    response_http.set_cookie(
        key="access_token", value=response.access_token, httponly=True, secure=True
    )
    return response
