import time
from src.features.user_management.refresh_token.refresh_token_request import (
    RefreshTokenRequest,
)
from src.features.user_management.shared.password_hasher import PasswordHasher
from itmentorsoft_persistence.repositories import (
    RefreshTokenInfo,
    RefreshTokenRepository,
)
from src.features.user_management.shared.token_generator import (
    TokenGenerator,
    TokenRequest,
)
from itmentorsoft_persistence.repositories import UserRepository
from src.features.user_management.refresh_token.refresh_token_response import (
    RefreshTokenResponse,
)
from src.infrastructure.env_manager.env_manager import EnvironmentVariablesConstants


def _get_refresh_token_expiration_delta_seconds() -> int:
    """Get the refresh token expiration delta seconds from environment variables.

    Returns:
        int: The refresh token expiration delta seconds.
    """
    value = EnvironmentVariablesConstants.REFRESH_TOKEN_EXPIRATION_DELTA_SECONDS
    if not value:
        return 604800  # Default to 7 days if not set
    try:
        return int(value)
    except ValueError:
        return 604800  # Default to 7 days if not set


REFRESH_TOKEN_EXPIRATION_DELTA_SECONDS = _get_refresh_token_expiration_delta_seconds()


class RefreshTokenHandler:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        password_hasher: PasswordHasher,
        token_generator: TokenGenerator,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.password_hasher = password_hasher
        self.token_generator = token_generator

    async def handle(
        self, refresh_token_request: RefreshTokenRequest
    ) -> RefreshTokenResponse:
        """Handle the refresh token request.

        Args:
            refresh_token_request (RefreshTokenRequest): The refresh token request containing the user name and refresh token.

        Returns:
            RefreshTokenResponse: The response with new access and refresh tokens if successful.
        """
        user_found = await self.user_repository.get_user_by_username(
            refresh_token_request.user_name
        )
        if not user_found:
            return RefreshTokenResponse(
                is_successful=False,
                access_token=None,
                refresh_token=None,
                expiration_time=None,
                user_id=None,
            )

        record = await self.refresh_token_repository.get_active_token(user_found.id)

        if not record:
            return RefreshTokenResponse(
                is_successful=False,
                access_token=None,
                refresh_token=None,
                expiration_time=None,
                user_id=None,
            )

        if record.status == "revoked":
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="Refresh token revoked")

        if record.expiration_time < time.time():
            await self.refresh_token_repository.revoke_tokens_by_user_id(record.user_id)
            return RefreshTokenResponse(
                is_successful=False,
                access_token=None,
                refresh_token=None,
                expiration_time=None,
                user_id=None,
            )

        is_valid = self.password_hasher.verify_password(
            refresh_token_request.refresh_token, record.token_hashed
        )

        if not is_valid:
            return RefreshTokenResponse(
                is_successful=False,
                access_token=None,
                refresh_token=None,
                expiration_time=None,
                user_id=None,
            )

        await self.refresh_token_repository.revoke_tokens_by_user_id(record.user_id)

        token_response = self.token_generator.generate_token(
            TokenRequest(
                user_id=user_found.id,
                user_name=user_found.username,
                role=user_found.role.value,
            )
        )

        new_refresh_token = self.token_generator.generate_random_token()
        hashed_refresh_token = self.password_hasher.hash_password(
            new_refresh_token.token
        )

        refresh_token_info = RefreshTokenInfo(
            user_id=record.user_id,
            token=hashed_refresh_token,
            expiration_time=new_refresh_token.expiration_time,
            status="active",
        )
        await self.refresh_token_repository.save_token(refresh_token_info)

        return RefreshTokenResponse(
            is_successful=True,
            access_token=token_response.token,
            refresh_token=new_refresh_token.token,
            expiration_time=token_response.expiration_time,
            user_id=record.user_id,
        )
