from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.features.reports.get_student_summary.get_student_summary_handler import (
    GetStudentSummaryHandler,
)
from src.features.reports.get_student_summary.get_student_summary_request import (
    GetStudentSummaryRequest,
)
from src.features.reports.get_student_summary.get_student_summary_response import (
    GetStudentSummaryResponse,
)
from src.features.reports.shared.dependencies import get_get_student_summary_handler
from src.features.user_management.shared.require_roles import require_roles
from src.features.user_management.shared.token_generator import TokenData
from src.features.user_management.shared.validate_user import UserIdentityValidator

router = APIRouter()


@router.get(
    "/student_summary",
    status_code=200,
    summary="Get student summary",
    description="Endpoint to retrieve the student summary for a given user ID.",
    tags=["Reports"],
    responses={
        200: {
            "description": "Student summary retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": True,
                        "message": "Student summary retrieved successfully",
                        "student_summary": {
                            "user_id": "123e4567e89b12d3a456426614174000",
                            "knowledge_profiles": [
                                {"topic": "Mathematics", "score": 85.0}
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
            "description": "Student not found.",
            "content": {
                "application/json": {
                    "example": {"is_success": False, "message": "Student not found."}
                }
            },
        },
    },
)
async def get_student_summary(
    id: str,
    handler: Annotated[
        GetStudentSummaryHandler, Depends(get_get_student_summary_handler)
    ],
    token_data: Annotated[
        TokenData, Depends(require_roles(["admin", "teacher", "student"]))
    ],
) -> GetStudentSummaryResponse:
    """Handle the request to get the student summary by user ID.

    Args:
        id (str): The ID of the user to retrieve the student summary for.
        handler (GetStudentSummaryHandler): The handler responsible for processing the request.
        token_data (TokenData): The token data of the authenticated user.

    Returns:
        GetStudentSummaryResponse: The student summary corresponding to the given user ID.
    """
    if not id:
        raise HTTPException(status_code=400, detail="User ID is required")
    request = GetStudentSummaryRequest(student_id=id)
    UserIdentityValidator.is_valid_user(
        user_logged=token_data,
        user_id_to_validate=id,
        blank_list_roles=["admin", "teacher"],
    )
    response = await handler.handle(request)
    if not response.is_success:
        raise HTTPException(status_code=404, detail=response.message)
    return response
