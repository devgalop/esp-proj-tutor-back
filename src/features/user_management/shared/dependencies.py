from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi.params import Depends

from src.features.user_management.assign_role.assign_role_handler import (
    AssignRoleHandler,
)
from src.features.user_management.change_password.change_password_handler import (
    ChangePasswordHandler,
)
from src.features.user_management.confirm_otp.confirm_otp_handler import (
    ConfirmOTPHandler,
)
from src.features.user_management.create_user.create_user_handler import (
    CreateUserHandler,
)

from src.features.user_management.get_available_roles.get_available_roles_handler import (
    GetAvailableRolesHandler,
)
from src.features.user_management.get_connected_users.get_connected_users_handler import (
    GetConnectedUsersHandler,
)
from src.features.user_management.get_user.get_user_handler import GetUserHandler
from src.features.user_management.login.login_handler import LoginHandler
from src.features.user_management.recovery_password.recovery_password_handler import (
    RecoveryPasswordHandler,
)
from src.features.user_management.shared.otp_generator import OTPGenerator
from src.features.user_management.shared.password_hasher import PasswordHasher
from itmentorsoft_persistence.repositories import (
    RoleRepository,
    UserRecoveryTokenRepository,
    UserRepository,
    RefreshTokenRepository,
)
from src.features.user_management.shared.token_generator import TokenGenerator
from src.features.user_management.shared.user_manager_service import UserManagerService
from src.features.user_management.refresh_token.refresh_token_handler import (
    RefreshTokenHandler,
)

from src.features.user_management.update_user_profile.update_user_profile_handler import (
    UpdateUserProfileHandler,
)
from src.features.user_management.update_user_status.update_user_status_handler import (
    UpdateUserStatusHandler,
)
from itmentorsoft_persistence.mappers import (
    PostgresRoleMapper,
    PostgresUserMapper,
    PostgresRecoveryTokenMapper,
    PostgresRefreshTokenMapper,
)

from itmentorsoft_persistence import (
    get_db,
)
from src.infrastructure.database.postgresql.repository.postgres_role_repository import (
    PostgresRoleRepository,
)
from src.infrastructure.database.postgresql.repository.postgres_user_recovery_token_repository import (
    PostgresUserRecoveryTokenRepository,
)
from src.infrastructure.database.postgresql.repository.postgres_user_refresh_token_repository import (
    PostgresUserRefreshTokenRepository,
)
from src.infrastructure.database.postgresql.repository.postgres_user_repository import (
    PostgresUserRepository,
)
from src.infrastructure.notification.brevo_notification_service import (
    BrevoNotificationService,
)
from src.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.security.jwt_token_generator import JWTTokenGenerator
from src.features.shared.notification_service import NotificationService
from src.features.shared.template_loader import TemplateLoader
from src.features.user_management.create_user_from_admin.create_user_from_admin_handler import (
    CreateUserFromAdminHandler,
)
from src.infrastructure.security.simple_otp_generator import SimpleOTPGenerator


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    return PostgresUserRepository(
        session_factory=session, user_mapper=PostgresUserMapper
    )


def get_role_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> RoleRepository:
    return PostgresRoleRepository(
        session_factory=session, role_mapper=PostgresRoleMapper
    )


def get_user_recovery_token_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserRecoveryTokenRepository:
    return PostgresUserRecoveryTokenRepository(
        session_factory=session, mapper=PostgresRecoveryTokenMapper
    )


def get_password_hasher() -> PasswordHasher:
    return BcryptPasswordHasher()


def get_token_generator() -> TokenGenerator:
    return JWTTokenGenerator()


def get_refresh_token_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> RefreshTokenRepository:
    return PostgresUserRefreshTokenRepository(
        session_factory=session, mapper=PostgresRefreshTokenMapper
    )


def get_create_user_handler(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    role_repository: Annotated[RoleRepository, Depends(get_role_repository)],
) -> CreateUserHandler:
    return CreateUserHandler(user_repository, password_hasher, role_repository)


