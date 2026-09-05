
from fastapi import Depends, HTTPException, status

from app.models.enums import UserRole
from app.models.user import User

ADMIN_ONLY = (UserRole.ADMIN,)
ADMIN_OR_ACCOUNTANT = (UserRole.ADMIN, UserRole.ACCOUNTANT)
ANY_AUTHENTICATED = (UserRole.ADMIN, UserRole.ACCOUNTANT, UserRole.CONTACT)


def require_role(*allowed_roles: UserRole):
    from app.api.deps import get_current_user

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return dependency
