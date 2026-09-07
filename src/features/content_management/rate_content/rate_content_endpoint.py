from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from src.features.content_management.rate_content.rate_content_handler import (
    RateContentHandler,
)
from src.features.content_management.rate_content.rate_content_request import (
    RateContentRequest,
)
from src.features.content_management.shared.dependencies import get_rate_content_handler
from src.features.user_management.shared.require_roles import require_roles
from src.features.user_management.shared.token_generator import TokenData
from src.features.user_management.shared.validate_user import UserIdentityValidator

router = APIRouter()


@router.post(
    "/rate",
    status_code=200,
    summary="Rate content",
    description="Endpoint to rate educational resource content.",
    tags=["Content Management"],
    responses={
        200: {
            "description": "Content rated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": True,
                        "message": "Content rated successfully.",
                    }
                }
            },
        },
        400: {
            "description": "Bad Request. Content rating failed due to invalid input data.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": False,
                        "message": "Content rating failed. Invalid input data.",
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Content rating failed due to missing or invalid authentication.",
            "content": {"application/json": {"example": {"message": "Unauthorized."}}},
        },
    },
)
async def rate_content(
    request: RateContentRequest,
    handler: Annotated[RateContentHandler, Depends(get_rate_content_handler)],
    token_data: Annotated[TokenData, Depends(require_roles(["student"]))],
):
    UserIdentityValidator.is_valid_user(
        user_logged=token_data, user_id_to_validate=request.user_id
    )
    response = await handler.handle(request)
    if not response.is_success:
        raise HTTPException(status_code=400, detail=response.message)
    return response
