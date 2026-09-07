from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from src.features.assessments.get_quantity_of_assessments.get_quantity_of_assessments_handler import (
    GetQuantityOfAssessmentsHandler,
)
from src.features.assessments.get_quantity_of_assessments.get_quantity_of_assessments_request import (
    GetQuantityOfAssessmentsRequest,
)
from src.features.assessments.get_quantity_of_assessments.get_quantity_of_assessments_response import (
    GetQuantityOfAssessmentsResponse,
)
from src.features.assessments.shared.dependencies import (
    get_get_quantity_of_assessments_handler,
)
from src.features.user_management.shared.require_roles import require_roles
from src.features.user_management.shared.token_generator import TokenData
from src.features.user_management.shared.validate_user import UserIdentityValidator

router = APIRouter()


@router.get(
    "/quantity",
    status_code=200,
    summary="Get the quantity of assessments for a student",
    description="Endpoint to retrieve the total number of assessments for a specific student.",
    tags=["Assessments"],
    responses={
        200: {
            "description": "Quantity of assessments retrieved successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "is_success": True,
                        "message": "Quantity of assessments retrieved successfully.",
                        "total_assessments": 5,
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
        404: {
            "description": "Student not found.",
            "content": {
                "application/json": {
                    "example": {"is_success": False, "message": "Student not found."}
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
async def get_quantity_of_assessments(
    student_id: str,
    handler: Annotated[
        GetQuantityOfAssessmentsHandler,
        Depends(get_get_quantity_of_assessments_handler),
    ],
    token_data: Annotated[
        TokenData, Depends(require_roles(["admin", "teacher", "student"]))
    ],
) -> GetQuantityOfAssessmentsResponse:

    try:
        request = GetQuantityOfAssessmentsRequest(student_id=student_id)
        UserIdentityValidator.is_valid_user(
            user_logged=token_data,
            user_id_to_validate=student_id,
            blank_list_roles=["admin", "teacher"],
        )
        response = await handler.handle(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
