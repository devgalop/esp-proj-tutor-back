from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.features.assessments.save_assessments_answers.save_assessments_answers_handler import (
    SaveAssessmentsAnswersHandler,
)
from src.features.assessments.save_assessments_answers.save_assessments_answers_request import (
    SaveAssessmentsAnswersRequest,
)
from src.features.assessments.save_assessments_answers.save_assessments_answers_response import (
    SaveAssessmentsAnswersResponse,
)
from src.features.assessments.shared.dependencies import (
    get_save_assessment_answers_handler,
)
from src.features.user_management.shared.require_roles import require_roles
from src.features.user_management.shared.token_generator import TokenData
from src.features.user_management.shared.validate_user import UserIdentityValidator

router = APIRouter()


@router.post(
    "/",
    status_code=200,
    summary="Save assessment answers",
    description="Endpoint to save the answers of an assessment taken by a user.",
    tags=["Assessments"],
    responses={
        200: {
            "description": "Assessment answers saved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": True,
                        "message": "Assessment answers saved successfully.",
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
        404: {
            "description": "User or assessment not found.",
            "content": {
                "application/json": {
                    "example": {"is_success": False, "message": "User not found."}
                }
            },
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": False,
                        "message": "Internal server error.",
                    }
                }
            },
        },
    },
)
async def save_assessment_answers(
    request: SaveAssessmentsAnswersRequest,
    handler: Annotated[
        SaveAssessmentsAnswersHandler, Depends(get_save_assessment_answers_handler)
    ],
    token_data: Annotated[TokenData, Depends(require_roles(["student"]))],
) -> SaveAssessmentsAnswersResponse:
    UserIdentityValidator.is_valid_user(
        user_logged=token_data, user_id_to_validate=request.user_id
    )
    response = await handler.handle(request)
    if not response.is_success:
        raise HTTPException(status_code=404, detail=response.model_dump())
    return response
