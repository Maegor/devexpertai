import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from models import PartnerDealStatus


class PartnerDealCreate(BaseModel):
    partner_id: uuid.UUID
    description: str
    currency: str
    status: PartnerDealStatus = PartnerDealStatus.Proposal
    start_month: date
    end_month: date
    total_cost: Decimal


class PartnerDealUpdate(BaseModel):
    description: str | None = None
    currency: str | None = None
    status: PartnerDealStatus | None = None
    start_month: date | None = None
    end_month: date | None = None
    total_cost: Decimal | None = None


class PartnerDealResponse(BaseModel):
    id: uuid.UUID
    partner_id: uuid.UUID
    description: str
    currency: str
    status: PartnerDealStatus
    start_month: date
    end_month: date
    total_cost: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
