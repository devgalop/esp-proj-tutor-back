from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from src.features.assessments.get_assessments_summary.get_assessments_summary_handler import (
    GetAssessmentsSummaryHandler,
)
from src.features.assessments.get_assessments_summary.get_assessments_summary_request import (
    GetAssessmentsSummaryRequest,
)
from src.features.assessments.get_assessments_summary.get_assessments_summary_response import (
    GetAssessmentsSummaryResponse,
)
from src.features.assessments.shared.dependencies import (
    get_get_assessments_summary_handler,
)
from src.features.user_management.shared.require_roles import require_roles
from src.features.user_management.shared.token_generator import TokenData
from src.features.user_management.shared.validate_user import UserIdentityValidator

router = APIRouter()


@router.get(
    "/summary",
    status_code=200,
    summary="Get the assessments summary for a student",
    description="Endpoint to retrieve a summary of assessments for a specific student.",
    tags=["Assessments"],
    responses={
        200: {
            "description": "Assessments summary retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": True,
                        "message": "Assessments summary retrieved successfully.",
                        "total_assessments": 5,
                        "assessments": [
                            {
                                "assessment_id": "assessment_1",
                                "score": 85.0,
                                "date_taken": "2023-09-01T10:00:00Z",
                                "classification": "Pass",
                                "feedback": "Good performance.",
                            },
                            {
                                "assessment_id": "assessment_2",
                                "score": 70.0,
                                "date_taken": "2023-09-05T14:30:00Z",
                                "classification": "Pass",
                                "feedback": "Satisfactory performance.",
                            },
                        ],
                    }
                }
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
async def get_assessments_summary(
    handler: Annotated[
        GetAssessmentsSummaryHandler,
        Depends(get_get_assessments_summary_handler),
    ],
    token_data: Annotated[
        TokenData, Depends(require_roles(["admin", "teacher", "student"]))
    ],
    student_id: str,
    page: int = 0,
    page_size: int = 10,
) -> GetAssessmentsSummaryResponse:
    try:
        request = GetAssessmentsSummaryRequest(
            student_id=student_id, page=page, page_size=page_size
        )
        UserIdentityValidator.is_valid_user(
            user_logged=token_data,
            user_id_to_validate=student_id,
            blank_list_roles=["admin", "teacher"],
        )
        response = await handler.handle(request)
        if not response.is_success:
            raise HTTPException(status_code=400, detail=response.model_dump())
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
