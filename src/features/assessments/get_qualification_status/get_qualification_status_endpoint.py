from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.features.assessments.get_qualification_status.get_qualification_status_handler import (
    GetQualificationStatusHandler,
)
from src.features.assessments.get_qualification_status.get_qualification_status_request import (
    GetQualificationStatusRequest,
)
from src.features.assessments.get_qualification_status.get_qualification_status_response import (
    GetQualificationStatusResponse,
)
from src.features.assessments.shared.dependencies import (
    get_get_qualification_status_handler,
)
from src.features.user_management.shared.require_roles import require_roles
from src.features.user_management.shared.token_generator import TokenData
from src.features.user_management.shared.validate_user import UserIdentityValidator

router = APIRouter()


@router.get(
    "/qualification-status",
    status_code=200,
    summary="Get the qualification status of an assessment for a user",
    description="Endpoint to retrieve the qualification status of a specific assessment for a user.",
    tags=["Assessments"],
    responses={
        200: {
            "description": "Qualification status retrieved successfully.",
            "content": {
                "application/json": {"example": {"is_already_qualified": True}}
            },
        },
        400: {
            "description": "Invalid request data.",
        },
        500: {
            "description": "Internal server error.",
        },
    },
)
async def get_qualification_status(
    user_id: str,
    assessment_id: str,
    handler: Annotated[
        GetQualificationStatusHandler,
        Depends(get_get_qualification_status_handler),
    ],
    token_data: Annotated[
        TokenData, Depends(require_roles(["admin", "teacher", "student"]))
    ],
) -> GetQualificationStatusResponse:
    try:
        request = GetQualificationStatusRequest(
            user_id=user_id, assessment_id=assessment_id
        )
        UserIdentityValidator.is_valid_user(
            user_logged=token_data,
            user_id_to_validate=user_id,
            blank_list_roles=["admin", "teacher"],
        )
        response = await handler.handle(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
