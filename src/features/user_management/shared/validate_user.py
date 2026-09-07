from fastapi import HTTPException

from src.features.user_management.shared.token_generator import TokenData


class UserIdentityValidator:

    ADMIN_ROLE = "admin"

    @staticmethod
    def is_valid_user(
        user_logged: TokenData,
        user_id_to_validate: str,
        blank_list_roles: list[str] | None = None,
    ):
        """Validates if the logged-in user is the same as the user being validated.

        Args:
            user_logged (TokenData): The logged-in user's token data.
            user_id_to_validate (str): The ID of the user to validate.
            blank_list_roles (list[str] | None): Optional list of roles that are allowed to bypass the validation.

        Raises:
            HTTPException: If the logged-in user is not the same as the user being validated or not an admin
            The exception detail will indicate "User not found" as the reason.
        """
        if blank_list_roles is None:
            blank_list_roles = [UserIdentityValidator.ADMIN_ROLE]

        if (
            user_logged.user_id != user_id_to_validate
            and user_logged.role not in blank_list_roles
        ):
            raise HTTPException(status_code=404, detail="User not found")
