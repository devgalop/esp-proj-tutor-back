from pydantic import BaseModel, field_validator


class ConfirmOTPRequest(BaseModel):
    user_id: str
    otp: str

    @field_validator("user_id")
    def validate_user_id(cls, value: str) -> str:
        if not value:
            raise ValueError("User ID must not be empty.")
        if len(value) < 3:
            raise ValueError("User ID must be at least 3 characters long.")
        if len(value) > 100:
            raise ValueError("User ID must not exceed 100 characters.")
        return value

    @field_validator("otp")
    def validate_otp(cls, value: str) -> str:
        if not value or len(value) != 6:
            raise ValueError("OTP must be a 6-character string.")
        return value.upper()
