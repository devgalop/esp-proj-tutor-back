from pydantic import BaseModel, field_validator
import re

USERNAME_PATTERN = r"\w+$"


class RefreshTokenRequest(BaseModel):
    user_id: str
    user_name: str
    refresh_token: str

    @field_validator("refresh_token")
    def validate_refresh_token(cls, value: str) -> str:
        if not value:
            raise ValueError("Refresh token cannot be empty")
        if len(value) < 5:
            raise ValueError("Refresh token is too short")
        if len(value) > 150:
            raise ValueError("Refresh token is too long")
        return value

    @field_validator("user_name")
    def validate_username(cls, value: str) -> str:
        if not value:
            raise ValueError("Username is required")
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(value) > 20:
            raise ValueError("Username must be no more than 20 characters long")
        if not re.match(USERNAME_PATTERN, value):
            raise ValueError(
                "Username must be alphanumeric and can include underscores"
            )
        return value

    @field_validator("user_id")
    def validate_user_id(cls, value: str) -> str:
        if not value:
            raise ValueError("User ID is required")
        if len(value) < 3:
            raise ValueError("User ID must be at least 3 characters long")
        if len(value) > 100:
            raise ValueError("User ID must be no more than 100 characters long")
        return value
