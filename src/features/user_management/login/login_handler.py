from src.features.user_management.login.login_request import LoginRequest
from src.features.user_management.login.login_response import LoginResponse
from src.features.user_management.shared.otp_generator import OTPGenerator
from src.features.user_management.shared.password_hasher import PasswordHasher
from time import time
from itmentorsoft_persistence.dto import UserAccessTries, UserOTPRequest
from itmentorsoft_persistence.repositories import UserRepository
from itmentorsoft_persistence.dto import IncrementLoginTryCounterRequest
from src.infrastructure.env_manager.env_manager import EnvironmentVariablesConstants


class LoginHandler:
    MAX_USER_ACCESS_TRY_LIMIT = int(
        EnvironmentVariablesConstants.USER_ACCESS_TRY_LIMIT
    ) + int(EnvironmentVariablesConstants.USER_ACCESS_LOCK_LIMIT)

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        otp_generator: OTPGenerator,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.otp_generator = otp_generator

    async def handle(self, request: LoginRequest) -> LoginResponse:
        """ "Handle the login request.

        Args:
            request (LoginRequest): The login request containing the user's email and password.
        Returns:
            LoginResponse: The response indicating whether the login was successful, along with a token and its expiration time if successful.
        """

        user = await self.user_repository.get_user_by_email(request.email)
        if not user:
            return LoginResponse(is_successful=False, user_id=None)  # nosec

        user_tries = await self.user_repository.get_login_try_counter(user.id)
        if self._is_blocked(user_tries):
            return LoginResponse(
                is_successful=False,
                user_id=None,
                is_temporarily_blocked=(
                    user_tries.is_temporarily_blocked if user_tries else False
                ),
                blocked_until=(
                    user_tries.temporary_block_expiration if user_tries else 0
                ),
                is_definitively_blocked=(
                    user_tries.definitively_blocked if user_tries else False
                ),
            )  # nosec

        if not self.password_hasher.verify_password(
            request.password, user.password_hashed
        ):
            increment = await self._create_fail_try(user.id, user_tries)
            return LoginResponse(
                is_successful=False,
                user_id=None,
                is_temporarily_blocked=(
                    increment.is_temporarily_blocked if increment else False
                ),
                blocked_until=increment.temporary_block_expiration if increment else 0,
                is_definitively_blocked=(
                    increment.is_definitively_blocked if increment else False
                ),
            )  # nosec

        otp = self.otp_generator.generate_otp()
        otp_expiration_time = int(time()) + int(
            EnvironmentVariablesConstants.USER_OTP_EXPIRED_TIME_SECONDS
        )
        await self.user_repository.save_user_otp(
            UserOTPRequest(
                user_id=user.id, otp=otp, expiration_time=otp_expiration_time
            )
        )

        await self.user_repository.reset_login_try_counter(user.id)
        return LoginResponse(is_successful=True, user_id=user.id)

    def _is_blocked(self, user_tries: UserAccessTries | None = None) -> bool:
        """Validate if user is blocked based on their access tries.

        Args:
            user_tries (UserAccessTries | None, optional): The user's access tries information. Defaults to None.

        Returns:
            bool: True if the user is blocked, False otherwise.
        """
        if not user_tries:
            return False
        if user_tries.definitively_blocked:
            return True
        if (
            user_tries.is_temporarily_blocked
            and user_tries.temporary_block_expiration > int(time())
        ):
            return True
        return False

    async def _create_fail_try(
        self, user_id: str, user_tries: UserAccessTries | None = None
    ) -> IncrementLoginTryCounterRequest:
        """Increment number of failed login attempts for a user.

        Args:
            user_id (str): User Identifier
            user_tries (UserAccessTries | None, optional): The user's access tries information. Defaults to None.

        Returns:
            IncrementLoginTryCounterRequest: The request object representing the incremented login try counter.
        """
        if not user_tries:
            increment_request = IncrementLoginTryCounterRequest(
                user_id=user_id,
                counter=1,
                is_temporarily_blocked=False,
                temporary_block_expiration=0,
                is_definitively_blocked=False,
            )
            await self.user_repository.increment_login_try_counter(increment_request)
            return increment_request
        user_tries.retry_count += 1

        if user_tries.retry_count >= int(
            EnvironmentVariablesConstants.USER_ACCESS_TRY_LIMIT
        ):
            user_tries.is_temporarily_blocked = True
            blocked_time = int(time()) + (
                int(EnvironmentVariablesConstants.USER_ACCESS_LOCK_TIME_SECONDS)
                * user_tries.retry_count
            )
            user_tries.temporary_block_expiration = blocked_time

        increment_request = IncrementLoginTryCounterRequest(
            user_id=user_id,
            counter=user_tries.retry_count,
            is_temporarily_blocked=user_tries.is_temporarily_blocked,
            temporary_block_expiration=user_tries.temporary_block_expiration,
            is_definitively_blocked=user_tries.retry_count
            >= self.MAX_USER_ACCESS_TRY_LIMIT,
        )
        await self.user_repository.increment_login_try_counter(increment_request)

        return increment_request
