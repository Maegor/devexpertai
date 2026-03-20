import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from models import PartnerStatus


class PartnerCreate(BaseModel):
    name: str
    email: EmailStr
    fp_promoter_id: str | None = None
    parent_partner_id: uuid.UUID | None = None
    company_name: str | None = None
    website: str | None = None
    country: str | None = None
    collaboration_reason: str | None = None
    assigned_sales_rep_id: uuid.UUID | None = None
    language_preference: str = "en"
    referral_enabled: bool = False
    deals_enabled: bool = False
    status: PartnerStatus = PartnerStatus.PendingReview
    tc_version_accepted: str | None = None
    tc_acceptance_date: datetime | None = None
    tc_acceptance_ip: str | None = None
    tc_accepted_by: str | None = None
    qb_account_referral: str | None = None
    qb_account_fixed: str | None = None
    self_billing_enabled: bool = False


class PartnerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    fp_promoter_id: str | None = None
    parent_partner_id: uuid.UUID | None = None
    company_name: str | None = None
    website: str | None = None
    country: str | None = None
    collaboration_reason: str | None = None
    assigned_sales_rep_id: uuid.UUID | None = None
    language_preference: str | None = None
    referral_enabled: bool | None = None
    deals_enabled: bool | None = None
    status: PartnerStatus | None = None
    tc_version_accepted: str | None = None
    tc_acceptance_date: datetime | None = None
    tc_acceptance_ip: str | None = None
    tc_accepted_by: str | None = None
    qb_account_referral: str | None = None
    qb_account_fixed: str | None = None
    self_billing_enabled: bool | None = None


class PartnerResponse(BaseModel):
    id: uuid.UUID
    fp_promoter_id: str | None
    parent_partner_id: uuid.UUID | None
    name: str
    email: str
    company_name: str | None
    website: str | None
    country: str | None
    collaboration_reason: str | None
    assigned_sales_rep_id: uuid.UUID | None
    language_preference: str
    referral_enabled: bool
    deals_enabled: bool
    status: PartnerStatus
    tc_version_accepted: str | None
    tc_acceptance_date: datetime | None
    tc_acceptance_ip: str | None
    tc_accepted_by: str | None
    qb_account_referral: str | None
    qb_account_fixed: str | None
    self_billing_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
