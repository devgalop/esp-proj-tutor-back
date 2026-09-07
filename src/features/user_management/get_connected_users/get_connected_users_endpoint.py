from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from src.features.user_management.get_connected_users.get_connected_users_handler import (
    GetConnectedUsersHandler,
)
from src.features.user_management.shared.dependencies import (
    get_get_connected_users_handler,
)
from src.features.user_management.shared.require_roles import require_roles
from src.features.user_management.shared.token_generator import TokenData
from src.features.user_management.get_connected_users.get_connected_users_response import (
    GetConnectedUsersResponse,
)

router = APIRouter()


@router.get(
    "/connected/total",
    status_code=200,
    summary="Get the total number of connected users",
    description="Retrieves the total number of users with active refresh tokens.",
    tags=["User Management"],
    responses={
        200: {
            "description": "Successfully retrieved the total number of connected users.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": True,
                        "message": "Users connected have been found successfully",
                        "total_users": 5,
                    }
                }
            },
        },
        400: {
            "description": "Bad Request. Unable to obtain any connected users.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": False,
                        "message": "Cannot obtain any connected users",
                        "total_users": 0,
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. The request requires authentication.",
            "content": {"application/json": {"example": {"detail": "Unauthorized"}}},
        },
        404: {
            "description": "Not Found. No connected users found.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": False,
                        "message": "No connected users found",
                        "total_users": 0,
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error. An unexpected error occurred while processing the request.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": False,
                        "message": "An unexpected error occurred while processing the request",
                        "total_users": 0,
                    }
                }
            },
        },
    },
)
async def get_connected_users(
    handler: Annotated[
        GetConnectedUsersHandler, Depends(get_get_connected_users_handler)
    ],
    _: Annotated[TokenData, Depends(require_roles(["admin", "teacher"]))],
) -> GetConnectedUsersResponse:
    response = await handler.handle()
    if not response.is_success:
        raise HTTPException(status_code=400, detail=response.model_dump())
    return response
