"""Pagination utility helpers."""

import math
from typing import Any, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


async def paginate(
    db: AsyncSession,
    query: Select,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """Apply pagination to a SQLAlchemy query and return results with metadata.

    Args:
        db: The async database session.
        query: The SQLAlchemy select query to paginate.
        page: Page number (1-indexed).
        page_size: Number of items per page.

    Returns:
        Dict with 'items', 'total', 'page', 'page_size', 'total_pages'.
    """
    # Count total matching rows
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply offset and limit
    offset = (page - 1) * page_size
    paginated_query = query.offset(offset).limit(page_size)
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }
