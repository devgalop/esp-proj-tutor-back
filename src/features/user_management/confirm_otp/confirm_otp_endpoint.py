from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Annotated

from src.features.user_management.confirm_otp.confirm_otp_handler import (
    ConfirmOTPHandler,
)
from src.features.user_management.confirm_otp.confirm_otp_request import (
    ConfirmOTPRequest,
)
from src.features.user_management.confirm_otp.confirm_otp_response import (
    ConfirmOTPResponse,
)
from src.features.user_management.shared.dependencies import get_confirm_otp_handler

router = APIRouter()


@router.post(
    "/otp/validate",
    status_code=200,
    summary="Confirm OTP",
    description="Endpoint to confirm the OTP sent to the user.",
    tags=["Authentication"],
    responses={
        200: {
            "description": "OTP confirmed successfully.",
            "content": {"application/json": {"example": {"is_successful": True}}},
        },
        400: {
            "description": "Invalid OTP or OTP expired.",
            "content": {"application/json": {"example": {"is_successful": False}}},
        },
        401: {
            "description": "Unauthorized. OTP confirmation failed due to invalid credentials.",
            "content": {"application/json": {"example": {"is_successful": False}}},
        },
    },
)
async def confirm_otp(
    request: ConfirmOTPRequest,
    handler: Annotated[ConfirmOTPHandler, Depends(get_confirm_otp_handler)],
    response_http: Response,
) -> ConfirmOTPResponse:
    result = await handler.handle(request)
    if not result.is_successful or not result.refresh_token or not result.token:
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired.")
    response_http.set_cookie(
        key="refresh_token", value=result.refresh_token, httponly=True, secure=True
    )
    response_http.set_cookie(
        key="access_token", value=result.token, httponly=True, secure=True
    )
    return result
