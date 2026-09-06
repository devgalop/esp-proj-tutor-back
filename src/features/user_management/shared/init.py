from fastapi import APIRouter

from src.features.user_management.create_user.create_user_endpoint import (
    router as create_user_router,
)
from src.features.user_management.login.login_endpoint import router as login_router
from src.features.user_management.get_user.get_user_endpoint import (
    router as get_user_router,
)
from src.features.user_management.recovery_password.recovery_password_endpoint import (
    router as recovery_password_router,
)
from src.features.user_management.change_password.change_password_endpoint import (
    router as change_password_router,
)
from src.features.user_management.assign_role.assign_role_endpoint import (
    router as assign_role_router,
)
from src.features.user_management.get_available_roles.get_available_roles_endpoint import (
    router as get_available_roles_router,
)
from src.features.user_management.refresh_token.refresh_token_endpoint import (
    router as refresh_token_router,
)
from src.features.user_management.create_user_from_admin.create_user_from_admin_endpoint import (
    router as create_user_from_admin_router,
)
from src.features.user_management.update_user_status.update_user_status_endpoint import (
    router as update_user_status_router,
)
from src.features.user_management.get_connected_users.get_connected_users_endpoint import (
    router as get_connected_users_router,
)
from src.features.user_management.update_user_profile.update_user_profile_endpoint import (
    router as update_user_profile_router,
)
from src.features.user_management.confirm_otp.confirm_otp_endpoint import (
    router as confirm_otp_router,
)

router = APIRouter()
router.include_router(create_user_router)
router.include_router(login_router)
router.include_router(get_available_roles_router)
router.include_router(get_user_router)
router.include_router(recovery_password_router)
router.include_router(change_password_router)
router.include_router(assign_role_router)
router.include_router(refresh_token_router)
router.include_router(create_user_from_admin_router)
router.include_router(update_user_status_router)
router.include_router(get_connected_users_router)
router.include_router(update_user_profile_router)
router.include_router(confirm_otp_router)
