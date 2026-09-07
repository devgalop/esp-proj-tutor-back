from time import time

from itmentorsoft_persistence import (
    RefreshTokenInfo,
    RefreshTokenRepository,
    UserRepository,
)

from src.features.user_management.confirm_otp.confirm_otp_request import (
    ConfirmOTPRequest,
)
from src.features.user_management.confirm_otp.confirm_otp_response import (
    ConfirmOTPResponse,
)
from src.features.user_management.shared.password_hasher import PasswordHasher
from src.features.user_management.shared.token_generator import (
    TokenGenerator,
    TokenRequest,
)


class ConfirmOTPHandler:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_generator: TokenGenerator,
        refresh_token_repository: RefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_generator = token_generator
        self.refresh_token_repository = refresh_token_repository

    async def handle(self, request: ConfirmOTPRequest) -> ConfirmOTPResponse:

        user = await self.user_repository.get_user_by_id(request.user_id)
        if not user:
            return ConfirmOTPResponse(is_successful=False, message="User not found")

        user_otp = await self.user_repository.get_user_otp(request.user_id)

        if not user_otp or not user_otp.otp or user_otp.expiration_time < int(time()):
            return ConfirmOTPResponse(
                is_successful=False, message="OTP has expired or is invalid"
            )

        if request.otp != user_otp.otp:
            return ConfirmOTPResponse(is_successful=False, message="Invalid OTP")

        token_response = self.token_generator.generate_token(
            TokenRequest(user_id=user.id, user_name=user.username, role=user.role.value)
        )

        refresh_token_response = self.token_generator.generate_random_token()
        hashed_refresh_token = self.password_hasher.hash_password(
            refresh_token_response.token
        )
        refresh_token_info = RefreshTokenInfo(
            user_id=user.id,
            token=hashed_refresh_token,
            expiration_time=refresh_token_response.expiration_time,
            status="active",
        )
        await self.refresh_token_repository.revoke_tokens_by_user_id(user.id)
        await self.refresh_token_repository.save_token(refresh_token_info)

        return ConfirmOTPResponse(
            is_successful=True,
            message="OTP confirmed successfully",
            token=token_response.token,
            expiration_time=token_response.expiration_time,
            refresh_token=refresh_token_response.token,
            user_id=user.id,
        )
