"""Pytest fixtures for async testing."""

import asyncio
import uuid
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import create_access_token, hash_password
from app.dependencies import get_db
from app.main import app as socketio_app
from app.models.base import Base
from app.models.tenant import Tenant
from app.models.user import User, UserRole

# Use an in-memory SQLite or test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

# Socket.IO wraps FastAPI; dependency overrides must target the inner app.
fastapi_app = socketio_app.other_asgi_app


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create tables before each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session."""
    async with test_session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client."""

    async def _override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test",
    ) as ac:
        yield ac

    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_tenant(db_session: AsyncSession) -> Tenant:
    """Create a test tenant."""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test Organization",
        slug="test-org",
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a test admin user."""
    user = User(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        email="admin@test.com",
        password_hash=hash_password("testpassword123"),
        full_name="Test Admin",
        role=UserRole.TENANT_ADMIN,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def _access_token_for_user(user: User, tenant_id: uuid.UUID) -> str:
    """Build an access token matching AuthService payload shape."""
    return create_access_token(
        {
            "sub": str(user.id),
            "tenant_id": str(tenant_id),
            "role": user.role.value,
            "full_name": user.full_name,
        }
    )


@pytest_asyncio.fixture
def auth_headers(test_user: User, test_tenant: Tenant) -> dict[str, str]:
    """Generate authentication headers for the test tenant admin user."""
    return {"Authorization": f"Bearer {_access_token_for_user(test_user, test_tenant.id)}"}


@pytest_asyncio.fixture
async def test_agent_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a test user with AGENT role."""
    user = User(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        email="agent@test.com",
        password_hash=hash_password("agentpass123"),
        full_name="Test Agent",
        role=UserRole.AGENT,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_manager_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a test user with MANAGER role."""
    user = User(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        email="manager@test.com",
        password_hash=hash_password("managerpass123"),
        full_name="Test Manager",
        role=UserRole.MANAGER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_super_admin(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a super admin user (same tenant for FK; super admin can see all tenants)."""
    user = User(
        id=uuid.uuid4(),
        tenant_id=test_tenant.id,
        email="super@test.com",
        password_hash=hash_password("superpass123"),
        full_name="Super Admin",
        role=UserRole.SUPER_ADMIN,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
def agent_auth_headers(test_agent_user: User, test_tenant: Tenant) -> dict[str, str]:
    return {"Authorization": f"Bearer {_access_token_for_user(test_agent_user, test_tenant.id)}"}


@pytest_asyncio.fixture
def manager_auth_headers(test_manager_user: User, test_tenant: Tenant) -> dict[str, str]:
    return {"Authorization": f"Bearer {_access_token_for_user(test_manager_user, test_tenant.id)}"}


@pytest_asyncio.fixture
def super_admin_auth_headers(test_super_admin: User, test_tenant: Tenant) -> dict[str, str]:
    return {"Authorization": f"Bearer {_access_token_for_user(test_super_admin, test_tenant.id)}"}
