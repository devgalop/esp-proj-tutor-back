from abc import ABC, abstractmethod


class InvalidTokenError(Exception):
    """Raised when a token is invalid or cannot be validated."""

    pass


class TokenRequest:
    """Data class for token generation request.
    Args:
        user_id (str): The ID of the user for which the token is being generated.
        user_name (str): The username for which the token is being generated.
        role (str): The role of the user (e.g., "student", "teacher").
    """

    def __init__(self, user_id: str, user_name: str, role: str):
        self.user_id = user_id
        self.user_name = user_name
        self.role = role


class TokenResponse:
    """Data class for token generation response.
    Args:
        token (str): The generated token.
        expiration_time (float): The time in seconds until the token expires. unix timestamp format.
    """

    def __init__(self, token: str, expiration_time: float):
        self.token = token
        self.expiration_time = expiration_time


class TokenData:
    """Data class for token data extracted from the token.
    Args:
        user_id (str): The ID of the user extracted from the token.
        user_name (str): The username extracted from the token.
        role (str): The role of the user extracted from the token.
    """

    def __init__(self, user_id: str, user_name: str, role: str):
        self.user_id = user_id
        self.user_name = user_name
        self.role = role


class TokenGenerator(ABC):
    """Interface for token generation and validation.

    Args:
        ABC (_type_): Abstract base class for token generation
    """

    @abstractmethod
    def generate_token(self, request: TokenRequest) -> TokenResponse:
        """Generate a token based on the provided request.

        Args:
            request (TokenRequest): The token generation request containing user information and expiration time.

        Returns:
            TokenResponse: The generated token and its expiration time.
        """
        pass

    @abstractmethod
    def validate_token(self, token: str, verify_exp: bool = True) -> TokenData:
        """Validate the provided token and extract user information.

        Args:
            token (str): The token to be validated.
            verify_exp (bool): Whether to verify the token's expiration. Defaults to True.
        Returns:
            TokenData: The user information extracted from the token if it is valid.
        Raises:
            Exception: If the token is invalid or expired.
        """
        pass

    @abstractmethod
    def generate_random_token(self) -> TokenResponse:
        """Generate a random token string.

        Returns:
            TokenResponse: A randomly generated token string and its expiration time.
        """
        pass
