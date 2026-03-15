"""Authentication service: register, login, refresh, password reset."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.common import MessageResponse


class AuthService:
    """Handles authentication logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register(self, payload: RegisterRequest) -> TokenResponse:
        """Register a new tenant and admin user."""
        # Check if slug already exists
        result = await self.db.execute(
            select(Tenant).where(Tenant.slug == payload.organization_slug)
        )
        if result.scalar_one_or_none():
            raise ConflictError("Organization slug already taken")

        # Check if email already exists
        result = await self.db.execute(select(User).where(User.email == payload.email))
        if result.scalar_one_or_none():
            raise ConflictError("Email already registered")

        # Create tenant
        tenant = Tenant(
            name=payload.organization_name,
            slug=payload.organization_slug,
        )
        self.db.add(tenant)
        await self.db.flush()

        # Create admin user
        user = User(
            tenant_id=tenant.id,
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            role=UserRole.TENANT_ADMIN,
        )
        self.db.add(user)
        await self.db.flush()

        # Generate tokens
        token_data = {"sub": str(user.id), "tenant_id": str(tenant.id), "role": user.role.value}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

    async def login(self, payload: LoginRequest) -> TokenResponse:
        """Authenticate user and return JWT token pair."""
        result = await self.db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await self.db.flush()

        token_data = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "role": user.role.value,
        }
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

    async def refresh(self, payload: RefreshTokenRequest) -> TokenResponse:
        """Refresh an access token using a valid refresh token."""
        try:
            token_payload = decode_token(payload.refresh_token)
        except Exception:
            raise UnauthorizedError("Invalid refresh token")

        if token_payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        user_id = token_payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        token_data = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "role": user.role.value,
        }
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )

    async def forgot_password(self, payload: ForgotPasswordRequest) -> MessageResponse:
        """Send a password reset email (stub — always returns success for security)."""
        # In production, look up user and send email with reset token
        return MessageResponse(
            message="If an account with that email exists, a reset link has been sent."
        )

    async def reset_password(self, payload: ResetPasswordRequest) -> MessageResponse:
        """Reset password using a valid reset token."""
        try:
            token_payload = decode_token(payload.token)
        except Exception:
            raise UnauthorizedError("Invalid or expired reset token")

        user_id = token_payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundError("User")

        user.password_hash = hash_password(payload.new_password)
        await self.db.flush()

        return MessageResponse(message="Password has been reset successfully")
