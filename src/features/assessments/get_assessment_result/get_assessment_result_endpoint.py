from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.features.assessments.get_assessment_result.get_assessment_result_handler import (
    GetAssessmentResultHandler,
)
from src.features.assessments.get_assessment_result.get_assessment_result_request import (
    GetAssessmentResultRequest,
)
from src.features.assessments.get_assessment_result.get_assessment_result_response import (
    GetAssessmentResultResponse,
)
from src.features.assessments.shared.dependencies import (
    get_get_assessment_result_handler,
)
from src.features.user_management.shared.require_roles import require_roles
from src.features.user_management.shared.token_generator import TokenData
from src.features.user_management.shared.validate_user import UserIdentityValidator

router = APIRouter()


@router.get(
    "/assessment_result",
    status_code=200,
    summary="Get assessment result",
    description="Endpoint to retrieve the result of a specific assessment for a user.",
    tags=["Assessments"],
    responses={
        200: {
            "description": "Assessment result retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": True,
                        "message": "Assessment result retrieved successfully.",
                        "result": {
                            "assessment_id": "123e4567-e89b-12d3-a456-426614174000",
                            "user_id": "user_123",
                            "avg_score": 85.0,
                            "classification": "Pass",
                            "feedback": "Good job!",
                            "answer_scores": [
                                {
                                    "question_id": "q1",
                                    "question_text": "What is the capital of France?",
                                    "answer": "Paris",
                                    "score": 10.0,
                                    "feedback": "Correct answer.",
                                    "misconceptions": None,
                                    "key_concepts": ["Geography", "Europe"],
                                }
                            ],
                        },
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
            "description": "Assessment result not found.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": False,
                        "message": "Assessment result not found.",
                    }
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
async def get_assessment_result(
    user_id: str,
    assessment_id: str,
    handler: Annotated[
        GetAssessmentResultHandler, Depends(get_get_assessment_result_handler)
    ],
    token_data: Annotated[
        TokenData, Depends(require_roles(["admin", "teacher", "student"]))
    ],
) -> GetAssessmentResultResponse:
    """
    Retrieve the result of a specific assessment for a user.

    Args:
        user_id (str): The ID of the user.
        assessment_id (str): The ID of the assessment.
        handler (GetAssessmentResultHandler): The handler to process the request.
        token_data (TokenData): The token data of the logged-in user.

    Returns:
        GetAssessmentResultResponse: The response containing the assessment result or an error message.
    """
    try:
        request = GetAssessmentResultRequest(
            user_id=user_id, assessment_id=assessment_id
        )
        UserIdentityValidator.is_valid_user(
            user_logged=token_data,
            user_id_to_validate=user_id,
            blank_list_roles=["admin", "teacher"],
        )
        response = await handler.handle(request)
        if not response.is_success:
            raise HTTPException(status_code=404, detail=response.message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
