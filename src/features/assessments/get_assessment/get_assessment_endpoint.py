from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.features.assessments.get_assessment.get_assessment_handler import (
    GetAssessmentHandler,
)
from src.features.assessments.get_assessment.get_assessment_request import (
    GetAssessmentRequest,
)
from src.features.assessments.get_assessment.get_assessment_response import (
    GetAssessmentResponse,
)
from src.features.assessments.shared.dependencies import get_get_assessment_handler
from src.features.user_management.shared.require_roles import require_roles
from src.features.user_management.shared.token_generator import TokenData
from src.features.user_management.shared.validate_user import UserIdentityValidator

router = APIRouter()


@router.get(
    "/",
    status_code=200,
    summary="Get assessment",
    description="Endpoint to generate an assessment for a user.",
    tags=["Assessments"],
    responses={
        200: {
            "description": "Assessment retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": True,
                        "message": "Assessment retrieved successfully",
                        "assessment_id": "123e4567e89b12d3a456426614174000",
                        "questions": [
                            {
                                "question_id": "123e4567e89b12d3a456426614174000",
                                "text_to_evaluate": "Explain the difference between...",
                            }
                        ],
                    }
                }
            },
        },
        400: {
            "description": "Invalid request data.",
            "content": {
                "application/json": {
                    "example": {"is_success": False, "message": "Invalid request data."}
                }
            },
        },
        401: {
            "description": "Unauthorized.",
            "content": {
                "application/json": {
                    "example": {"is_success": False, "message": "Unauthorized."}
                }
            },
        },
    },
)
async def get_assessment(
    user_id: str,
    handler: Annotated[GetAssessmentHandler, Depends(get_get_assessment_handler)],
    token_data: Annotated[TokenData, Depends(require_roles(["student"]))],
) -> GetAssessmentResponse:
    request = GetAssessmentRequest(student_id=user_id)
    UserIdentityValidator.is_valid_user(
        user_logged=token_data, user_id_to_validate=user_id
    )
    response = await handler.handle(request)
    if not response.is_success:
        raise HTTPException(status_code=400, detail=response.model_dump())
    return response
