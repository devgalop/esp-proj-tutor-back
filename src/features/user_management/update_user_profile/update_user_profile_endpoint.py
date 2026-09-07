from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from src.features.user_management.shared.dependencies import (
    get_update_user_profile_handler,
)
from src.features.user_management.shared.require_roles import require_roles
from src.features.user_management.shared.token_generator import TokenData
from src.features.user_management.shared.validate_user import UserIdentityValidator
from src.features.user_management.update_user_profile.update_user_profile_handler import (
    UpdateUserProfileHandler,
)
from src.features.user_management.update_user_profile.update_user_profile_request import (
    UpdateUserProfileRequest,
)
from src.features.user_management.update_user_profile.update_user_profile_response import (
    UpdateUserProfileResponse,
)

router = APIRouter()


@router.put(
    "/profile",
    status_code=200,
    summary="Update User Profile",
    description="Endpoint for updating a user's profile. Returns a message indicating the result of the update operation.",
    tags=["User Management"],
    responses={
        200: {
            "description": "User profile updated successfully. Returns a message indicating the successful update.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": True,
                        "message": "Username updated successfully",
                    }
                }
            },
        },
        400: {
            "description": "Bad Request. User profile update failed due to invalid input data.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": False,
                        "message": "Username is not available",
                    }
                }
            },
        },
        404: {
            "description": "Not Found. User profile update failed because the user was not found.",
            "content": {
                "application/json": {
                    "example": {"is_success": False, "message": "User not found"}
                }
            },
        },
        500: {
            "description": "Internal Server Error. An unexpected error occurred during the user profile update.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": False,
                        "message": "An unexpected error occurred",
                    }
                }
            },
        },
    },
)
async def update_user_profile(
    request: UpdateUserProfileRequest,
    handler: Annotated[
        UpdateUserProfileHandler, Depends(get_update_user_profile_handler)
    ],
    token_data: Annotated[
        TokenData, Depends(require_roles(["admin", "teacher", "student"]))
    ],
) -> UpdateUserProfileResponse:
    """Endpoint for updating a user's profile.

    Args:
        request (UpdateUserProfileRequest): The user data for updating the profile.
        handler (Annotated[UpdateUserProfileHandler, Depends]): The handler responsible for processing the user profile update.
        token_data: Annotated[TokenData, Depends]: The token data containing user information and roles.

    Returns:
        UpdateUserProfileResponse: The response containing the message about the user profile update result.
    """
    UserIdentityValidator.is_valid_user(
        user_logged=token_data, user_id_to_validate=request.user_id
    )
    response = await handler.handle(request)
    if not response.is_success:
        raise HTTPException(status_code=400, detail={"message": response.model_dump()})
    return response
