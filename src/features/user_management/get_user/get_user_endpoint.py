from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from src.features.user_management.get_user.get_user_handler import GetUserHandler
from src.features.user_management.get_user.get_user_request import GetUserRequest
from src.features.user_management.get_user.get_user_response import GetUserResponse
from src.features.user_management.shared.dependencies import get_get_user_handler
from src.features.user_management.shared.require_roles import require_roles
from src.features.user_management.shared.token_generator import TokenData
from src.features.user_management.shared.validate_user import UserIdentityValidator

router = APIRouter()


@router.get(
    "/{user_id}",
    status_code=200,
    summary="Get User",
    description="Endpoint for retrieving user information by user ID. Returns the user details if found, otherwise returns a message indicating that the user was not found.",
    tags=["User Management"],
    responses={
        200: {
            "description": "User found. Returns the user details.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": True,
                        "message": "User found",
                        "user": {
                            "user_id": "12345",
                            "username": "john_doe",
                            "email": "john_doe@example.com",
                            "role": "STUDENT",
                        },
                    }
                }
            },
        },
        404: {
            "description": "User not found. Returns a message indicating that the user was not found.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": False,
                        "message": "User not found",
                        "user": None,
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. User retrieval failed due to missing or invalid authentication.",
            "content": {"application/json": {"example": {"message": "Unauthorized."}}},
        },
    },
)
async def get_user(
    user_id: str,
    handler: Annotated[GetUserHandler, Depends(get_get_user_handler)],
    token_data: Annotated[
        TokenData, Depends(require_roles(["admin", "teacher", "student"]))
    ],
) -> GetUserResponse:
    """Endpoint for retrieving user information by user ID.

    Args:
        user_id (str): The ID of the user to retrieve.
        handler (Annotated[GetUserHandler, Depends]): The handler responsible for processing the user retrieval.
        token_data: Annotated[TokenData, Depends]: The authenticated user data.
    Returns:
        GetUserResponse: The response containing the user details if found, otherwise a message indicating that the user was not found.
    """
    request = GetUserRequest(user_id=user_id)
    UserIdentityValidator.is_valid_user(token_data, user_id)
    response = await handler.handle(request)
    if not response.is_success:
        raise HTTPException(status_code=404, detail=response.model_dump())
    return response
