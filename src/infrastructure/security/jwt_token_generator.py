import uuid
import jwt
from datetime import datetime, timedelta, timezone
from src.infrastructure.env_manager.env_manager import EnvironmentVariablesConstants

from src.features.user_management.shared.token_generator import (
    InvalidTokenError,
    TokenData,
    TokenGenerator,
    TokenRequest,
    TokenResponse,
)


class TokenPayload:
    def __init__(self, user_id: str, user_name: str, role: str, exp: datetime):
        self.user_id = user_id
        self.user_name = user_name
        self.role = role
        self.exp = exp

    def to_dict(self) -> dict[str, str | datetime]:
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "role": self.role,
            "exp": self.exp,
        }


class JWTTokenGenerator(TokenGenerator):

    def generate_token(self, request: TokenRequest) -> TokenResponse:
        expiration_time = datetime.now(tz=timezone.utc) + timedelta(
            seconds=int(EnvironmentVariablesConstants.JWT_EXPIRATION_DELTA_SECONDS)
        )
        token_payload = TokenPayload(
            user_id=request.user_id,
            user_name=request.user_name,
            role=request.role,
            exp=expiration_time,
        ).to_dict()
        return TokenResponse(
            token=jwt.encode(
                token_payload,
                EnvironmentVariablesConstants.JWT_SECRET_KEY,
                algorithm=EnvironmentVariablesConstants.JWT_ALGORITHM,
            ),  # pyright: ignore[reportUnknownMemberType]
            expiration_time=expiration_time.timestamp(),
        )

    def validate_token(self, token: str, verify_exp: bool = True) -> TokenData:
        try:
            payload = jwt.decode(
                token,
                EnvironmentVariablesConstants.JWT_SECRET_KEY,
                algorithms=EnvironmentVariablesConstants.JWT_ALGORITHM,
                options={"verify_exp": verify_exp},
            )  # pyright: ignore[reportUnknownMemberType]
            return TokenData(
                user_id=payload["user_id"],
                user_name=payload["user_name"],
                role=payload["role"],
            )
        except jwt.PyJWTError as e:
            raise InvalidTokenError(str(e)) from e

    def generate_random_token(self) -> TokenResponse:
        uuid_token = uuid.uuid4().hex
        expiration_time = datetime.now(tz=timezone.utc) + timedelta(
            seconds=int(
                EnvironmentVariablesConstants.RANDOM_TOKEN_EXPIRATION_DELTA_SECONDS
            )
        )
        return TokenResponse(
            token=uuid_token, expiration_time=expiration_time.timestamp()
        )
