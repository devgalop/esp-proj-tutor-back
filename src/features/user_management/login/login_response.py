from pydantic import BaseModel


class LoginResponse(BaseModel):
    is_successful: bool
    user_id: str | None
    is_temporarily_blocked: bool = False
    blocked_until: float = 0
    is_definitively_blocked: bool = False
