"""SQLAlchemy models package — import all models to register with Base.metadata."""

from app.models.base import Base, TenantMixin, TimestampMixin
from app.models.tenant import Tenant, TenantPlan
from app.models.user import User, UserRole
from app.models.lead import Lead, LeadStatus, LeadPriority
from app.models.lead_flow import LeadFlow
from app.models.campaign import Campaign, CampaignStatus
from app.models.call import Call, CallDirection, CallStatus
from app.models.call_transcript import CallTranscript, Speaker
from app.models.call_analysis import CallAnalysis
from app.models.deal_prediction import DealPrediction, PredictionConfidence
from app.models.notification import Notification
from app.models.webhook import Webhook
from app.models.audit_log import AuditLog

__all__ = [
    "Base",
    "TenantMixin",
    "TimestampMixin",
    "Tenant",
    "TenantPlan",
    "User",
    "UserRole",
    "Lead",
    "LeadStatus",
    "LeadPriority",
    "LeadFlow",
    "Campaign",
    "CampaignStatus",
    "Call",
    "CallDirection",
    "CallStatus",
    "CallTranscript",
    "Speaker",
    "CallAnalysis",
    "DealPrediction",
    "PredictionConfidence",
    "Notification",
    "Webhook",
    "AuditLog",
]
