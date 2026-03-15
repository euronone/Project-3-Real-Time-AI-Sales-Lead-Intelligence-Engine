"""Top-level API router aggregating all versioned routes."""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    tenants,
    users,
    agents,
    leads,
    lead_flows,
    campaigns,
    calls,
    call_routing,
    analytics,
    predictions,
    notifications,
    webhooks,
    twilio_webhooks,
)

api_router = APIRouter()

# V1 routes
api_router.include_router(auth.router, prefix="/v1/auth", tags=["Authentication"])
api_router.include_router(tenants.router, prefix="/v1/tenants", tags=["Tenants"])
api_router.include_router(users.router, prefix="/v1/users", tags=["Users"])
api_router.include_router(agents.router, prefix="/v1/agents", tags=["Agents"])
api_router.include_router(leads.router, prefix="/v1/leads", tags=["Leads"])
api_router.include_router(lead_flows.router, prefix="/v1/lead-flows", tags=["Lead Flows"])
api_router.include_router(campaigns.router, prefix="/v1/campaigns", tags=["Campaigns"])
api_router.include_router(calls.router, prefix="/v1/calls", tags=["Calls"])
api_router.include_router(call_routing.router, prefix="/v1/call-routing", tags=["Call Routing"])
api_router.include_router(analytics.router, prefix="/v1/analytics", tags=["Analytics"])
api_router.include_router(predictions.router, prefix="/v1/predictions", tags=["Predictions"])
api_router.include_router(
    notifications.router, prefix="/v1/notifications", tags=["Notifications"]
)
api_router.include_router(webhooks.router, prefix="/v1/webhooks", tags=["Webhooks"])
api_router.include_router(
    twilio_webhooks.router, prefix="/v1/twilio", tags=["Twilio Webhooks"]
)
