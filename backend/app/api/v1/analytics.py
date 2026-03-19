"""Analytics endpoints: dashboard, funnel, leaderboard, trends, prediction accuracy."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get dashboard KPIs for the current tenant."""
    return {
        "total_calls": 0,
        "conversion_rate": 0.0,
        "active_agents": 0,
        "pipeline_value": 0.0,
        "avg_deal_score": 0.0,
        "calls_today": 0,
    }


@router.get("/conversion-funnel")
async def get_conversion_funnel(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get conversion funnel metrics."""
    return {
        "stages": [
            {"name": "new", "count": 0},
            {"name": "contacted", "count": 0},
            {"name": "qualified", "count": 0},
            {"name": "proposal", "count": 0},
            {"name": "negotiation", "count": 0},
            {"name": "won", "count": 0},
            {"name": "lost", "count": 0},
        ]
    }


@router.get("/agent-leaderboard")
async def get_agent_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """Get agent ranking by performance."""
    return []


@router.get("/call-trends")
async def get_call_trends(
    period: str = Query(default="7d", pattern=r"^(7d|30d|90d)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get call volume and duration trends."""
    return {
        "period": period,
        "data_points": [],
    }


@router.get("/prediction-accuracy")
async def get_prediction_accuracy(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get AI prediction accuracy over time."""
    return {
        "overall_accuracy": 0.0,
        "data_points": [],
    }
