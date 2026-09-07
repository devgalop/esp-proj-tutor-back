from unittest.mock import Mock, AsyncMock, patch
import pytest

from src.features.user_management.login.login_handler import LoginHandler
from src.features.user_management.login.login_request import LoginRequest
from itmentorsoft_persistence.dto import (
    CompleteUserResponse,
    UserRole,
    UserStatus,
    UserAccessTries,
)


@pytest.mark.asyncio
async def test_when_credentials_are_valid_should_return_successful_with_user_id():
    user_repository = AsyncMock()
    password_hasher = Mock()
    otp_generator = Mock()
    notification_service = AsyncMock()
    template_loader = Mock()

    user_repository.get_user_by_email = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    user_repository.get_login_try_counter = AsyncMock(return_value=None)
    password_hasher.verify_password = Mock(return_value=True)
    otp_generator.generate_otp = Mock(return_value="ABC123")
    user_repository.save_user_otp = AsyncMock()
    user_repository.reset_login_try_counter = AsyncMock()

    handler = LoginHandler(
        user_repository,
        password_hasher,
        otp_generator,
        notification_service,
        template_loader,
    )
    sample_pass = "Password123!"
    response = await handler.handle(
        LoginRequest(email="test@example.com", password=sample_pass)
    )

    assert response.is_successful
    assert response.user_id == "user_id"
    user_repository.get_user_by_email.assert_called_once_with("test@example.com")
    password_hasher.verify_password.assert_called_once_with(
        sample_pass, "hashed_password"
    )
    otp_generator.generate_otp.assert_called_once()
    user_repository.save_user_otp.assert_called_once()
    user_repository.reset_login_try_counter.assert_called_once_with("user_id")


@pytest.mark.asyncio
async def test_when_email_does_not_exist_should_return_unsuccessful():
    user_repository = AsyncMock()
    password_hasher = Mock()
    otp_generator = Mock()
    notification_service = AsyncMock()
    template_loader = Mock()

    user_repository.get_user_by_email = AsyncMock(return_value=None)

    handler = LoginHandler(
        user_repository,
        password_hasher,
        otp_generator,
        notification_service,
        template_loader,
    )
    response = await handler.handle(
        LoginRequest(email="invalid@example.com", password="Password123!")
    )

    assert not response.is_successful
    assert response.user_id is None
    user_repository.get_user_by_email.assert_called_once_with("invalid@example.com")
    password_hasher.verify_password.assert_not_called()
    otp_generator.generate_otp.assert_not_called()


@pytest.mark.asyncio
async def test_when_password_is_incorrect_should_increment_tries_and_return_unsuccessful():
    user_repository = AsyncMock()
    password_hasher = Mock()
    otp_generator = Mock()
    notification_service = AsyncMock()
    template_loader = Mock()

    user_repository.get_user_by_email = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    user_repository.get_login_try_counter = AsyncMock(return_value=None)
    password_hasher.verify_password = Mock(return_value=False)
    user_repository.increment_login_try_counter = AsyncMock()

    handler = LoginHandler(
        user_repository,
        password_hasher,
        otp_generator,
        notification_service,
        template_loader,
    )
    response = await handler.handle(
        LoginRequest(email="test@example.com", password="IncorrectPassword12!")
    )

    assert not response.is_successful
    assert response.user_id is None
    user_repository.get_user_by_email.assert_called_once_with("test@example.com")
    password_hasher.verify_password.assert_called_once_with(
        "IncorrectPassword12!", "hashed_password"
    )
    user_repository.increment_login_try_counter.assert_called_once()
    otp_generator.generate_otp.assert_not_called()


@pytest.mark.asyncio
async def test_when_user_is_temporarily_blocked_should_return_blocked_response():
    user_repository = AsyncMock()
    password_hasher = Mock()
    otp_generator = Mock()
    notification_service = AsyncMock()
    template_loader = Mock()

    user_repository.get_user_by_email = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    user_repository.get_login_try_counter = AsyncMock(
        return_value=UserAccessTries(
            user_id="user_id",
            retry_count=3,
            is_temporarily_blocked=True,
            temporary_block_expiration=9999999999,
            definitively_blocked=False,
        )
    )

    handler = LoginHandler(
        user_repository,
        password_hasher,
        otp_generator,
        notification_service,
        template_loader,
    )

    with patch(
        "src.features.user_management.login.login_handler.time",
        return_value=100.0,
    ):
        response = await handler.handle(
            LoginRequest(email="test@example.com", password="Password123!")
        )

    assert not response.is_successful
    assert response.is_temporarily_blocked is True
    assert response.blocked_until == 9999999999
    password_hasher.verify_password.assert_not_called()


@pytest.mark.asyncio
async def test_when_user_is_definitively_blocked_should_return_blocked_response():
    user_repository = AsyncMock()
    password_hasher = Mock()
    otp_generator = Mock()
    notification_service = AsyncMock()
    template_loader = Mock()

    user_repository.get_user_by_email = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    user_repository.get_login_try_counter = AsyncMock(
        return_value=UserAccessTries(
            user_id="user_id",
            retry_count=10,
            is_temporarily_blocked=False,
            temporary_block_expiration=0,
            definitively_blocked=True,
        )
    )

    handler = LoginHandler(
        user_repository,
        password_hasher,
        otp_generator,
        notification_service,
        template_loader,
    )
    response = await handler.handle(
        LoginRequest(email="test@example.com", password="Password123!")
    )

    assert not response.is_successful
    assert response.is_definitively_blocked is True
    password_hasher.verify_password.assert_not_called()
