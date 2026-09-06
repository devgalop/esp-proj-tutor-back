from unittest.mock import Mock, AsyncMock, patch
import pytest

from src.features.user_management.confirm_otp.confirm_otp_handler import (
    ConfirmOTPHandler,
)
from src.features.user_management.confirm_otp.confirm_otp_request import (
    ConfirmOTPRequest,
)
from src.features.user_management.shared.token_generator import (
    TokenResponse,
)
from itmentorsoft_persistence.dto import (
    CompleteUserResponse,
    UserRole,
    UserStatus,
    UserOTP,
)
from itmentorsoft_persistence import RefreshTokenInfo


@pytest.mark.asyncio
async def test_when_user_not_found_should_return_unsuccessful():
    user_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()
    refresh_token_repository = AsyncMock()

    user_repository.get_user_by_id = AsyncMock(return_value=None)

    handler = ConfirmOTPHandler(
        user_repository, password_hasher, token_generator, refresh_token_repository
    )
    response = await handler.handle(ConfirmOTPRequest(user_id="user_id", otp="ABC123"))

    assert not response.is_successful
    assert response.message == "User not found"
    user_repository.get_user_by_id.assert_called_once_with("user_id")
    token_generator.generate_token.assert_not_called()


@pytest.mark.asyncio
async def test_when_no_otp_stored_should_return_unsuccessful():
    user_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()
    refresh_token_repository = AsyncMock()

    user_repository.get_user_by_id = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    user_repository.get_user_otp = AsyncMock(return_value=None)

    handler = ConfirmOTPHandler(
        user_repository, password_hasher, token_generator, refresh_token_repository
    )
    response = await handler.handle(ConfirmOTPRequest(user_id="user_id", otp="ABC123"))

    assert not response.is_successful
    assert response.message == "OTP has expired or is invalid"
    token_generator.generate_token.assert_not_called()


@pytest.mark.asyncio
async def test_when_otp_is_expired_should_return_unsuccessful():
    user_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()
    refresh_token_repository = AsyncMock()

    user_repository.get_user_by_id = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    user_repository.get_user_otp = AsyncMock(
        return_value=UserOTP(
            user_id="user_id",
            otp="ABC123",
            status="active",
            expiration_time=1000.0,
        )
    )

    handler = ConfirmOTPHandler(
        user_repository, password_hasher, token_generator, refresh_token_repository
    )

    with patch(
        "src.features.user_management.confirm_otp.confirm_otp_handler.time",
    ) as mock_time:
        mock_time.return_value = 2000
        response = await handler.handle(
            ConfirmOTPRequest(user_id="user_id", otp="ABC123")
        )

    assert not response.is_successful
    assert response.message == "OTP has expired or is invalid"
    token_generator.generate_token.assert_not_called()


@pytest.mark.asyncio
async def test_when_otp_does_not_match_should_return_unsuccessful():
    user_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()
    refresh_token_repository = AsyncMock()

    user_repository.get_user_by_id = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    user_repository.get_user_otp = AsyncMock(
        return_value=UserOTP(
            user_id="user_id",
            otp="ABC123",
            status="active",
            expiration_time=9999999999,
        )
    )

    handler = ConfirmOTPHandler(
        user_repository, password_hasher, token_generator, refresh_token_repository
    )

    with patch(
        "src.features.user_management.confirm_otp.confirm_otp_handler.time",
    ) as mock_time:
        mock_time.return_value = 100
        response = await handler.handle(
            ConfirmOTPRequest(user_id="user_id", otp="WRONG1")
        )

    assert not response.is_successful
    assert response.message == "Invalid OTP"
    token_generator.generate_token.assert_not_called()


@pytest.mark.asyncio
async def test_when_otp_is_valid_should_return_tokens_and_save_refresh_token():
    user_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()
    refresh_token_repository = AsyncMock()

    user_repository.get_user_by_id = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    user_repository.get_user_otp = AsyncMock(
        return_value=UserOTP(
            user_id="user_id",
            otp="ABC123",
            status="active",
            expiration_time=9999999999,
        )
    )
    token_generator.generate_token = Mock(
        return_value=TokenResponse(token="jwt_token", expiration_time=3600)
    )
    token_generator.generate_random_token = Mock(
        return_value=TokenResponse(token="refresh_raw", expiration_time=604800)
    )
    password_hasher.hash_password = Mock(return_value="hashed_refresh")
    refresh_token_repository.revoke_tokens_by_user_id = AsyncMock()
    refresh_token_repository.save_token = AsyncMock()

    handler = ConfirmOTPHandler(
        user_repository, password_hasher, token_generator, refresh_token_repository
    )

    with patch(
        "src.features.user_management.confirm_otp.confirm_otp_handler.time",
    ) as mock_time:
        mock_time.return_value = 100
        response = await handler.handle(
            ConfirmOTPRequest(user_id="user_id", otp="ABC123")
        )

    assert response.is_successful
    assert response.message == "OTP confirmed successfully"
    assert response.token == "jwt_token"
    assert response.expiration_time == 3600
    assert response.refresh_token == "refresh_raw"
    assert response.user_id == "user_id"

    token_generator.generate_token.assert_called_once()
    token_generator.generate_random_token.assert_called_once()
    password_hasher.hash_password.assert_called_once_with("refresh_raw")
    refresh_token_repository.revoke_tokens_by_user_id.assert_called_once_with("user_id")
    refresh_token_repository.save_token.assert_called_once()

    saved_token_info = refresh_token_repository.save_token.call_args[0][0]
    assert isinstance(saved_token_info, RefreshTokenInfo)
    assert saved_token_info.user_id == "user_id"
    assert saved_token_info.token == "hashed_refresh"
    assert saved_token_info.expiration_time == 604800
    assert saved_token_info.status == "active"


@pytest.mark.asyncio
async def test_when_otp_is_empty_string_should_return_unsuccessful():
    user_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()
    refresh_token_repository = AsyncMock()

    user_repository.get_user_by_id = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    user_repository.get_user_otp = AsyncMock(
        return_value=UserOTP(
            user_id="user_id",
            otp="",
            status="active",
            expiration_time=9999999999,
        )
    )

    handler = ConfirmOTPHandler(
        user_repository, password_hasher, token_generator, refresh_token_repository
    )

    with patch(
        "src.features.user_management.confirm_otp.confirm_otp_handler.time",
    ) as mock_time:
        mock_time.return_value = 100
        response = await handler.handle(
            ConfirmOTPRequest(user_id="user_id", otp="ABC123")
        )

    assert not response.is_successful
    assert response.message == "OTP has expired or is invalid"
