import pytest

from src.features.user_management.confirm_otp.confirm_otp_request import (
    ConfirmOTPRequest,
)


def test_when_request_is_valid_should_not_raise_exception():
    request = ConfirmOTPRequest(user_id="user_id", otp="ABC123")
    assert request.user_id == "user_id"
    assert request.otp == "ABC123"


def test_when_otp_is_lowercase_should_be_uppercased():
    request = ConfirmOTPRequest(user_id="user_id", otp="abc123")
    assert request.otp == "ABC123"


def test_when_user_id_is_empty_should_raise_exception():
    with pytest.raises(ValueError):
        ConfirmOTPRequest(user_id="", otp="ABC123")


def test_when_user_id_is_too_short_should_raise_exception():
    with pytest.raises(ValueError):
        ConfirmOTPRequest(user_id="ab", otp="ABC123")


def test_when_user_id_is_too_long_should_raise_exception():
    with pytest.raises(ValueError):
        ConfirmOTPRequest(user_id="a" * 101, otp="ABC123")


def test_when_otp_is_empty_should_raise_exception():
    with pytest.raises(ValueError):
        ConfirmOTPRequest(user_id="user_id", otp="")


def test_when_otp_is_too_short_should_raise_exception():
    with pytest.raises(ValueError):
        ConfirmOTPRequest(user_id="user_id", otp="ABC")


def test_when_otp_is_too_long_should_raise_exception():
    with pytest.raises(ValueError):
        ConfirmOTPRequest(user_id="user_id", otp="ABC1234")


def test_when_user_id_is_at_minimum_length_should_be_valid():
    request = ConfirmOTPRequest(user_id="abc", otp="ABC123")
    assert request.user_id == "abc"


def test_when_user_id_is_at_maximum_length_should_be_valid():
    request = ConfirmOTPRequest(user_id="a" * 100, otp="ABC123")
    assert request.user_id == "a" * 100
