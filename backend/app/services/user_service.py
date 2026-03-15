"""User service with CRUD operations."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.common import MessageResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate


class UserService:
    """Handles user CRUD operations within a tenant."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_users(self, tenant_id: uuid.UUID) -> list[UserResponse]:
        """List all users in a tenant."""
        result = await self.db.execute(
            select(User).where(User.tenant_id == tenant_id).order_by(User.created_at.desc())
        )
        users = result.scalars().all()
        return [UserResponse.model_validate(u) for u in users]

    async def list_agents(self, tenant_id: uuid.UUID) -> list[UserResponse]:
        """List all agents in a tenant."""
        result = await self.db.execute(
            select(User).where(
                User.tenant_id == tenant_id,
                User.role == UserRole.AGENT,
                User.is_active == True,  # noqa: E712
            )
        )
        agents = result.scalars().all()
        return [UserResponse.model_validate(a) for a in agents]

    async def create_user(self, payload: UserCreate, tenant_id: uuid.UUID) -> UserResponse:
        """Create a new user within a tenant."""
        # Check for duplicate email within tenant
        result = await self.db.execute(
            select(User).where(User.tenant_id == tenant_id, User.email == payload.email)
        )
        if result.scalar_one_or_none():
            raise ConflictError("Email already registered in this organization")

        user = User(
            tenant_id=tenant_id,
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            role=payload.role,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return UserResponse.model_validate(user)

    async def get_user(self, user_id: uuid.UUID, tenant_id: uuid.UUID) -> UserResponse:
        """Get user by ID within a tenant."""
        user = await self._get_user_or_404(user_id, tenant_id)
        return UserResponse.model_validate(user)

    async def update_user(
        self, user_id: uuid.UUID, payload: UserUpdate, tenant_id: uuid.UUID
    ) -> UserResponse:
        """Update a user within a tenant."""
        user = await self._get_user_or_404(user_id, tenant_id)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: uuid.UUID, tenant_id: uuid.UUID) -> MessageResponse:
        """Deactivate a user."""
        user = await self._get_user_or_404(user_id, tenant_id)
        user.is_active = False
        await self.db.flush()
        return MessageResponse(message="User deactivated")

    async def get_agent_scorecard(self, agent_id: uuid.UUID, tenant_id: uuid.UUID) -> dict:
        """Get performance scorecard for an agent."""
        agent = await self._get_user_or_404(agent_id, tenant_id)
        return {
            "agent_id": str(agent.id),
            "full_name": agent.full_name,
            "total_calls": 0,
            "avg_call_duration": 0,
            "avg_agent_score": 0.0,
            "conversion_rate": 0.0,
            "total_deals_won": 0,
            "total_pipeline_value": 0.0,
            "avg_talk_ratio": 0.0,
            "avg_filler_words": 0,
        }

    async def _get_user_or_404(self, user_id: uuid.UUID, tenant_id: uuid.UUID) -> User:
        """Fetch a user within a tenant or raise NotFoundError."""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.tenant_id == tenant_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User", str(user_id))
        return user
