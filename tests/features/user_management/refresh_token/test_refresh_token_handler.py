from unittest.mock import Mock, AsyncMock, patch
import pytest
from fastapi import HTTPException

from src.features.user_management.refresh_token.refresh_token_handler import (
    RefreshTokenHandler,
)
from src.features.user_management.refresh_token.refresh_token_request import (
    RefreshTokenRequest,
)
from itmentorsoft_persistence.repositories import (
    RefreshTokenData,
    RefreshTokenInfo,
)
from src.features.user_management.shared.token_generator import TokenResponse
from itmentorsoft_persistence.dto import (
    CompleteUserResponse,
    UserRole,
    UserStatus,
)


@pytest.mark.asyncio
async def test_when_user_not_found_should_return_unsuccessful():
    user_repository = AsyncMock()
    refresh_token_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()

    user_repository.get_user_by_username = AsyncMock(return_value=None)

    handler = RefreshTokenHandler(
        user_repository, refresh_token_repository, password_hasher, token_generator
    )
    response = await handler.handle(
        RefreshTokenRequest(
            user_id="user_id", user_name="testuser", refresh_token="some-token"
        )
    )

    assert not response.is_successful
    assert response.access_token is None
    assert response.refresh_token is None
    assert response.expiration_time is None
    user_repository.get_user_by_username.assert_called_once_with("testuser")
    refresh_token_repository.get_active_token.assert_not_called()


@pytest.mark.asyncio
async def test_when_no_active_token_should_return_unsuccessful():
    user_repository = AsyncMock()
    refresh_token_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()

    user_repository.get_user_by_username = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    refresh_token_repository.get_active_token = AsyncMock(return_value=None)

    handler = RefreshTokenHandler(
        user_repository, refresh_token_repository, password_hasher, token_generator
    )
    response = await handler.handle(
        RefreshTokenRequest(
            user_id="user_id", user_name="testuser", refresh_token="some-token"
        )
    )

    assert not response.is_successful
    assert response.access_token is None
    assert response.refresh_token is None
    assert response.expiration_time is None
    refresh_token_repository.get_active_token.assert_called_once_with("user_id")


@pytest.mark.asyncio
async def test_when_token_is_revoked_should_raise_http_exception():
    user_repository = AsyncMock()
    refresh_token_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()

    user_repository.get_user_by_username = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    refresh_token_repository.get_active_token = AsyncMock(
        return_value=RefreshTokenData(
            user_id="user_id",
            token_hashed="hashed_token",
            expiration_time=9999999999,
            status="revoked",
        )
    )

    handler = RefreshTokenHandler(
        user_repository, refresh_token_repository, password_hasher, token_generator
    )

    with pytest.raises(HTTPException, match="Refresh token revoked"):
        await handler.handle(
            RefreshTokenRequest(
                user_id="user_id", user_name="testuser", refresh_token="some-token"
            )
        )


@pytest.mark.asyncio
async def test_when_token_is_expired_should_revoke_and_return_unsuccessful():
    user_repository = AsyncMock()
    refresh_token_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()

    user_repository.get_user_by_username = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    refresh_token_repository.get_active_token = AsyncMock(
        return_value=RefreshTokenData(
            user_id="user_id",
            token_hashed="hashed_token",
            expiration_time=1000.0,
            status="active",
        )
    )

    handler = RefreshTokenHandler(
        user_repository, refresh_token_repository, password_hasher, token_generator
    )

    with patch(
        "src.features.user_management.refresh_token.refresh_token_handler.time.time",
        return_value=2000.0,
    ):
        response = await handler.handle(
            RefreshTokenRequest(
                user_id="user_id", user_name="testuser", refresh_token="some-token"
            )
        )

    assert not response.is_successful
    assert response.access_token is None
    assert response.refresh_token is None
    assert response.expiration_time is None
    refresh_token_repository.revoke_tokens_by_user_id.assert_called_once_with("user_id")
    password_hasher.verify_password.assert_not_called()
    token_generator.generate_token.assert_not_called()


@pytest.mark.asyncio
async def test_when_token_is_invalid_should_return_unsuccessful():
    user_repository = AsyncMock()
    refresh_token_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()

    user_repository.get_user_by_username = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    refresh_token_repository.get_active_token = AsyncMock(
        return_value=RefreshTokenData(
            user_id="user_id",
            token_hashed="hashed_token",
            expiration_time=9999999999,
            status="active",
        )
    )
    password_hasher.verify_password = Mock(return_value=False)

    handler = RefreshTokenHandler(
        user_repository, refresh_token_repository, password_hasher, token_generator
    )

    with patch(
        "src.features.user_management.refresh_token.refresh_token_handler.time.time",
        return_value=100.0,
    ):
        response = await handler.handle(
            RefreshTokenRequest(
                user_id="user_id", user_name="testuser", refresh_token="wrong-token"
            )
        )

    assert not response.is_successful
    assert response.access_token is None
    assert response.refresh_token is None
    assert response.expiration_time is None
    password_hasher.verify_password.assert_called_once_with(
        "wrong-token", "hashed_token"
    )
    refresh_token_repository.revoke_tokens_by_user_id.assert_not_called()
    token_generator.generate_token.assert_not_called()


@pytest.mark.asyncio
async def test_when_everything_is_valid_should_return_new_tokens():
    user_repository = AsyncMock()
    refresh_token_repository = AsyncMock()
    password_hasher = Mock()
    token_generator = Mock()

    user_repository.get_user_by_username = AsyncMock(
        return_value=CompleteUserResponse(
            id="user_id",
            username="testuser",
            email="test@example.com",
            password_hashed="hashed_password",
            status=UserStatus.ACTIVE,
            role=UserRole.STUDENT,
        )
    )
    refresh_token_repository.get_active_token = AsyncMock(
        return_value=RefreshTokenData(
            user_id="user_id",
            token_hashed="hashed_token",
            expiration_time=9999999999,
            status="active",
        )
    )
    password_hasher.verify_password = Mock(return_value=True)
    password_hasher.hash_password = Mock(return_value="new_hashed_token")
    token_generator.generate_token = Mock(
        return_value=TokenResponse(token="new_jwt_token", expiration_time=3600)
    )
    token_generator.generate_random_token = Mock(
        return_value=TokenResponse(token="new_refresh_raw", expiration_time=604800)
    )
    refresh_token_repository.revoke_tokens_by_user_id = AsyncMock()
    refresh_token_repository.save_token = AsyncMock()

    handler = RefreshTokenHandler(
        user_repository, refresh_token_repository, password_hasher, token_generator
    )

    with patch(
        "src.features.user_management.refresh_token.refresh_token_handler.time.time",
        return_value=100.0,
    ):
        response = await handler.handle(
            RefreshTokenRequest(
                user_id="user_id", user_name="testuser", refresh_token="valid-token"
            )
        )

    assert response.is_successful
    assert response.access_token == "new_jwt_token"
    assert response.refresh_token == "new_refresh_raw"
    assert response.expiration_time == 3600

    refresh_token_repository.revoke_tokens_by_user_id.assert_called_once_with("user_id")
    token_generator.generate_token.assert_called_once()
    token_generator.generate_random_token.assert_called_once()
    password_hasher.hash_password.assert_called_once_with("new_refresh_raw")
    refresh_token_repository.save_token.assert_called_once()

    saved_token_info = refresh_token_repository.save_token.call_args[0][0]
    assert isinstance(saved_token_info, RefreshTokenInfo)
    assert saved_token_info.user_id == "user_id"
    assert saved_token_info.token == "new_hashed_token"
    assert saved_token_info.expiration_time == 604800
    assert saved_token_info.status == "active"
