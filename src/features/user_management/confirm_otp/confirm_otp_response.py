from pydantic import BaseModel


class ConfirmOTPResponse(BaseModel):
    is_successful: bool
    message: str
    token: str | None = None
    expiration_time: float = 0
    refresh_token: str | None = None
    user_id: str | None = None