def get_otp_generator() -> OTPGenerator:
    return SimpleOTPGenerator()


def get_confirm_otp_handler(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    token_generator: Annotated[TokenGenerator, Depends(get_token_generator)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    refresh_token_repository: Annotated[
        RefreshTokenRepository, Depends(get_refresh_token_repository)
    ],
) -> ConfirmOTPHandler:
    return ConfirmOTPHandler(
        user_repository, password_hasher, token_generator, refresh_token_repository
    )


def get_notification_service() -> NotificationService:
    return BrevoNotificationService()


def get_template_loader() -> TemplateLoader:
    return TemplateLoader()


def get_login_handler(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    otp_generator: Annotated[OTPGenerator, Depends(get_otp_generator)],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
    template_loader: Annotated[TemplateLoader, Depends(get_template_loader)],
) -> LoginHandler:
    return LoginHandler(
        user_repository,
        password_hasher,
        otp_generator,
        notification_service,
        template_loader,
    )


def get_get_user_handler(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> GetUserHandler:
    return GetUserHandler(user_repository)


def get_recovery_password_handler(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    user_recovery_token_repository: Annotated[
        UserRecoveryTokenRepository, Depends(get_user_recovery_token_repository)
    ],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
    token_generator: Annotated[TokenGenerator, Depends(get_token_generator)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    template_loader: Annotated[TemplateLoader, Depends(get_template_loader)],
) -> RecoveryPasswordHandler:
    return RecoveryPasswordHandler(
        user_repository,
        user_recovery_token_repository,
        notification_service,
        token_generator,
        password_hasher,
        template_loader,
    )


def get_change_password_handler(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    user_recovery_token_repository: Annotated[
        UserRecoveryTokenRepository, Depends(get_user_recovery_token_repository)
    ],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
) -> ChangePasswordHandler:
    return ChangePasswordHandler(
        user_repository, user_recovery_token_repository, password_hasher
    )


def get_assign_role_handler(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    role_repository: Annotated[RoleRepository, Depends(get_role_repository)],
) -> AssignRoleHandler:
    return AssignRoleHandler(user_repository, role_repository)


def get_get_available_roles_handler(
    role_repository: Annotated[RoleRepository, Depends(get_role_repository)],
) -> GetAvailableRolesHandler:
    return GetAvailableRolesHandler(role_repository)


def get_refresh_token_handler(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    refresh_token_repository: Annotated[
        RefreshTokenRepository, Depends(get_refresh_token_repository)
    ],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    token_generator: Annotated[TokenGenerator, Depends(get_token_generator)],
) -> RefreshTokenHandler:
    return RefreshTokenHandler(
        user_repository, refresh_token_repository, password_hasher, token_generator
    )


def get_user_manager_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
    role_repository: Annotated[RoleRepository, Depends(get_role_repository)],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
    template_loader: Annotated[TemplateLoader, Depends(get_template_loader)],
) -> UserManagerService:
    return UserManagerService(
        user_repository,
        password_hasher,
        role_repository,
        notification_service,
        template_loader,
    )


def get_create_user_from_admin_handler(
    user_manager_service: Annotated[
        UserManagerService, Depends(get_user_manager_service)
    ],
) -> CreateUserFromAdminHandler:

    return CreateUserFromAdminHandler(user_manager_service)


def get_update_user_status_handler(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UpdateUserStatusHandler:
    return UpdateUserStatusHandler(user_repository)


def get_get_connected_users_handler(
    refresh_token_repository: Annotated[
        RefreshTokenRepository, Depends(get_refresh_token_repository)
    ],
) -> GetConnectedUsersHandler:
    return GetConnectedUsersHandler(refresh_token_repository)


def get_update_user_profile_handler(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UpdateUserProfileHandler:
    return UpdateUserProfileHandler(user_repository)
