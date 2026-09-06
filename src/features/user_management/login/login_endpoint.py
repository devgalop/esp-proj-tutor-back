from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from src.features.user_management.login.login_handler import LoginHandler
from src.features.user_management.login.login_request import LoginRequest
from src.features.user_management.login.login_response import LoginResponse
from src.features.user_management.shared.dependencies import get_login_handler

router = APIRouter()


@router.post(
    "/sessions",
    response_model=LoginResponse,
    status_code=200,
    summary="User Login",
    description="Endpoint for user login. Returns a token and its expiration time if the login is successful.",
    tags=["Authentication"],
    responses={
        200: {
            "description": "Login successful. Returns a token and its expiration time.",
            "content": {
                "application/json": {
                    "example": {
                        "is_successful": True,
                        "token": "...token...",  # nosec
                        "expiration_time": 3600,
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Login failed due to invalid credentials.",
            "content": {
                "application/json": {
                    "example": {
                        "is_successful": False,
                        "token": "",  # nosec
                        "expiration_time": 0,
                    }
                }
            },
        },
    },
)
async def login(
    request: LoginRequest,
    handler: Annotated[LoginHandler, Depends(get_login_handler)],
):
    """Endpoint for user login.

    Args:
        request (LoginRequest): The login request containing the user's email and password.
        handler (Annotated[LoginHandler, Depends]): The handler responsible for processing the login.
    Returns:
        LoginResponse: The response indicating whether the login was successful, along with a token and its expiration time if successful.
    """
    response = await handler.handle(request)
    if not response.is_successful:
        raise HTTPException(status_code=401, detail=response.model_dump())
    return response
