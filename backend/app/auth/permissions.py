"""
Role-based access control.

Roles (from app.models.enums.UserRole):
    admin       - Create/Modify/Archive Master Data, record
                  transactions, view all reports. Can create Admin or
                  Accountant users via the admin "Create User" screen.
    accountant  - Create master data, record transactions, view
                  reports. Cannot create other users beyond public
                  sign-up (which only ever creates more accountants).
    contact     - READ-ONLY access to their own invoices/bills, plus
                  the ability to make a payment against them. Cannot
                  create/edit any master data or other business
                  records — the portal is intentionally restricted.

TODO: implement as FastAPI dependencies, e.g.:

    def require_role(*allowed_roles):
        def dependency(current_user = Depends(get_current_user)):
            if current_user.role not in allowed_roles:
                raise HTTPException(status_code=403, detail="Forbidden")
            return current_user
        return dependency
"""
from app.models.enums import UserRole

ADMIN_ONLY = (UserRole.ADMIN,)
ADMIN_OR_ACCOUNTANT = (UserRole.ADMIN, UserRole.ACCOUNTANT)
ANY_AUTHENTICATED = (UserRole.ADMIN, UserRole.ACCOUNTANT, UserRole.CONTACT)


def require_role(*allowed_roles):
    """TODO: implement as a real FastAPI dependency (see docstring above)."""
    raise NotImplementedError
