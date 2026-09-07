import pytest

from src.features.user_management.refresh_token.refresh_token_request import (
    RefreshTokenRequest,
)


def test_when_request_is_valid_should_not_raise_exception():
    request = RefreshTokenRequest(
        user_id="user_id", user_name="testuser", refresh_token="valid-token-123"
    )
    assert request.user_name == "testuser"
    assert request.refresh_token == "valid-token-123"


def test_when_user_name_is_empty_should_raise_exception():
    with pytest.raises(ValueError, match="Username is required"):
        RefreshTokenRequest(
            user_id="user_id", user_name="", refresh_token="valid-token-123"
        )


def test_when_user_name_is_too_short_should_raise_exception():
    with pytest.raises(ValueError, match="Username must be at least 3 characters long"):
        RefreshTokenRequest(
            user_id="user_id", user_name="ab", refresh_token="valid-token-123"
        )


def test_when_user_name_is_too_long_should_raise_exception():
    with pytest.raises(
        ValueError, match="Username must be no more than 20 characters long"
    ):
        RefreshTokenRequest(
            user_id="user_id", user_name="a" * 21, refresh_token="valid-token-123"
        )


def test_when_user_name_has_invalid_characters_should_raise_exception():
    with pytest.raises(
        ValueError,
        match="Username must be alphanumeric and can include underscores",
    ):
        RefreshTokenRequest(
            user_id="user_id", user_name="user name!", refresh_token="valid-token-123"
        )


def test_when_refresh_token_is_empty_should_raise_exception():
    with pytest.raises(ValueError, match="Refresh token cannot be empty"):
        RefreshTokenRequest(user_id="user_id", user_name="testuser", refresh_token="")


def test_when_refresh_token_is_too_short_should_raise_exception():
    with pytest.raises(ValueError, match="Refresh token is too short"):
        RefreshTokenRequest(
            user_id="user_id", user_name="testuser", refresh_token="abc"
        )


def test_when_refresh_token_is_too_long_should_raise_exception():
    with pytest.raises(ValueError, match="Refresh token is too long"):
        RefreshTokenRequest(
            user_id="user_id", user_name="testuser", refresh_token="a" * 151
        )
