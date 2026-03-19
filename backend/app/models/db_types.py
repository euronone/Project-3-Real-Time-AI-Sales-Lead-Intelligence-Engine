"""Portable SQLAlchemy column types: PostgreSQL in production, SQLite in tests."""

import uuid

import sqlalchemy as sa
from sqlalchemy import CHAR, TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID


class GUID(TypeDecorator):
    """UUID: native on PostgreSQL; 36-char string on SQLite (aiosqlite cannot bind uuid.UUID)."""

    impl = CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return str(value) if isinstance(value, uuid.UUID) else value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


# JSONB on PostgreSQL; generic JSON on SQLite for pytest + aiosqlite.
JSONDocument = sa.JSON().with_variant(JSONB(), "postgresql")
