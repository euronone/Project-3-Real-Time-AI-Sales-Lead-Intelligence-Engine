"""Role-based access control (RBAC) utilities."""

from enum import Enum

from fastapi import Depends, HTTPException, status

from app.models.user import UserRole


class Permission(str, Enum):
    """Fine-grained permissions for the application."""

    MANAGE_TENANTS = "manage_tenants"
    MANAGE_USERS = "manage_users"
    MANAGE_AGENTS = "manage_agents"
    MANAGE_LEADS = "manage_leads"
    MANAGE_CAMPAIGNS = "manage_campaigns"
    MANAGE_LEAD_FLOWS = "manage_lead_flows"
    MANAGE_CALL_ROUTING = "manage_call_routing"
    MANAGE_WEBHOOKS = "manage_webhooks"
    VIEW_ANALYTICS = "view_analytics"
    VIEW_AUDIT_LOG = "view_audit_log"
    MAKE_CALLS = "make_calls"
    VIEW_OWN_LEADS = "view_own_leads"
    VIEW_OWN_CALLS = "view_own_calls"
    VIEW_PREDICTIONS = "view_predictions"


ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.SUPER_ADMIN: set(Permission),
    UserRole.TENANT_ADMIN: {
        Permission.MANAGE_USERS,
        Permission.MANAGE_AGENTS,
        Permission.MANAGE_LEADS,
        Permission.MANAGE_CAMPAIGNS,
        Permission.MANAGE_LEAD_FLOWS,
        Permission.MANAGE_CALL_ROUTING,
        Permission.MANAGE_WEBHOOKS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_AUDIT_LOG,
        Permission.MAKE_CALLS,
        Permission.VIEW_PREDICTIONS,
    },
    UserRole.MANAGER: {
        Permission.MANAGE_AGENTS,
        Permission.MANAGE_LEADS,
        Permission.MANAGE_CAMPAIGNS,
        Permission.VIEW_ANALYTICS,
        Permission.MAKE_CALLS,
        Permission.VIEW_PREDICTIONS,
    },
    UserRole.AGENT: {
        Permission.MAKE_CALLS,
        Permission.VIEW_OWN_LEADS,
        Permission.VIEW_OWN_CALLS,
        Permission.VIEW_PREDICTIONS,
    },
}


class RoleChecker:
    """Dependency that checks if the current user has the required role(s)."""

    def __init__(self, allowed_roles: list[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user=Depends()) -> None:
        """Check if the current user's role is in the allowed roles list."""
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )


def require_role(*roles: UserRole):
    """Create a dependency that requires one of the specified roles."""

    async def _check_role(current_user=Depends()) -> None:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    return _check_role
